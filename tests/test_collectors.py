from datetime import UTC, datetime
from typing import Any

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
            assert scope == f"{collectors.POWER_BI_ROOT}/.default"

        def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
            assert method == "POST"
            assert url.endswith("/datasets/model-one/executeQueries")
            assert kwargs["json"]["queries"] == [{"query": "EVALUATE test"}]
            return FakeResponse()

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
