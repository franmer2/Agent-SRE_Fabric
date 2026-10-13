from __future__ import annotations

import asyncio
import hmac
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any

import httpx
from azure.identity.aio import ClientSecretCredential, ManagedIdentityCredential
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

FABRIC_ROOT = "https://api.fabric.microsoft.com"
FABRIC_SCOPE = f"{FABRIC_ROOT}/.default"
POWER_BI_ROOT = "https://api.powerbi.com"
POWER_BI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
MAX_ATTEMPTS = 6
MAX_PAGES = 1000
SCAN_CACHE_SECONDS = 300
PAGE_DELAY_SECONDS = 2.0

ARTIFACT_COLLECTIONS = {
    "dashboards": "Dashboard",
    "dataflows": "Dataflow",
    "datamarts": "Datamart",
    "datasets": "SemanticModel",
    "eventhouses": "Eventhouse",
    "kqlDatabases": "KQLDatabase",
    "lakehouses": "Lakehouse",
    "mirroredDatabases": "MirroredDatabase",
    "notebooks": "Notebook",
    "pipelines": "DataPipeline",
    "reports": "Report",
    "warehouses": "Warehouse",
}

_scan_cache: tuple[float, list[dict[str, Any]]] | None = None
_scan_lock = asyncio.Lock()
_admin_lock = asyncio.Lock()
_admin_cache: dict[
    tuple[str, tuple[tuple[str, str], ...], str],
    tuple[float, datetime, list[dict[str, Any]]],
] = {}
_cu_cache: dict[int, tuple[float, dict[str, Any]]] = {}
_cu_daily_cache: dict[int, tuple[float, dict[str, Any]]] = {}
_cu_lock = asyncio.Lock()
_admin_refresh_task: asyncio.Task[None] | None = None
logger = logging.getLogger(__name__)


@asynccontextmanager
async def _app_lifespan(_: Any):
    global _admin_refresh_task

    async with mcp.session_manager.run():
        _admin_refresh_task = asyncio.create_task(_maintain_admin_cache())
        try:
            yield
        finally:
            _admin_refresh_task.cancel()
            await asyncio.gather(_admin_refresh_task, return_exceptions=True)
            _admin_refresh_task = None


allowed_host = os.environ.get("MCP_ALLOWED_HOST")
transport_security = (
    TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[allowed_host],
        allowed_origins=[],
    )
    if allowed_host
    else None
)
mcp = FastMCP(
    "Fabric Admin",
    host="0.0.0.0",
    stateless_http=True,
    json_response=True,
    transport_security=transport_security,
)


class FabricAdminError(RuntimeError):
    pass


class ApiKeyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path == "/health":
            await JSONResponse(
                {
                    "status": "ok",
                    "cacheMaintainerRunning": (
                        _admin_refresh_task is not None
                        and not _admin_refresh_task.done()
                    ),
                    "cache": {
                        cache_key[0]: {
                            "collectedAtUtc": collected_at.isoformat(),
                            "count": len(rows),
                        }
                        for cache_key, (_, collected_at, rows) in _admin_cache.items()
                    },
                }
            )(scope, receive, send)
            return

        expected = os.environ.get("MCP_API_KEY")
        if not expected:
            await JSONResponse(
                {"error": "MCP_API_KEY is not configured"},
                status_code=503,
            )(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        supplied = headers.get("x-api-key", "")
        if not hmac.compare_digest(supplied, expected):
            await JSONResponse({"error": "Unauthorized"}, status_code=401)(
                scope,
                receive,
                send,
            )
            return

        await self.app(scope, receive, send)


def _fabric_credential() -> ClientSecretCredential | ManagedIdentityCredential:
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    app_client_id = os.environ.get("FABRIC_ADMIN_CLIENT_ID")
    app_client_secret = os.environ.get("FABRIC_ADMIN_CLIENT_SECRET")
    if tenant_id and app_client_id and app_client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=app_client_id,
            client_secret=app_client_secret,
        )

    client_id = os.environ.get("AZURE_CLIENT_ID")
    return ManagedIdentityCredential(client_id=client_id) if client_id else ManagedIdentityCredential()


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        if retry_after.isdigit():
            return min(float(retry_after), 120.0)
        try:
            parsed = parsedate_to_datetime(retry_after)
            return min(max(parsed.timestamp() - datetime.now(UTC).timestamp(), 0.0), 120.0)
        except (TypeError, ValueError):
            pass
    return min(float(2 ** (attempt - 1)), 60.0)


