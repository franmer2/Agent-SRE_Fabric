CREATE TABLE IF NOT EXISTS bronze_fabric_capacities (
  id STRING,
  displayName STRING,
  sku STRING,
  region STRING,
  state STRING,
  admins STRING,
  _source STRING,
  _collectedAtUtc STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_fabric_workspaces (
  id STRING,
  displayName STRING,
  capacityId STRING,
  state STRING,
  _source STRING,
  _collectedAtUtc STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_fabric_items (
  id STRING,
  displayName STRING,
  type STRING,
  workspaceId STRING,
  _source STRING,
  _collectedAtUtc STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver_item_cu (
  EventDate DATE,
  CapacityId STRING,
  WorkspaceId STRING,
  ItemId STRING,
  ItemName STRING,
  ItemType STRING,
  OperationName STRING,
  OperationType STRING,
  UserIdHash STRING,
  CuSeconds DECIMAL(24,6),
  DurationSeconds DECIMAL(24,6),
  IsFailure BOOLEAN,
  ThrottlingSeconds DECIMAL(24,6),
  CollectedAtUtc TIMESTAMP
) USING DELTA
PARTITIONED BY (EventDate);

CREATE TABLE IF NOT EXISTS silver_refresh (
  EventDate DATE,
  WorkspaceId STRING,
  ItemId STRING,
  RefreshType STRING,
  StartUtc TIMESTAMP,
  EndUtc TIMESTAMP,
  DurationSeconds DECIMAL(24,6),
  Status STRING,
  ErrorCode STRING,
  CollectedAtUtc TIMESTAMP
) USING DELTA
PARTITIONED BY (EventDate);

CREATE TABLE IF NOT EXISTS silver_storage (
  SnapshotDate DATE,
  WorkspaceId STRING,
  ItemId STRING,
  StorageBytes BIGINT,
  CollectedAtUtc TIMESTAMP
) USING DELTA
PARTITIONED BY (SnapshotDate);

CREATE TABLE IF NOT EXISTS collection_run (
  RunId STRING,
  Collector STRING,
  StartedUtc TIMESTAMP,
  EndedUtc TIMESTAMP,
  Status STRING,
  RowCount BIGINT,
  ErrorMessage STRING
) USING DELTA;
