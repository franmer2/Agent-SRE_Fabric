# Fabric notebook source
# ruff: noqa: F821
import json
import os
import sys
from datetime import UTC, datetime

PACKAGE_PATH = "/lakehouse/default/Files/fabric-sre/src"
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)

from fabric_sre.auth import get_credential
from fabric_sre.collectors import collect_arm_capacities, collect_fabric_inventory
from fabric_sre.config import load_config
from fabric_sre.lakehouse import append_delta

CONFIG_PATH = os.getenv(
    "FABRIC_SRE_CONFIG",
    "/lakehouse/default/Files/fabric-sre/config/client.parameters.yaml",
)
SCHEMA_PATH = "/lakehouse/default/Files/fabric-sre/config/client.parameters.schema.json"

config = load_config(CONFIG_PATH, SCHEMA_PATH)
credential = get_credential()
collected_at = datetime.now(UTC)

datasets = collect_fabric_inventory(credential, collected_at=collected_at)
try:
    datasets["bronze_arm_capacities"] = collect_arm_capacities(
        credential,
        config["azure"]["subscriptionIds"],
        collected_at=collected_at,
    )
except ValueError as error:
    print(
        json.dumps(
            {
                "collector": "bronze_arm_capacities",
                "status": "unsupported_in_fabric_notebook",
                "error": str(error),
            }
        )
    )

summary = {
    table_name: append_delta(spark, table_name, rows)
    for table_name, rows in datasets.items()
}
print(json.dumps(summary, indent=2))