async def _fabric_get(
    path: str,
    *,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    credential = _fabric_credential()
    try:
        token = await credential.get_token(FABRIC_SCOPE)
    finally:
        await credential.close()

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Accept": "application/json",
        "x-ms-fabric-skill": "fabric-sre-accelerator",
    }
    url = path if path.startswith("https://") else f"{FABRIC_ROOT}{path}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            response = await client.get(url, params=params, headers=headers)
            if response.status_code < 400:
                payload = response.json()
                if not isinstance(payload, dict):
                    raise FabricAdminError("Fabric Admin returned a non-object response.")
                return payload
            if response.status_code not in {408, 429, 500, 502, 503, 504}:
                raise FabricAdminError(
                    f"Fabric Admin GET failed with {response.status_code}: "
                    f"{response.text[:2000]}"
                )
            if attempt == MAX_ATTEMPTS:
                raise FabricAdminError(
                    f"Fabric Admin GET exhausted {MAX_ATTEMPTS} attempts; "
                    f"last status was {response.status_code}."
                )
            await asyncio.sleep(_retry_delay(response, attempt))

    raise AssertionError("Retry loop terminated unexpectedly.")


async def _power_bi_request(
    method: str,
    path: str,
    *,
    params: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
) -> Any:
    credential = _fabric_credential()
    try:
        token = await credential.get_token(POWER_BI_SCOPE)
    finally:
        await credential.close()

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    url = path if path.startswith("https://") else f"{POWER_BI_ROOT}{path}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            response = await client.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
            )
            if response.status_code < 400:
                return response.json()
            if response.status_code not in {408, 429, 500, 502, 503, 504}:
                raise FabricAdminError(
                    f"Power BI Admin {method} failed with {response.status_code}: "
                    f"{response.text[:2000]}"
                )
            if attempt == MAX_ATTEMPTS:
                raise FabricAdminError(
                    f"Power BI Admin {method} exhausted {MAX_ATTEMPTS} attempts; "
                    f"last status was {response.status_code}."
                )
            await asyncio.sleep(_retry_delay(response, attempt))

    raise AssertionError("Retry loop terminated unexpectedly.")


def _dax_value(row: dict[str, Any], column_name: str) -> Any:
    suffix = f"[{column_name}]"
    for key, value in row.items():
        if key == column_name or key.endswith(suffix):
            return value
    return None


def _capacity_metrics_query(period_days: int) -> str:
    offset_days = period_days - 1
    return f"""
DEFINE
  VAR _LastDate =
    CALCULATE(
      MAX('Metrics By Item Operation And Day'[Date]),
      REMOVEFILTERS('Metrics By Item Operation And Day')
    )
  VAR _DateFilter =
    FILTER(
      ALL('Metrics By Item Operation And Day'[Date]),
      'Metrics By Item Operation And Day'[Date] >= _LastDate - {offset_days}
        && 'Metrics By Item Operation And Day'[Date] <= _LastDate
    )
EVALUATE
  SUMMARIZECOLUMNS(
    'Metrics By Item Operation And Day'[Capacity Id],
    'Metrics By Item Operation And Day'[Workspace Id],
    'Metrics By Item Operation And Day'[Item Id],
    'Metrics By Item Operation And Day'[Date],
    _DateFilter,
    "CuSeconds", SUM('Metrics By Item Operation And Day'[CU (s)]),
    "ThroughDate", _LastDate
  )
ORDER BY [CuSeconds] DESC
""".strip()


