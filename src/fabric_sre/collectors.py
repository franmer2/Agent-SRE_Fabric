from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from urllib.parse import quote

from azure.core.credentials import TokenCredential

from fabric_sre.capacity_metrics import (
    bind_capacity_query,
    capacity_metrics_ids,
    capacity_query_rows,
)
from fabric_sre.http import RestClient

FABRIC_ROOT = "https://api.fabric.microsoft.com"
POWER_BI_ROOT = "https://api.powerbi.com"
POWER_BI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"
ARM_ROOT = "https://management.azure.com"


def _stamp(rows: Iterable[dict[str, Any]], source: str, collected_at: datetime) -> list[dict[str, Any]]:
    timestamp = collected_at.astimezone(UTC).isoformat()
    return [{**row, "_source": source, "_collectedAtUtc": timestamp} for row in rows]


def _power_bi_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _normalize_dax_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized.append(
            {
                (
                    key[key.rfind("[") + 1 : -1]
                    if "[" in key and key.endswith("]")
                    else key
                ): value
                for key, value in row.items()
            }
        )
    return normalized


def collect_fabric_inventory(
    credential: TokenCredential,
    *,
    collected_at: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    now = collected_at or datetime.now(UTC)
    fabric_client = RestClient(credential, f"{FABRIC_ROOT}/.default")
    power_bi_client = RestClient(credential, POWER_BI_SCOPE)
    headers = {"x-ms-fabric-skill": "fabric-sre-accelerator"}

    capacities = list(
        power_bi_client.paginate(f"{POWER_BI_ROOT}/v1.0/myorg/admin/capacities")
    )
    workspaces = list(
        fabric_client.paginate(f"{FABRIC_ROOT}/v1/admin/workspaces", headers=headers)
    )
    items = list(fabric_client.paginate(f"{FABRIC_ROOT}/v1/admin/items", headers=headers))

    return {
        "bronze_fabric_capacities": _stamp(
            capacities,
            "Power BI Admin REST /v1.0/myorg/admin/capacities",
            now,
        ),
        "bronze_fabric_workspaces": _stamp(workspaces, "Fabric Admin REST /v1/admin/workspaces", now),
        "bronze_fabric_items": _stamp(items, "Fabric Admin REST /v1/admin/items", now),
    }


def collect_powerbi_activity_events(
    credential: TokenCredential,
    activity_date: date,
    *,
    collected_at: datetime | None = None,
) -> list[dict[str, Any]]:
    now = collected_at or datetime.now(UTC)
    start = datetime.combine(activity_date, time.min, tzinfo=UTC)
    end = start + timedelta(days=1) - timedelta(microseconds=1)
    query = (
        f"startDateTime='{quote(_power_bi_timestamp(start))}'"
        f"&endDateTime='{quote(_power_bi_timestamp(end))}'"
    )
    client = RestClient(credential, POWER_BI_SCOPE)
    rows = client.paginate(
        f"{POWER_BI_ROOT}/v1.0/myorg/admin/activityevents?{query}",
        items_key="activityEventEntities",
        next_link_keys=("continuationUri",),
    )
    return _stamp(rows, "Power BI Admin getActivityEvents", now)


def collect_arm_capacities(
    credential: TokenCredential,
    subscription_ids: Iterable[str],
    *,
    collected_at: datetime | None = None,
) -> list[dict[str, Any]]:
    now = collected_at or datetime.now(UTC)
    client = RestClient(credential, f"{ARM_ROOT}/.default")
    rows: list[dict[str, Any]] = []
    for subscription_id in subscription_ids:
        url = (
            f"{ARM_ROOT}/subscriptions/{subscription_id}/providers/Microsoft.Fabric/capacities"
            "?api-version=2023-11-01"
        )
        rows.extend(client.paginate(url))
    return _stamp(rows, "ARM Microsoft.Fabric/capacities", now)


def execute_capacity_metrics_queries(
    credential: TokenCredential,
    semantic_model_id: str,
    queries: dict[str, str],
    *,
    collected_at: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    if not semantic_model_id:
        raise ValueError(
            "fabric.capacityMetrics.semanticModelId is required when capacity metrics collection is enabled"
        )
    now = collected_at or datetime.now(UTC)
    client = RestClient(credential, POWER_BI_SCOPE)
    capacities = list(client.paginate(f"{POWER_BI_ROOT}/v1.0/myorg/admin/capacities"))
    capacity_ids = capacity_metrics_ids(capacities)
    result: dict[str, list[dict[str, Any]]] = {name: [] for name in queries}
    url = f"{POWER_BI_ROOT}/v1.0/myorg/datasets/{semantic_model_id}/executeQueries"

    for capacity_id in capacity_ids:
        for target_table, dax in queries.items():
            payload = client.request(
                "POST",
                url,
                json={
                    "queries": [{"query": bind_capacity_query(dax, capacity_id)}],
                    "serializerSettings": {"includeNulls": True},
                },
                headers={"Content-Type": "application/json"},
            ).json()
            rows = _normalize_dax_rows(capacity_query_rows(payload))
            for row in rows:
                returned_id = row.get("CapacityId")
                if returned_id is not None and str(returned_id).lower() != capacity_id:
                    raise RuntimeError(
                        f"Capacity Metrics returned {returned_id} while querying {capacity_id}."
                    )
            result[target_table].extend(
                _stamp(rows, "Capacity Metrics semantic model ExecuteQueries", now)
            )
    return result
