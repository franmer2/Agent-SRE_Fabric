from datetime import UTC, datetime
from typing import Any

import pytest

from fabric_sre import collectors
from fabric_sre.collectors import _power_bi_timestamp, execute_capacity_metrics_queries


def test_power_bi_timestamp_uses_utc_milliseconds() -> None:
    value = datetime(2026, 10, 9, 23, 59, 59, 999999, tzinfo=UTC)

    assert _power_bi_timestamp(value) == "2026-10-09T23:59:59.999Z"


def test_capacity_metrics_normalizes_dax_column_names(monkeypatch: Any) -> None:
    class FakeResponse:
        def json(self) -> dict[str, Any]:
            return {
                "results": [
                    {
                        "tables": [
                            {
                                "rows": [
                                    {
                                        "[EventDate]": "2026-10-11T00:00:00",
                                        "'Items'[ItemId]": "item-one",
                                        "[CuSeconds]": 42.5,
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

    class FakeRestClient:
        def __init__(self, credential: Any, scope: str) -> None:
            assert credential == "credential"
            assert scope == "https://analysis.windows.net/powerbi/api/.default"

        def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
            assert method == "POST"
            assert url.endswith("/datasets/model-one/executeQueries")
            assert kwargs["json"]["queries"] == [
                {"query": 'DEFINE\n  MPARAMETER \'CapacitiesList\' = {"cap-one"}\nEVALUATE test'}
            ]
            return FakeResponse()

        def paginate(self, url: str) -> list[dict[str, str]]:
            assert url.endswith("/admin/capacities")
            return [{"id": "cap-one", "sku": "F8"}]

    monkeypatch.setattr(collectors, "RestClient", FakeRestClient)
    collected_at = datetime(2026, 10, 11, 12, tzinfo=UTC)

    result = execute_capacity_metrics_queries(
        "credential",  # type: ignore[arg-type]
        "model-one",
        {"silver_item_cu": "EVALUATE test"},
        collected_at=collected_at,
    )

    assert result["silver_item_cu"] == [
        {
            "EventDate": "2026-10-11T00:00:00",
            "ItemId": "item-one",
            "CuSeconds": 42.5,
            "_source": "Capacity Metrics semantic model ExecuteQueries",
            "_collectedAtUtc": "2026-10-11T12:00:00+00:00",
        }
    ]


def test_capacity_metrics_queries_each_new_capacity(monkeypatch: Any) -> None:
    calls: list[str] = []

    class FakeResponse:
        def __init__(self, capacity_id: str) -> None:
            self.capacity_id = capacity_id

        def json(self) -> dict[str, Any]:
            return {"results": [{"tables": [{"rows": [
                {"[CapacityId]": self.capacity_id, "[CuSeconds]": 10},
            ]}]}]}

    class FakeRestClient:
        def __init__(self, credential: Any, scope: str) -> None:
            pass

        def paginate(self, url: str) -> list[dict[str, str]]:
            return [
                {"id": "cap-old", "sku": "F16"},
                {"id": "cap-new", "sku": "F8"},
                {"id": "ppu", "sku": "PP3"},
            ]

        def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
            query = kwargs["json"]["queries"][0]["query"]
            calls.append(query)
            capacity_id = "cap-new" if '{"cap-new"}' in query else "cap-old"
            return FakeResponse(capacity_id)

    monkeypatch.setattr(collectors, "RestClient", FakeRestClient)
    result = execute_capacity_metrics_queries(
        "credential",  # type: ignore[arg-type]
        "model",
        {"silver_item_cu": "EVALUATE test"},
    )
    assert len(calls) == 2
    assert {row["CapacityId"] for row in result["silver_item_cu"]} == {"cap-old", "cap-new"}
    assert all("MPARAMETER 'CapacitiesList'" in query for query in calls)


def test_capacity_metrics_rejects_ignored_parameter(monkeypatch: Any) -> None:
    class FakeResponse:
        def json(self) -> dict[str, Any]:
            return {"results": [{"tables": [{"rows": [{"[CapacityId]": "wrong-capacity"}]}]}]}

    class FakeRestClient:
        def __init__(self, credential: Any, scope: str) -> None:
            pass

        def paginate(self, url: str) -> list[dict[str, str]]:
            return [{"id": "requested-capacity", "sku": "F8"}]

        def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(collectors, "RestClient", FakeRestClient)
    with pytest.raises(RuntimeError, match="while querying requested-capacity"):
        execute_capacity_metrics_queries(
            "credential",  # type: ignore[arg-type]
            "model",
            {"silver_item_cu": "EVALUATE test"},
        )
