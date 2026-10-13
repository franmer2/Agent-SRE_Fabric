from __future__ import annotations

import json
from typing import Any, Protocol


class DataFrameWriter(Protocol):
    @property
    def write(self) -> Any: ...


def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            key: (
                json.dumps(value, ensure_ascii=False, sort_keys=True)
                if isinstance(value, (dict, list))
                else str(value)
            )
            for key, value in row.items()
            if value is not None
        }
        for row in rows
    ]


def append_delta(spark: Any, table_name: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    frame: DataFrameWriter = spark.createDataFrame(_normalize_rows(rows))
    (
        frame.write.format("delta")
        .mode("append")
        .option("mergeSchema", "true")
        .saveAsTable(table_name)
    )
    return len(rows)


def upsert_delta(
    spark: Any,
    table_name: str,
    rows: list[dict[str, Any]],
    key_columns: tuple[str, ...],
) -> int:
    if not rows:
        return 0
    normalized = _normalize_rows(rows)
    missing_keys = [
        key for key in key_columns if any(key not in row for row in normalized)
    ]
    if missing_keys:
        raise ValueError(
            f"Cannot upsert {table_name}; missing key columns: {', '.join(missing_keys)}"
        )

    frame = spark.createDataFrame(normalized).dropDuplicates(list(key_columns))
    if not spark.catalog.tableExists(table_name):
        (
            frame.write.format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(table_name)
        )
        return len(rows)

    from delta.tables import DeltaTable

    spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
    condition = " AND ".join(
        f"target.`{key.replace('`', '``')}` = source.`{key.replace('`', '``')}`"
        for key in key_columns
    )
    (
        DeltaTable.forName(spark, table_name)
        .alias("target")
        .merge(frame.alias("source"), condition)
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
    return len(rows)


def overwrite_delta(spark: Any, table_name: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        raise ValueError(f"Refusing to overwrite {table_name} with an empty data set")
    frame: DataFrameWriter = spark.createDataFrame(_normalize_rows(rows))
    (
        frame.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )
    return len(rows)