async def _load_cu_metrics(period_days: int) -> dict[str, Any]:
    cached = _cu_cache.get(period_days)
    daily_cached = _cu_daily_cache.get(period_days)
    if (
        cached
        and daily_cached
        and time.monotonic() - cached[0] < SCAN_CACHE_SECONDS
        and time.monotonic() - daily_cached[0] < SCAN_CACHE_SECONDS
    ):
        return cached[1]

    async with _cu_lock:
        cached = _cu_cache.get(period_days)
        daily_cached = _cu_daily_cache.get(period_days)
        if (
            cached
            and daily_cached
            and time.monotonic() - cached[0] < SCAN_CACHE_SECONDS
            and time.monotonic() - daily_cached[0] < SCAN_CACHE_SECONDS
        ):
            return cached[1]

        semantic_model_id = os.environ.get("FABRIC_CAPACITY_METRICS_MODEL_ID")
        if not semantic_model_id:
            raise FabricAdminError(
                "FABRIC_CAPACITY_METRICS_MODEL_ID is not configured."
            )

        response = await _power_bi_request(
            "POST",
            f"/v1.0/myorg/datasets/{semantic_model_id}/executeQueries",
            json={
                "queries": [{"query": _capacity_metrics_query(period_days)}],
                "serializerSettings": {"includeNulls": True},
            },
        )
        try:
            dax_rows = response["results"][0]["tables"][0]["rows"]
        except (KeyError, IndexError, TypeError) as error:
            raise FabricAdminError(
                "Capacity Metrics returned an unexpected ExecuteQueries payload."
            ) from error
        if not isinstance(dax_rows, list):
            raise FabricAdminError("Capacity Metrics rows are not a list.")

        item_totals: dict[tuple[str, str, str], float] = {}
        workspace_totals: dict[tuple[str, str], float] = {}
        capacity_totals: dict[str, float] = {}
        item_daily: dict[str, dict[str, float]] = {}
        workspace_daily: dict[str, dict[str, float]] = {}
        capacity_daily: dict[str, dict[str, float]] = {}
        covered_dates: set[str] = set()
        through_date: datetime | None = None

        for dax_row in dax_rows:
            if not isinstance(dax_row, dict):
                continue
            capacity_id = str(_dax_value(dax_row, "Capacity Id") or "").lower()
            workspace_id = str(_dax_value(dax_row, "Workspace Id") or "").lower()
            item_id = str(_dax_value(dax_row, "Item Id") or "").lower()
            cu_seconds = float(_dax_value(dax_row, "CuSeconds") or 0)
            metric_date_value = _dax_value(dax_row, "Date")
            row_through_date = _dax_value(dax_row, "ThroughDate")
            if row_through_date and through_date is None:
                through_date = datetime.fromisoformat(str(row_through_date))
            if (
                not capacity_id
                or not workspace_id
                or not item_id
                or not metric_date_value
            ):
                continue
            metric_date = datetime.fromisoformat(str(metric_date_value)).date().isoformat()
            covered_dates.add(metric_date)
            item_key = (capacity_id, workspace_id, item_id)
            item_totals[item_key] = item_totals.get(item_key, 0) + cu_seconds
            workspace_key = (capacity_id, workspace_id)
            workspace_totals[workspace_key] = (
                workspace_totals.get(workspace_key, 0) + cu_seconds
            )
            capacity_totals[capacity_id] = (
                capacity_totals.get(capacity_id, 0) + cu_seconds
            )
            item_daily.setdefault(item_id, {})[metric_date] = (
                item_daily.setdefault(item_id, {}).get(metric_date, 0) + cu_seconds
            )
            workspace_daily.setdefault(workspace_id, {})[metric_date] = (
                workspace_daily.setdefault(workspace_id, {}).get(metric_date, 0)
                + cu_seconds
            )
            capacity_daily.setdefault(capacity_id, {})[metric_date] = (
                capacity_daily.setdefault(capacity_id, {}).get(metric_date, 0)
                + cu_seconds
            )

        collected_at = datetime.now(UTC)
        ordered_dates = sorted(covered_dates)
        covered_days = len(ordered_dates)

        def metric_values(
            cu_seconds: float,
            daily_values: dict[str, float],
        ) -> dict[str, float]:
            denominator = covered_days * 86400
            return {
                "cuSeconds": cu_seconds,
                "averageCu": cu_seconds / denominator if denominator else 0,
                "peakDailyAverageCu": (
                    max(daily_values.values(), default=0) / 86400
                ),
            }

        result = {
            "source": "Fabric Capacity Metrics semantic model",
            "periodDays": period_days,
            "coveredDays": covered_days,
            "fromDate": (
                (through_date - timedelta(days=period_days - 1)).date().isoformat()
                if through_date
                else None
            ),
            "throughDate": through_date.date().isoformat() if through_date else None,
            "collectedAtUtc": collected_at.isoformat(),
            "items": [
                {
                    "capacityId": capacity_id,
                    "workspaceId": workspace_id,
                    "itemId": item_id,
                    **metric_values(cu_seconds, item_daily[item_id]),
                }
                for (
                    capacity_id,
                    workspace_id,
                    item_id,
                ), cu_seconds in item_totals.items()
            ],
            "workspaces": [
                {
                    "capacityId": capacity_id,
                    "workspaceId": workspace_id,
                    **metric_values(cu_seconds, workspace_daily[workspace_id]),
                }
                for (capacity_id, workspace_id), cu_seconds in workspace_totals.items()
            ],
            "capacities": [
                {
                    "capacityId": capacity_id,
                    **metric_values(cu_seconds, capacity_daily[capacity_id]),
                }
                for capacity_id, cu_seconds in capacity_totals.items()
            ],
        }
        cached_at = time.monotonic()
        _cu_cache[period_days] = (cached_at, result)
        _cu_daily_cache[period_days] = (
            cached_at,
            {
                "dates": ordered_dates,
                "item": item_daily,
                "workspace": workspace_daily,
                "capacity": capacity_daily,
            },
        )
        return result


