# Capacity Metrics adapter

Place DAX queries validated against **the installed version** of the Fabric
Capacity Metrics semantic model in this folder. Each `table_name.dax` file
produces a `table_name` Delta table.

On each collection, the collector discovers dedicated capacities through the
admin API, then runs each adapter separately per capacity with
`DEFINE MPARAMETER 'CapacitiesList' = {"<capacity-id>"}`. An unparameterized
query may only return the model's default capacity; a list of multiple
capacities may fail when resolving their regions.
Do not define this parameter in DAX files: the collector injects it, including
when an adapter already contains a `DEFINE` block.

Premium Per User (`PP`) reservations are excluded: they are not dedicated
capacities for this CU source. API errors, truncated results, and schema drift
fail collection explicitly; a failed capacity is never converted to zero
consumption. The identity still needs read-only admin API access and Read/Build
on the model.

The recent-CU MCP uses only the source model's retention window; it does not
read Lakehouse history. Its `requestedCapacityIds` and `unavailableCapacityIds`
show the capacities queried and those with no returned CU rows. Historical
retention is accumulated by the scheduled notebook. When upgrading an existing
installation, deploy the MCP image and upload both `capacity_metrics.py` and
`collectors.py` to `Files/fabric-sre/src/fabric_sre` in the collection Lakehouse.
Do not rerun the append-only notebook just to verify deployment: that can
duplicate historical facts.

The app model can change without a public schema contract. Deployment therefore
runs a schema check before enabling collection and fails explicitly when an
expected column is missing. Do not replace this failure with an empty result.
