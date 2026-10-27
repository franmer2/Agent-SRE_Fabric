# Fabric SRE deployment guide

This guide follows a progressive journey. A user can first create Azure SRE
Agent, connect Fabric, and explore the environment through conversation, then
install Basic or Advanced without recreating the agent.

For a detailed procedure suitable for a non-technical audience, follow the
[step-by-step deployment guide](deployment-step-by-step.en.md).

## 1. Choose a progression level

| Capability | Discovery | Basic | Advanced |
|---|---:|---:|---:|
| Azure SRE Agent connected to Fabric Core | Yes | Yes | Yes |
| On-demand questions and generated visuals | Yes | Yes | Yes |
| Fabric Admin tenant inventory | No | Yes | Yes |
| Persistent bilingual Live Report | No | Yes | Yes |
| Recent CU from Fabric Capacity Metrics | Connector-dependent | Optional | Yes |
| Technical `Fabric Administration` workspace | No | No | Yes |
| Lakehouse, notebooks, and daily pipeline | No | No | Yes |
| Guaranteed history of at least 60 days | No | No | Yes |
| TMDL model and French/English PBIP reports | No | No | Yes |

### Discovery

Discovery is the recommended starting point for a new user:

1. create the agent at <https://sre.azure.com>;
2. connect Fabric Core MCP under **Builder > Connectors**;
3. select only the required read tools;
4. test the connection in a new conversation;
5. use the [prompt catalog](prompts.en.md).

This level provides dynamic answers and visuals from resources visible to the
identity. It does not provide guaranteed tenant inventory, a persistent Live
Report, or durable history.

### Basic

Basic is appropriate for a quick start, demonstration, or tenant that first
wants to validate inventory and agent behavior. It uses:

- Fabric Core MCP for live operations authorized to the identity;
- Fabric Admin MCP for read-only tenant inventory;
- the Azure SRE integrated Live Report;
- optionally, the `Fabric Capacity Metrics` model for recent CU.

It **does not require** the `Fabric Administration` workspace. Without a CU
source, inventory remains usable and CU values are marked unavailable. With
Capacity Metrics, the available Compute window is normally about 14 days;
requesting 30 or 60 days cannot recreate expired data.

Part of Basic configuration can be driven in natural language from a client
that supports Azure MCP Server: creating or updating the Azure SRE Agent
connector and registering common prompts. This alternative is not a magic
command in the agent's own chat and does not deploy the Fabric Admin MCP
service. The endpoint must already exist, Azure permissions must be available,
and secrets must remain in a secure mechanism.

### Advanced

Advanced adds a dedicated technical Fabric workspace, named
`Fabric Administration` by default. It hosts:

- the `FabricSRE` Lakehouse;
- collector files, notebooks, and the daily pipeline;
- Bronze, Silver, and Gold Delta tables;
- the `Fabric SRE` semantic model;
- French and English PBIP/TMDL Power BI reports;
- workspace identity and refresh connections.

This edition is required to guarantee at least 60 days of history, calculate
durable trends, and operate version-controlled Power BI reports.

## 2. Dependency architecture

```text
Discovery
Azure SRE Agent
  └─ Fabric Core MCP
       └─ On-demand questions and visuals

Basic
Discovery
  ├─ Fabric Core MCP
  ├─ Fabric Admin MCP (Container App)
  ├─ FR/EN Live Report
  └─ Capacity Metrics (optional, native retention)

Advanced
Basic
  └─ Fabric Administration workspace
       ├─ FabricSRE Lakehouse
       ├─ Notebooks + daily pipeline
       ├─ Bronze / Silver / Gold tables
       ├─ TMDL semantic model
       └─ French and English Power BI reports
```

Deleting the Advanced workspace does not stop Basic tenant inventory, but it
stops collection, historical storage, the semantic model, and its Power BI
reports.

Visuals generated in a conversation do not replace the Basic Live Report or
Advanced Power BI reports: their layout and filters are not guaranteed between
sessions.

## 3. Prerequisites

### Discovery

- an active Azure subscription;
- Owner, or Contributor with User Access Administrator, to create the agent;
- network access to `*.azuresre.ai`;
- an approved Fabric MCP endpoint and its authentication method;
- read access to the Fabric resources to observe.

The command line, local repository, and Fabric Admin MCP infrastructure are not
required when remaining at Discovery.

