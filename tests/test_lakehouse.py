import pytest

from fabric_sre.lakehouse import _normalize_rows, upsert_delta


def test_normalize_rows_serializes_values_and_removes_nulls() -> None:
    rows = [
        {
            "id": "event-1",
            "duration": 42,
            "succeeded": True,
            "details": {"b": 2, "a": 1},
            "sources": ["gateway", "cloud"],
            "optional": None,
        }
    ]

    assert _normalize_rows(rows) == [
        {
            "id": "event-1",
            "duration": "42",
            "succeeded": "True",
            "details": '{"a": 1, "b": 2}',
            "sources": '["gateway", "cloud"]',
        }
    ]


def test_upsert_delta_rejects_rows_without_key_columns() -> None:
    with pytest.raises(ValueError, match="missing key columns: Id"):
        upsert_delta(object(), "bronze_events", [{"Operation": "ViewReport"}], ("Id",))
