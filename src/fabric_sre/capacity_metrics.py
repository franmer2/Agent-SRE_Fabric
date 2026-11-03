from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def capacity_metrics_ids(capacities: list[dict[str, Any]]) -> list[str]:
    ids: set[str] = set()
    for capacity in capacities:
        capacity_id = capacity.get("id")
        sku = capacity.get("sku")
        if not isinstance(capacity_id, str) or not capacity_id.strip():
            raise ValueError("Capacity inventory contains a missing or invalid ID.")
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"Capacity {capacity_id} has a missing or invalid SKU.")
        if re.fullmatch(r"PP\d+", sku, re.IGNORECASE):
            logger.info("Skipping PPU reservation %s: no dedicated capacity CU source.", capacity_id)
            continue
        if not re.fullmatch(r"(?:FTL|FT|F|P|A|EM)\d+", sku, re.IGNORECASE):
            raise ValueError(f"Unsupported Capacity Metrics SKU {sku!r} for {capacity_id}.")
        ids.add(capacity_id.strip().lower())
    if not ids:
        raise ValueError("No supported capacities were discovered for Capacity Metrics.")
    return sorted(ids)


def bind_capacity_query(query: str, capacity_id: str) -> str:
    if not capacity_id.strip():
        raise ValueError("A capacity ID is required for a Capacity Metrics query.")
    if re.search(r"\bMPARAMETER\s+'CapacitiesList'", query, re.IGNORECASE):
        raise ValueError("The DAX adapter must not define CapacitiesList itself.")
    escaped_id = capacity_id.replace('"', '""')
    parameter = f'MPARAMETER \'CapacitiesList\' = {{"{escaped_id}"}}'
    define = re.match(r"\s*DEFINE\b", query, re.IGNORECASE)
    if define:
        return f"{query[:define.end()]}\n  {parameter}\n{query[define.end():]}"
    return f"DEFINE\n  {parameter}\n{query}"


def capacity_query_rows(payload: Any) -> list[dict[str, Any]]:
    try:
        result = payload["results"][0]
        table = result["tables"][0]
        rows = table["rows"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Capacity Metrics returned an unexpected ExecuteQueries payload.") from error
    for container in (payload, result, table):
        if container.get("error"):
            raise RuntimeError(f"Capacity Metrics ExecuteQueries error: {container['error']}")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("Capacity Metrics rows must be a list of objects.")
    return rows
