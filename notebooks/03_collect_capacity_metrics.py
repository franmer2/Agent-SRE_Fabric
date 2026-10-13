# Fabric notebook source
# ruff: noqa: F821
import json
import os
import sys
from pathlib import Path

PACKAGE_PATH = "/lakehouse/default/Files/fabric-sre/src"
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)

from fabric_sre.auth import get_credential
from fabric_sre.collectors import execute_capacity_metrics_queries
from fabric_sre.config import load_config
from fabric_sre.lakehouse import append_delta

CONFIG_PATH = os.getenv(
    "FABRIC_SRE_CONFIG",
    "/lakehouse/default/Files/fabric-sre/config/client.parameters.yaml",
)
SCHEMA_PATH = "/lakehouse/default/Files/fabric-sre/config/client.parameters.schema.json"
QUERY_ROOT = Path("/lakehouse/default/Files/fabric-sre/queries/capacity-metrics")
config = load_config(CONFIG_PATH, SCHEMA_PATH)

if not config["features"]["collectCapacityMetrics"]:
    print("Capacity metrics collection is disabled.")
else:
    query_files = sorted(QUERY_ROOT.glob("*.dax"))
    if not query_files:
        raise FileNotFoundError(f"No DAX query adapters found under {QUERY_ROOT}")
    queries = {query_file.stem: query_file.read_text(encoding="utf-8") for query_file in query_files}
    results = execute_capacity_metrics_queries(
        get_credential(),
        config["fabric"]["capacityMetrics"]["semanticModelId"],
        queries,
    )
    counts = {
        table_name: append_delta(spark, table_name, rows)
        for table_name, rows in results.items()
    }
    print(json.dumps(counts, indent=2))