### Basic and Advanced

### Administrative access

- Fabric Administrator for bootstrap;
- Owner or User Access Administrator on Azure resources being created;
- access to the target Azure SRE subscription, resource group, and agent;
- Azure CLI authenticated to the correct tenant;
- PowerShell 7, Python, Node.js, and repository dependencies.

### Fabric tenant settings

In the Fabric admin portal, scope each setting to the dedicated SRE identity
security group:

1. enable **Service principals can use Fabric APIs**;
2. enable service-principal access to **read-only admin APIs**;
3. enable detailed scanner metadata only when required;
4. do not enable update admin APIs for the read identity.

Keep any action identity separate. Every write operation must retain human
approval.

### Client parameter file

```powershell
Copy-Item config\client.parameters.example.yaml `
  config\client.parameters.yaml
```

Set at least:

- `client`, `azure.tenantId`, and `azure.subscriptionIds`;
- `foundry.subscriptionId`, `resourceGroup`, and `agentName`;
- the complete `foundry.fabricAdminMcp` section;
- `fabric.capacityScope`;
- `fabric.capacityMetrics.semanticModelId` when recent CU is enabled.

Never commit client parameters when they contain sensitive values. Keep secrets
in Container Apps, Key Vault, or the pipeline secret store.

### Local validation

```powershell
.\scripts\validate.ps1
```

This runs tests, Ruff, regenerates PBIP reports, and validates both report
definitions. It requires the Power BI authoring CLIs even for Basic. The full
validation is still recommended to certify the delivery package.

Verify the active account and target resource:

```powershell
.\scripts\preflight-agent.ps1 `
  -SubscriptionId "<agent-subscription>" `
  -ResourceGroup "<resource-group>" `
  -AgentName "<agent-name>" `
  -ExpectedAccount "<admin@tenant>"
```

## 4. Basic installation

### Step 1 — Prepare identities

1. Create or reuse the security group allowed to call read-only admin APIs.
2. Confirm the agent managed identity can use Fabric Core MCP.
3. Do not grant the Fabric Admin reader Contributor on workspaces. Tenant
   inventory is authorized through tenant settings, not Viewer assignments on
   every workspace.

### Step 2 — Deploy Fabric Admin MCP

```powershell
.\scripts\deploy-fabric-admin-mcp.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml
```

The script:

- creates or reuses the reader application and service principal;
- adds it to the admin API security group;
- creates or reuses the configured Container Apps, ACR, and managed identity;
- keeps secrets in Container Apps;
- deploys the MCP service with at least one replica;
- configures the Capacity Metrics model ID when supplied.

It must not print or commit secrets.

### Step 3 — Configure the agent connector

Create or update the Azure SRE connector named `FabricAdmin`:

- type: MCP, Streamable HTTP;
- endpoint: the Container App `/mcp` URL;
- authentication: custom `x-api-key` header;
- selected tools:
  - `list_workspaces`;
  - `list_items`;
  - `get_cu_metrics` when Capacity Metrics is configured;
- tools visible to the agent:
  - `FabricAdmin_list_workspaces`;
  - `FabricAdmin_list_items`;
  - `FabricAdmin_get_cu_metrics`.

Keep the `FabricSRE` connector to Fabric Core MCP for live operations scoped to
workspaces visible to the identity.

### Step 4 — Publish agent configuration and Live Report

Publish `agent/azure-sre-agent.yaml` to `meta_agent`, then publish the bilingual
Live Report. Confirm that no tool is duplicated and that the report can invoke
all three Fabric Admin tools and the FabricSRE capacity-inventory tool.

Use the latest approved asset and run the acceptance procedure in the
[Live Report specification](live-report.en.md). The development environment's
validated reference is service version 41, but an import into another
environment can receive another number; capabilities and acceptance checks are
authoritative.

### Step 5 — Verify Basic

- `/health` returns `status: ok`;
- the cache maintainer is running;
- inventory contains the expected non-personal workspaces;
- capacity, workspace, and item CU totals reconcile when CU is available;
- the FR/EN toggle translates the UI without clearing filters;
- no write action is exposed without approval.

For Advanced, prefer a small Fabric capacity dedicated to the SRE
administration workspace. A production-capacity outage must not also stop the
monitoring Lakehouse, notebooks, and pipeline. See
[Stopped Fabric capacity](live-report.en.md#5-stopped-fabric-capacity).

## 5. Advanced installation

Install Basic first, then complete the following steps.

### Step 1 — Preview and create the workspace

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -WhatIf
```

