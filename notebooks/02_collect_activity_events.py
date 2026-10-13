# Fabric notebook source
# ruff: noqa: F821
import json
import os
import sys
from datetime import UTC, datetime, timedelta

PACKAGE_PATH = "/lakehouse/default/Files/fabric-sre/src"
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)

from fabric_sre.auth import get_credential
from fabric_sre.collectors import collect_powerbi_activity_events
from fabric_sre.config import load_config
from fabric_sre.lakehouse import upsert_delta

CONFIG_PATH = os.getenv(
    "FABRIC_SRE_CONFIG",
    "/lakehouse/default/Files/fabric-sre/config/client.parameters.yaml",
)
SCHEMA_PATH = "/lakehouse/default/Files/fabric-sre/config/client.parameters.schema.json"
config = load_config(CONFIG_PATH, SCHEMA_PATH)

credential = get_credential()
# The 28-day rolling API window includes the current, incomplete UTC day.
lookback = min(config["fabric"]["activityLookbackDays"], 27)
today = datetime.now(UTC).date()
counts = {}
for offset in range(1, lookback + 1):
    activity_date = today - timedelta(days=offset)
    rows = collect_powerbi_activity_events(credential, activity_date)
    counts[activity_date.isoformat()] = upsert_delta(
        spark,
        "bronze_powerbi_activity_events",
        rows,
        ("Id",),
    )
print(json.dumps(counts, indent=2))
