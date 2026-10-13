CREATE OR REPLACE TABLE gold_capacity_daily USING DELTA AS
SELECT
  EventDate,
  CapacityId,
  SUM(CuSeconds) AS CuSeconds,
  AVG(CuSeconds) AS AverageCuSeconds,
  percentile_approx(CuSeconds, 0.95) AS P95CuSeconds,
  MAX(CuSeconds) AS MaxCuSeconds,
  SUM(ThrottlingSeconds) AS ThrottlingSeconds,
  SUM(CASE WHEN IsFailure THEN 1 ELSE 0 END) AS FailureCount
FROM silver_item_cu
GROUP BY EventDate, CapacityId;

CREATE OR REPLACE TABLE gold_item_daily USING DELTA AS
SELECT
  EventDate,
  CapacityId,
  WorkspaceId,
  ItemId,
  CONCAT(OperationType, '|', OperationName) AS OperationId,
  MAX(ItemName) AS ItemName,
  MAX(ItemType) AS ItemType,
  SUM(CuSeconds) AS CuSeconds,
  SUM(DurationSeconds) AS DurationSeconds,
  SUM(CASE WHEN IsFailure THEN 1 ELSE 0 END) AS FailureCount,
  SUM(ThrottlingSeconds) AS ThrottlingSeconds,
  COUNT(DISTINCT UserIdHash) AS UserCount
FROM silver_item_cu
GROUP BY EventDate, CapacityId, WorkspaceId, ItemId, OperationType, OperationName;

CREATE OR REPLACE TABLE gold_refresh_daily USING DELTA AS
SELECT
  EventDate,
  WorkspaceId,
  ItemId,
  COUNT(*) AS RefreshCount,
  SUM(CASE WHEN Status <> 'Completed' THEN 1 ELSE 0 END) AS RefreshFailureCount,
  AVG(DurationSeconds) AS AverageDurationSeconds,
  percentile_approx(DurationSeconds, 0.95) AS P95DurationSeconds
FROM silver_refresh
GROUP BY EventDate, WorkspaceId, ItemId;

CREATE OR REPLACE TABLE gold_storage_daily USING DELTA AS
SELECT
  SnapshotDate,
  WorkspaceId,
  ItemId,
  MAX(StorageBytes) AS StorageBytes
FROM silver_storage
GROUP BY SnapshotDate, WorkspaceId, ItemId;
