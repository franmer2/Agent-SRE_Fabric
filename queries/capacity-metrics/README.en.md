# Capacity Metrics adapter

Place DAX queries validated against **the installed version** of the Fabric
Capacity Metrics semantic model in this folder. Each `table_name.dax` file
produces a `table_name` Delta table.

The app model can change without a public schema contract. Deployment therefore
runs a schema check before enabling collection and fails explicitly when an
expected column is missing. Do not replace this failure with an empty result.