Create or reuse the workspace and Lakehouse:

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -CreateWorkspace
```

**Important limitation:** this script creates or resolves the workspace and
Lakehouse, then prints a plan. It does not yet upload every file, create the
notebooks/pipeline, or automatically publish the model and reports.

### Step 2 — Configure the workspace

1. Assign the workspace to an appropriate Fabric capacity.
2. Enable its workspace identity.
3. Grant Contributor to the collection or automation identity.
4. Grant only required read/Build permissions to consumption identities.
5. Do not grant Contributor to the agent read identity.

### Step 3 — Deploy collection assets

Upload under `Files/fabric-sre/`:

- `config/client.parameters.yaml`;
- `src/fabric_sre/`;
- `notebooks/`;
- `queries/`.

Create notebooks from the versioned files and create the daily pipeline from
`pipelines/daily-collection.pipeline.template.json`.

Run in this order:

1. table bootstrap;
2. inventory and activity collection;
3. Capacity Metrics collection;
4. Silver/Gold build;
5. data quality checks.

Confirm DAX response columns are normalized before Delta writes and that Gold
tables contain non-null identifiers and CU.

### Step 4 — Deploy Power BI

1. Set the TMDL Server and Database parameters.
2. Publish the `Fabric SRE` semantic model.
3. Create a `WorkspaceIdentity` SQL cloud connection.
4. Bind the model to that connection.
5. Trigger and verify a refresh.
6. Publish the French and English PBIP reports.
7. Certify artifacts according to customer governance.

### Step 5 — Schedule and monitor

- schedule the pipeline at least daily;
- retain at least 60 days, 400 by default;
- alert when freshness exceeds the configured SLO;
- honor `Retry-After` on 429 responses;
- monitor pipeline status, collected row counts, and explicit errors.

### Step 6 — Verify Advanced

In addition to Basic checks:

- one complete collection succeeds;
- Bronze, Silver, and Gold contain the current date;
- `gold_capacity_daily` and `gold_item_daily` do not contain only blank rows;
- history progressively reaches 60 days;
- semantic-model refresh succeeds;
- French and English reports show matching totals;
- Live Report and Power BI CU reconcile over a common period.

## 6. Upgrade from Basic to Advanced

The upgrade is additive:

1. keep the Basic agent, connectors, and Live Report;
2. create the `Fabric Administration` workspace;
3. deploy the Lakehouse and collectors;
4. allow history to accumulate;
5. publish the model and reports;
6. update agent instructions to prefer Gold for historical periods and direct
   telemetry for freshness.

The upgrade does not require recreating the agent or Fabric Admin connector.

## 7. Return from Advanced to Basic

Before deleting the workspace:

1. disable routines that depend on Gold;
2. export data required for audit;
3. remove links to workspace Power BI reports;
4. confirm the Live Report still uses Fabric Admin MCP and direct Capacity
   Metrics;
5. notify users that 60-day analysis and Power BI reports will no longer be
   available.

Never delete the workspace merely to repair a pipeline issue. Repair or disable
dependencies first.

## 8. Quick troubleshooting

| Symptom | Check |
|---|---|
| Only a few workspaces | Use `FabricAdmin_list_workspaces`, not only Fabric Core |
| CU unavailable | Check model ID, refresh, and Read/Build access |
| Incomplete 60-day CU request in Basic | Native retention limit; install Advanced |
| Pipeline succeeds but Gold is blank | Check DAX aliases and column normalization |
| Power BI refresh denied | Check `WorkspaceIdentity` connection and binding |
| Admin API 401/403 | Check tenant settings, security group, and propagation |
| 429 | Honor `Retry-After`, cache, and pagination pacing |
| Slow cold Live Report | Keep one minimum Container Apps replica |

## 9. Definition of done

### Basic

- complete tenant inventory;
- operational bilingual Live Report;
- recent CU clearly dated or explicitly unavailable;
- read-only agent;
- validated MCP health and cache.

### Advanced

All Basic criteria, plus:

- operational daily collection;
- durable history of at least 60 days;
- refreshable semantic model;
- two published PBIP reports;
- documented freshness, quality, and replay controls.
