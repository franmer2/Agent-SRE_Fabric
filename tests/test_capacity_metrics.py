import pytest

from fabric_sre.capacity_metrics import (
    bind_capacity_query,
    capacity_metrics_ids,
    capacity_query_rows,
)


def test_discovers_dedicated_capacities_and_excludes_ppu() -> None:
    assert capacity_metrics_ids([
        {"id": "CAP-TWO", "sku": "F8"},
        {"id": "cap-one", "sku": "FTL64"},
        {"id": "cap-two", "sku": "F8"},
        {"id": "ppu", "sku": "PP3"},
    ]) == ["cap-one", "cap-two"]


@pytest.mark.parametrize("capacities", [
    [],
    [{"id": "ppu", "sku": "PP3"}],
    [{"sku": "F8"}],
    [{"id": "cap"}],
    [{"id": "cap", "sku": "unknown"}],
])
def test_invalid_or_empty_inventory_fails_explicitly(capacities: list[dict[str, str]]) -> None:
    with pytest.raises(ValueError):
        capacity_metrics_ids(capacities)


def test_binds_one_capacity_without_changing_existing_definitions() -> None:
    query = "DEFINE\n VAR _LastDate = 1\nEVALUATE ROW(\"Date\", _LastDate)"
    bound = bind_capacity_query(query, 'cap"one')
    assert bound.count("DEFINE") == 1
    assert 'MPARAMETER \'CapacitiesList\' = {"cap""one"}' in bound
    assert "VAR _LastDate = 1" in bound


def test_rejects_adapter_owned_capacity_binding() -> None:
    with pytest.raises(ValueError, match="must not define"):
        bind_capacity_query("DEFINE MPARAMETER 'CapacitiesList' = {\"old\"}", "new")


def test_rejects_partial_execute_queries_results() -> None:
    with pytest.raises(RuntimeError, match="ExecuteQueries error"):
        capacity_query_rows({
            "results": [{
                "error": {"message": "More than the allowed number of rows"},
                "tables": [{"rows": [{"CuSeconds": 1}]}],
            }],
        })


@pytest.mark.parametrize("payload", [
    {},
    {"results": [{"tables": [{"rows": "invalid"}]}]},
    {"results": [{"tables": [{"rows": [None]}]}]},
])
def test_rejects_execute_queries_schema_drift(payload: dict) -> None:
    with pytest.raises(RuntimeError):
        capacity_query_rows(payload)