async def _load_cu_timeseries(
    period_days: int,
    entity_type: str,
    entity_id: str,
) -> dict[str, Any]:
    summary = await _load_cu_metrics(period_days)
    daily = _cu_daily_cache[period_days][1]
    normalized_type = entity_type.lower()
    normalized_id = entity_id.lower()
    if normalized_type not in {"item", "workspace", "capacity"}:
        raise ValueError("entity_type must be item, workspace, or capacity.")

    values = daily[normalized_type].get(normalized_id)
    if values is None:
        raise FabricAdminError(
            f"No CU telemetry found for {normalized_type} '{normalized_id}'."
        )

    summary_collection = (
        summary["items"]
        if normalized_type == "item"
        else summary[f"{normalized_type}s"]
    )
    id_field = f"{normalized_type}Id"
    entity_summary = next(
        row for row in summary_collection if row[id_field] == normalized_id
    )
    return {
        "source": summary["source"],
        "periodDays": period_days,
        "coveredDays": summary["coveredDays"],
        "fromDate": summary["fromDate"],
        "throughDate": summary["throughDate"],
        "collectedAtUtc": summary["collectedAtUtc"],
        "entityType": normalized_type,
        "entityId": normalized_id,
        "summary": entity_summary,
        "series": [
            {
                "date": metric_date,
                "cuSeconds": values.get(metric_date, 0),
                "averageCu": values.get(metric_date, 0) / 86400,
            }
            for metric_date in daily["dates"]
        ],
    }


async def _scan_workspaces() -> list[dict[str, Any]]:
    global _scan_cache

    if _scan_cache and time.monotonic() - _scan_cache[0] < SCAN_CACHE_SECONDS:
        return _scan_cache[1]

    async with _scan_lock:
        if _scan_cache and time.monotonic() - _scan_cache[0] < SCAN_CACHE_SECONDS:
            return _scan_cache[1]

        modified = await _power_bi_request(
            "GET",
            "/v1.0/myorg/admin/workspaces/modified",
            params={
                "excludePersonalWorkspaces": "true",
                "excludeInActiveWorkspaces": "true",
            },
        )
        if not isinstance(modified, list):
            raise FabricAdminError("GetModifiedWorkspaces returned a non-list response.")
        workspace_ids = [
            row["id"]
            for row in modified
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        ]

        workspaces: list[dict[str, Any]] = []
        for offset in range(0, len(workspace_ids), 100):
            batch = workspace_ids[offset : offset + 100]
            request = await _power_bi_request(
                "POST",
                "/v1.0/myorg/admin/workspaces/getInfo",
                params={
                    "lineage": "true",
                    "datasourceDetails": "false",
                    "datasetSchema": "false",
                    "datasetExpressions": "false",
                    "getArtifactUsers": "false",
                },
                json={"workspaces": batch},
            )
            scan_id = request.get("id") if isinstance(request, dict) else None
            if not isinstance(scan_id, str):
                raise FabricAdminError("PostWorkspaceInfo did not return a scan ID.")

            for _ in range(120):
                status = await _power_bi_request(
                    "GET",
                    f"/v1.0/myorg/admin/workspaces/scanStatus/{scan_id}",
                )
                state = status.get("status") if isinstance(status, dict) else None
                if state == "Succeeded":
                    break
                if state == "Failed":
                    raise FabricAdminError(f"Workspace scan {scan_id} failed: {status}")
                await asyncio.sleep(1)
            else:
                raise FabricAdminError(f"Workspace scan {scan_id} timed out.")

            result = await _power_bi_request(
                "GET",
                f"/v1.0/myorg/admin/workspaces/scanResult/{scan_id}",
            )
            page = result.get("workspaces", []) if isinstance(result, dict) else []
            if not isinstance(page, list):
                raise FabricAdminError("GetScanResult field 'workspaces' is not a list.")
            workspaces.extend(row for row in page if isinstance(row, dict))

        _scan_cache = (time.monotonic(), workspaces)
        return workspaces


