CREATE OR REPLACE TABLE silver_capacity_snapshot USING DELTA AS
WITH capacity_latest AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY id, CAST(_collectedAtUtc AS DATE)
      ORDER BY _collectedAtUtc DESC
    ) AS row_number
  FROM bronze_fabric_capacities
),
workspace_counts AS (
  SELECT
    capacityId,
    CAST(_collectedAtUtc AS DATE) AS SnapshotDate,
    COUNT(DISTINCT id) AS WorkspaceCount
  FROM bronze_fabric_workspaces
  WHERE capacityId IS NOT NULL
  GROUP BY capacityId, CAST(_collectedAtUtc AS DATE)
)
SELECT
  CAST(c._collectedAtUtc AS DATE) AS SnapshotDate,
  c.id AS CapacityId,
  c.displayName AS CapacityName,
  CASE
    WHEN c.sku LIKE 'F%' THEN 'F'
    WHEN c.sku LIKE 'P%' THEN 'P'
    WHEN lower(c.sku) LIKE '%trial%' THEN 'Trial'
    ELSE 'Other'
  END AS CapacityType,
  c.sku AS Sku,
  c.region AS Region,
  c.state AS State,
  c.admins AS AdminsJson,
  CAST(NULL AS STRING) AS SubscriptionId,
  CAST(NULL AS STRING) AS ResourceGroup,
  CAST(NULL AS STRING) AS TagsJson,
  COALESCE(w.WorkspaceCount, 0) AS WorkspaceCount,
  CAST(NULL AS DECIMAL(18,2)) AS EstimatedCost,
  CAST(c._collectedAtUtc AS TIMESTAMP) AS CollectedAtUtc
FROM capacity_latest c
LEFT JOIN workspace_counts w
  ON w.capacityId = c.id
  AND w.SnapshotDate = CAST(c._collectedAtUtc AS DATE)
WHERE c.row_number = 1;

CREATE OR REPLACE TABLE gold_workspace_current USING DELTA AS
WITH latest AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _collectedAtUtc DESC) AS row_number
  FROM bronze_fabric_workspaces
)
SELECT
  id AS WorkspaceId,
  displayName AS WorkspaceName,
  CAST(NULL AS STRING) AS DomainName,
  state AS WorkspaceState,
  CAST(false AS BOOLEAN) AS IsOrphaned,
  CAST(NULL AS DATE) AS LastActivityDate
FROM latest
WHERE row_number = 1;

CREATE OR REPLACE TABLE gold_item_current USING DELTA AS
WITH latest AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY _collectedAtUtc DESC) AS row_number
  FROM bronze_fabric_items
)
SELECT
  id AS ItemId,
  displayName AS ItemName,
  type AS ItemType,
  CAST(NULL AS STRING) AS Owner,
  CAST(NULL AS STRING) AS Certification,
  CAST(NULL AS TIMESTAMP) AS LastRefreshDate
FROM latest
WHERE row_number = 1;
