from __future__ import annotations

import asyncio
import importlib.util
import time
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Self


def _load_server() -> ModuleType:
    path = (
        Path(__file__).parents[1]
        / "services"
        / "fabric-admin-mcp"
        / "server.py"
    )
    spec = importlib.util.spec_from_file_location("fabric_admin_mcp_server", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_paginate_follows_continuation_token(monkeypatch: Any) -> None:
    server = _load_server()
    calls: list[tuple[str, dict[str, str]]] = []

    async def fake_get(path: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
        current = dict(params or {})
        calls.append((path, current))
        if "continuationToken" not in current:
            return {"workspaces": [{"id": "one"}], "continuationToken": "next"}
        if current["continuationToken"] == "next":
            return {"workspaces": [], "continuationToken": "after-empty"}
        return {"workspaces": [{"id": "two"}]}

    monkeypatch.setattr(server, "_fabric_get", fake_get)
    monkeypatch.setattr(server, "PAGE_DELAY_SECONDS", 0)

    rows = asyncio.run(
        server._paginate(
            "/v1/admin/workspaces",
            params={"state": "active"},
            collection_key="workspaces",
        )
    )

    assert rows == [{"id": "one"}, {"id": "two"}]
    assert calls == [
        ("/v1/admin/workspaces", {"state": "active"}),
        (
            "/v1/admin/workspaces",
            {"state": "active", "continuationToken": "next"},
        ),
        (
            "/v1/admin/workspaces",
            {"state": "active", "continuationToken": "after-empty"},
        ),
    ]


def test_list_items_uses_admin_filters(monkeypatch: Any) -> None:
    server = _load_server()

    async def fake_paginate(
        path: str,
        *,
        params: dict[str, str] | None = None,
        collection_key: str = "value",
    ) -> list[dict[str, Any]]:
        if path == "/v1/admin/workspaces":
            assert params is None
            assert collection_key == "workspaces"
            return [{"id": "workspace-one", "name": "Workspace One"}]
        assert path == "/v1/admin/items"
        assert params == {"state": "active"}
        assert collection_key == "itemEntities"
        return [
            {
                "id": "item-one",
                "name": "Report One",
                "type": "Report",
                "state": "Active",
                "workspaceId": "workspace-one",
                "capacityId": "capacity-one",
            },
            {
                "id": "item-two",
                "name": "Model One",
                "type": "SemanticModel",
                "state": "Active",
                "workspaceId": "workspace-one",
                "capacityId": "capacity-one",
            },
        ]

    monkeypatch.setattr(server, "_paginate", fake_paginate)

    result = asyncio.run(
        server.list_items(
            workspace_id="workspace-one",
            capacity_id="capacity-one",
            state="active",
            item_type="Report",
        )
    )

    assert result["count"] == 1
    assert result["value"][0] == {
        "id": "item-one",
        "name": "Report One",
        "displayName": "Report One",
        "type": "Report",
        "state": "Active",
        "workspaceId": "workspace-one",
        "workspaceName": "Workspace One",
        "capacityId": "capacity-one",
    }


def test_power_bi_request_sends_bearer_token(monkeypatch: Any) -> None:
    server = _load_server()
    observed_headers: dict[str, str] = {}

    class FakeCredential:
        async def get_token(self, scope: str) -> Any:
            assert scope == server.POWER_BI_SCOPE
            return type("Token", (), {"token": "test-token"})()

        async def close(self) -> None:
            return None

    class FakeResponse:
        status_code = 200

        def json(self) -> dict[str, list[Any]]:
            return {"value": []}

    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            assert timeout == 60.0

        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
            assert method == "GET"
            assert url == f"{server.POWER_BI_ROOT}/admin/test"
            observed_headers.update(kwargs["headers"])
            return FakeResponse()

    monkeypatch.setattr(server, "_fabric_credential", FakeCredential)
    monkeypatch.setattr(server.httpx, "AsyncClient", FakeClient)

    result = asyncio.run(server._power_bi_request("GET", "/admin/test"))

    assert result == {"value": []}
    assert observed_headers["Authorization"] == "Bearer test-token"


def test_cached_paginate_reuses_recent_result(monkeypatch: Any) -> None:
    server = _load_server()
    calls = 0

    async def fake_paginate(
        path: str,
        *,
        params: dict[str, str] | None = None,
        collection_key: str = "value",
    ) -> list[dict[str, Any]]:
        nonlocal calls
        calls += 1
        return [{"id": "workspace-one"}]

    async def run_twice() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        first = await server._cached_paginate(
            "/v1/admin/workspaces",
            collection_key="workspaces",
        )
        second = await server._cached_paginate(
            "/v1/admin/workspaces",
            collection_key="workspaces",
        )
        return first, second

    monkeypatch.setattr(server, "_paginate", fake_paginate)

    first, second = asyncio.run(run_twice())

    assert calls == 1
    assert first == second == [{"id": "workspace-one"}]
    assert first is not second


def test_cached_paginate_serves_stale_without_blocking(monkeypatch: Any) -> None:
    server = _load_server()
    cache_key = (
        "/v1/admin/items",
        (("state", "active"),),
        "itemEntities",
    )
    server._admin_cache[cache_key] = (
        time.monotonic() - server.SCAN_CACHE_SECONDS - 1,
        datetime.now(UTC),
        [{"id": "stale-item"}],
    )
    async def read_twice() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        first = await server._cached_paginate(
            "/v1/admin/items",
            params={"state": "active"},
            collection_key="itemEntities",
        )
        second = await server._cached_paginate(
            "/v1/admin/items",
            params={"state": "active"},
            collection_key="itemEntities",
        )
        return first, second

    async def unexpected_refresh(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        raise AssertionError("A stale read must not block on a refresh.")

    monkeypatch.setattr(server, "_refresh_admin_cache", unexpected_refresh)

    first, second = asyncio.run(read_twice())

    assert first == second == [{"id": "stale-item"}]


def test_cache_maintainer_repeats_refresh(monkeypatch: Any) -> None:
    server = _load_server()
    refreshes = 0

    async def fake_refresh() -> None:
        nonlocal refreshes
        refreshes += 1

    async def run_maintainer() -> None:
        task = asyncio.create_task(server._maintain_admin_cache())
        while refreshes < 2:
            await asyncio.sleep(0)
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    monkeypatch.setattr(server, "_refresh_admin_snapshot", fake_refresh)
    monkeypatch.setattr(server, "SCAN_CACHE_SECONDS", 0)

    asyncio.run(run_maintainer())

    assert refreshes >= 2
    assert server.mcp_app.router.lifespan_context is server._app_lifespan


def test_get_cu_metrics_aggregates_all_levels(monkeypatch: Any) -> None:
    server = _load_server()

    async def fake_power_bi_request(
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        assert method == "POST"
        assert path.endswith("/datasets/model-one/executeQueries")
        assert params is None
        assert json and "- 6" in json["queries"][0]["query"]
        return {
            "results": [
                {
                    "tables": [
                        {
                            "rows": [
                                {
                                    "Metrics[Capacity Id]": "CAP-ONE",
                                    "Metrics[Workspace Id]": "WS-ONE",
                                    "Metrics[Item Id]": "ITEM-ONE",
                                    "Metrics[Date]": "2026-10-10T00:00:00",
                                    "[CuSeconds]": 12.5,
                                    "[ThroughDate]": "2026-10-11T00:00:00",
                                },
                                {
                                    "Metrics[Capacity Id]": "CAP-ONE",
                                    "Metrics[Workspace Id]": "WS-ONE",
                                    "Metrics[Item Id]": "ITEM-TWO",
                                    "Metrics[Date]": "2026-10-10T00:00:00",
                                    "[CuSeconds]": 7.5,
                                    "[ThroughDate]": "2026-10-11T00:00:00",
                                },
                                {
                                    "Metrics[Capacity Id]": "CAP-ONE",
                                    "Metrics[Workspace Id]": "WS-ONE",
                                    "Metrics[Item Id]": "ITEM-ONE",
                                    "Metrics[Date]": "2026-10-11T00:00:00",
                                    "[CuSeconds]": 4.5,
                                    "[ThroughDate]": "2026-10-11T00:00:00",
                                },
                            ]
                        }
                    ]
                }
            ]
        }

    monkeypatch.setenv("FABRIC_CAPACITY_METRICS_MODEL_ID", "model-one")
    monkeypatch.setattr(server, "_power_bi_request", fake_power_bi_request)

    result = asyncio.run(server.get_cu_metrics(period_days=7))

    assert result["fromDate"] == "2026-10-05"
    assert result["throughDate"] == "2026-10-11"
    assert result["coveredDays"] == 2
    assert result["items"] == [
        {
            "capacityId": "cap-one",
            "workspaceId": "ws-one",
            "itemId": "item-one",
            "cuSeconds": 17.0,
            "averageCu": 17.0 / 172800,
            "peakDailyAverageCu": 12.5 / 86400,
        },
        {
            "capacityId": "cap-one",
            "workspaceId": "ws-one",
            "itemId": "item-two",
            "cuSeconds": 7.5,
            "averageCu": 7.5 / 172800,
            "peakDailyAverageCu": 7.5 / 86400,
        },
    ]
    assert result["workspaces"] == [
        {
            "capacityId": "cap-one",
            "workspaceId": "ws-one",
            "cuSeconds": 24.5,
            "averageCu": 24.5 / 172800,
            "peakDailyAverageCu": 20.0 / 86400,
        }
    ]
    assert result["capacities"] == [
        {
            "capacityId": "cap-one",
            "cuSeconds": 24.5,
            "averageCu": 24.5 / 172800,
            "peakDailyAverageCu": 20.0 / 86400,
        }
    ]

    detail = asyncio.run(
        server.get_cu_metrics(
            period_days=7,
            entity_type="item",
            entity_id="ITEM-ONE",
        )
    )
    assert detail["summary"] == result["items"][0]
    assert detail["series"] == [
        {
            "date": "2026-10-10",
            "cuSeconds": 12.5,
            "averageCu": 12.5 / 86400,
        },
        {
            "date": "2026-10-11",
            "cuSeconds": 4.5,
            "averageCu": 4.5 / 86400,
        },
    ]


def test_get_cu_metrics_rejects_unsupported_period() -> None:
    server = _load_server()

    try:
        asyncio.run(server.get_cu_metrics(period_days=15))
    except ValueError as error:
        assert str(error) == "period_days must be one of 7, 14, 30, or 60."
    else:
        raise AssertionError("Unsupported period should fail.")


def test_get_cu_metrics_requires_complete_entity_scope() -> None:
    server = _load_server()

    try:
        asyncio.run(server.get_cu_metrics(entity_type="workspace"))
    except ValueError as error:
        assert str(error) == "entity_type and entity_id must be provided together."
    else:
        raise AssertionError("Incomplete entity scope should fail.")