def _normalize_workspace(workspace: dict[str, Any]) -> dict[str, Any]:
    return {
        **workspace,
        "id": workspace.get("id"),
        "displayName": workspace.get("name") or workspace.get("displayName"),
        "type": workspace.get("type") or "Workspace",
        "state": workspace.get("state") or "Active",
    }


def _workspace_items(workspaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for workspace in workspaces:
        workspace_id = workspace.get("id")
        workspace_name = workspace.get("name") or workspace.get("displayName")
        capacity_id = workspace.get("capacityId")
        for collection, item_type in ARTIFACT_COLLECTIONS.items():
            artifacts = workspace.get(collection, [])
            if not isinstance(artifacts, list):
                continue
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    continue
                item_id = artifact.get("id") or artifact.get("objectId")
                display_name = artifact.get("displayName") or artifact.get("name")
                if not item_id or not display_name:
                    continue
                rows.append(
                    {
                        **artifact,
                        "id": item_id,
                        "displayName": display_name,
                        "type": item_type,
                        "workspaceId": workspace_id,
                        "workspaceName": workspace_name,
                        "capacityId": capacity_id,
                    }
                )
    return rows


async def _paginate(
    path: str,
    *,
    params: dict[str, str] | None = None,
    collection_key: str = "value",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    next_path = path
    next_params = dict(params or {})
    seen_tokens: set[str] = set()

    for _ in range(MAX_PAGES):
        payload = await _fabric_get(next_path, params=next_params)
        page = payload.get(collection_key, [])
        if not isinstance(page, list):
            raise FabricAdminError(
                f"Fabric Admin response field '{collection_key}' is not a list."
            )
        rows.extend(item for item in page if isinstance(item, dict))

        continuation_uri = payload.get("continuationUri")
        continuation_token = payload.get("continuationToken")
        if isinstance(continuation_token, str) and continuation_token:
            if continuation_token in seen_tokens:
                raise FabricAdminError("Fabric Admin returned a repeated continuation token.")
            seen_tokens.add(continuation_token)
            next_path = path
            next_params = {**(params or {}), "continuationToken": continuation_token}
        elif isinstance(continuation_uri, str) and continuation_uri:
            next_path = continuation_uri
            next_params = {}
        else:
            return rows
        await asyncio.sleep(PAGE_DELAY_SECONDS)

    raise FabricAdminError(f"Fabric Admin pagination exceeded {MAX_PAGES} pages.")


async def _cached_paginate(
    path: str,
    *,
    params: dict[str, str] | None = None,
    collection_key: str = "value",
) -> list[dict[str, Any]]:
    cache_key = (path, tuple(sorted((params or {}).items())), collection_key)
    cached = _admin_cache.get(cache_key)
    if cached:
        return list(cached[2])

    return await _refresh_admin_cache(
        cache_key,
        path=path,
        params=params,
        collection_key=collection_key,
        force=False,
    )


async def _refresh_admin_cache(
    cache_key: tuple[str, tuple[tuple[str, str], ...], str],
    *,
    path: str,
    params: dict[str, str] | None,
    collection_key: str,
    force: bool,
) -> list[dict[str, Any]]:
    async with _admin_lock:
        cached = _admin_cache.get(cache_key)
        if cached and not force:
            return list(cached[2])
        rows = await _paginate(
            path,
            params=params,
            collection_key=collection_key,
        )
        _admin_cache[cache_key] = (time.monotonic(), datetime.now(UTC), rows)
        return list(rows)


def _cache_collected_at(
    path: str,
    *,
    params: dict[str, str] | None = None,
    collection_key: str = "value",
) -> datetime:
    cache_key = (path, tuple(sorted((params or {}).items())), collection_key)
    cached = _admin_cache.get(cache_key)
    return cached[1] if cached else datetime.now(UTC)


def _result(
    rows: list[dict[str, Any]],
    endpoint: str,
    collected_at: datetime,
) -> dict[str, Any]:
    return {
        "source": f"Fabric Admin REST {endpoint}",
        "collectedAtUtc": collected_at.isoformat(),
        "count": len(rows),
        "value": rows,
    }


@mcp.tool()
async def list_workspaces(
    capacity_id: str | None = None,
    state: str | None = "active",
    workspace_type: str | None = None,
    include_personal: bool = False,
) -> dict[str, Any]:
    """List tenant-wide Fabric workspaces through the read-only Fabric Admin API.

    Use this tool for exhaustive tenant inventory. It does not require workspace
    membership. Optional filters are passed to Fabric Admin when supplied.
    """
    workspaces = [
        _normalize_workspace(row)
        for row in await _cached_paginate(
            "/v1/admin/workspaces",
            collection_key="workspaces",
        )
    ]
    rows = [
        row
        for row in workspaces
        if (
            include_personal
            or str(row.get("type", "")).casefold() != "personal"
        )
        and (not capacity_id or row.get("capacityId") == capacity_id)
        and (not state or str(row.get("state", "")).casefold() == state.casefold())
        and (
            not workspace_type
            or str(row.get("type", "")).casefold() == workspace_type.casefold()
        )
    ]
    return _result(
        rows,
        "/v1/admin/workspaces",
        _cache_collected_at(
            "/v1/admin/workspaces",
            collection_key="workspaces",
        ),
    )


@mcp.tool()
async def list_items(
    workspace_id: str | None = None,
    capacity_id: str | None = None,
    state: str | None = "active",
    item_type: str | None = None,
) -> dict[str, Any]:
    """List tenant-wide Fabric items through the read-only Fabric Admin API.

    Use workspace_id for drill-down, or omit it for an exhaustive active-item
    inventory. The response includes each item's workspace and capacity metadata
    when supplied by Fabric.
    """
    item_entities, workspaces = await asyncio.gather(
        _cached_paginate(
            "/v1/admin/items",
            params={"state": state} if state else None,
            collection_key="itemEntities",
        ),
        _cached_paginate("/v1/admin/workspaces", collection_key="workspaces"),
    )
    workspace_names = {
        row.get("id"): row.get("name")
        for row in workspaces
        if isinstance(row.get("id"), str)
    }
    rows = [
        {
            **row,
            "displayName": row.get("displayName") or row.get("name"),
            "workspaceName": workspace_names.get(row.get("workspaceId")),
        }
        for row in item_entities
        if (not workspace_id or row.get("workspaceId") == workspace_id)
        and (not capacity_id or row.get("capacityId") == capacity_id)
        and (not item_type or str(row.get("type", "")).casefold() == item_type.casefold())
        and (not state or str(row.get("state", "")).casefold() == state.casefold())
    ]
    return _result(
        rows,
        "/v1/admin/items",
        _cache_collected_at(
            "/v1/admin/items",
            params={"state": state} if state else None,
            collection_key="itemEntities",
        ),
    )


@mcp.tool()
async def get_cu_metrics(
    period_days: int = 14,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> dict[str, Any]:
    """Return read-only CU metrics and optional daily time series.

    Supported periods are 7, 14, 30, and 60 days. Capacity Metrics currently
    retains approximately 14 days; longer periods grow as daily history is
    collected into the Fabric SRE Lakehouse.
    """
    if period_days not in {7, 14, 30, 60}:
        raise ValueError("period_days must be one of 7, 14, 30, or 60.")
    if (entity_type is None) != (entity_id is None):
        raise ValueError("entity_type and entity_id must be provided together.")
    if entity_type and entity_id:
        return await _load_cu_timeseries(period_days, entity_type, entity_id)
    return await _load_cu_metrics(period_days)


async def _refresh_admin_snapshot() -> None:
    item_key = (
        "/v1/admin/items",
        (("state", "active"),),
        "itemEntities",
    )
    workspace_key = (
        "/v1/admin/workspaces",
        (),
        "workspaces",
    )
    await asyncio.gather(
        _refresh_admin_cache(
            item_key,
            path="/v1/admin/items",
            params={"state": "active"},
            collection_key="itemEntities",
            force=True,
        ),
        _refresh_admin_cache(
            workspace_key,
            path="/v1/admin/workspaces",
            params=None,
            collection_key="workspaces",
            force=True,
        ),
    )


async def _maintain_admin_cache() -> None:
    while True:
        try:
            await _refresh_admin_snapshot()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Fabric Admin background cache refresh failed.")
        await asyncio.sleep(SCAN_CACHE_SECONDS)


mcp_app = mcp.streamable_http_app()
mcp_app.router.lifespan_context = _app_lifespan
app = ApiKeyMiddleware(mcp_app)
