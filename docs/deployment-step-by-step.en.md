# Fabric SRE step-by-step deployment

This document explains how to install the Fabric SRE solution when the person
performing the installation is unfamiliar with both the project and the
customer environment.

It supplements the [technical deployment guide](deployment.en.md). It does not
replace that guide for architecture decisions.

> **Important**
>
> - Follow the steps in order.
> - Never guess an identifier, subscription, or resource name.
> - Never copy a secret, API key, or password into this document, an email,
>   Teams, or Git.
> - If a button or resource described below is not visible, stop the
>   installation and ask the administrator listed in the preparation sheet for
>   help.
> - Portal labels change over time. English names are used throughout to make
>   screens easier to find.

## 1. Progressive journey

The solution is discovered and installed in three levels. You do not need to
select Basic or Advanced before trying the agent.

### Discovery level

Discovery lets you:

- create Azure SRE Agent from the portal;
- connect Fabric Core MCP;
- ask questions about visible resources;
- generate on-demand tables and visuals;
- understand the agent's capabilities and limitations before installing the
  Fabric SRE solution.

This level does not provide guaranteed tenant inventory, a persistent Live
Report, or durable history.

### Basic edition

Basic installs:

- the Fabric SRE configuration on the existing Azure SRE agent;
- the Fabric Core connector already tested during Discovery;
- a read-only Fabric Admin MCP service;
- the bilingual Live Report;
- optionally, recent metrics from the Fabric Capacity Metrics app.

Basic does not create durable history in a Lakehouse.

### Advanced edition

Advanced installs Basic first, then adds:

- a Microsoft Fabric workspace named `Fabric Administration` by default;
- a Lakehouse named `FabricSRE` by default;
- six notebooks;
- a daily collection pipeline;
- Bronze, Silver, and Gold tables;
- a Power BI semantic model;
- one French report and one English report.

### How to choose

Start with **Discovery** to validate Fabric access and learn how to use Azure
SRE Agent.

Then choose **Basic** to obtain tenant inventory, a bilingual Live Report, and
optionally recent CU without durable history.

Choose **Advanced** if the customer wants to:

- retain at least 60 days of history;
- analyze trends;
- use version-controlled Power BI reports;
- retain administration data daily.

Moving from Discovery to Basic or Advanced does not require recreating the
agent.

## 2. Division of responsibilities

One person may fill several roles, but all the roles below must be covered.

| Role | What this person must be able to do |
|---|---|
| Solution owner | Approve the Discovery, Basic, or Advanced progression and names |
| Fabric administrator | Change Fabric tenant settings |
| Azure administrator | Create or use resources in the subscription |
| Entra administrator | Create a security group and manage its members |
| Azure SRE administrator | Modify the agent and its connectors |
| Power BI administrator | Publish and configure the model and reports |
| Installer | Perform the steps in this guide |

## 3. Preparation sheet

Before taking any action, ask the owner to complete the lines required for
Discovery. Complete the additional Azure parameters only when moving to Basic
or Advanced. Keep the sheet in a secure customer location.

| Information | Value to provide |
|---|---|
| Target level | `Discovery`, `Basic`, or `Advanced` |
| Customer name | |
| Lowercase customer code, without spaces | |
| Default language | `fr-CA` or `en-CA` |
| Time zone | Example: `America/Toronto` |
| Microsoft Entra tenant name | |
| Tenant ID | |
| Azure subscription ID for the agent | |
| IDs of subscriptions containing Fabric capacities | |
| Azure resource group name | |
| Azure region | Example: `canadacentral` |
| Azure SRE agent name | |
| Security group name for Fabric Admin APIs | |
| Azure managed identity name | |
| Container Apps environment name | |
| Fabric Admin MCP Container App name | |
| Azure Container Registry name | |
| Fabric workspace name | Default: `Fabric Administration` |
| Lakehouse name | Default: `FabricSRE` |
| Fabric capacity name to use | Advanced only |
| Fabric Capacity Metrics model ID | If CU metrics are enabled |
| Administrator to contact if blocked | |

### Rules for Azure names

Use only names approved by the customer.

- The Azure Container Registry name must be globally unique in Azure and may
  contain only letters and numbers.
- The Container App name must be unique within its environment.
- The customer code may contain only lowercase letters, numbers, and hyphens.
- Do not add a suffix such as `test`, `prod`, or a region without approval.

## 4. Checks before starting

Check every line.

- [ ] The Discovery, Basic, or Advanced level is approved.
- [ ] The sheet lines required for the selected level are complete.
- [ ] The installer is using an individual account, never a shared account.
- [ ] The account can see the correct Microsoft Entra tenant.
- [ ] The account can see the correct Azure subscription.
- [ ] The account can open the Fabric portal.
- [ ] The account can create or open Azure SRE Agent.

For Basic or Advanced only:

- [ ] A Fabric capacity is available for Advanced.
- [ ] The Fabric SRE repository is available on the workstation.
- [ ] A change window has been approved.
- [ ] Someone who can grant permissions is available.

Do not continue if any box remains unchecked.

## 5. Open the required portals

Open each link in a separate tab with the same work account.

1. Azure SRE Agent portal: <https://sre.azure.com>
2. Azure portal: <https://portal.azure.com>
3. Microsoft Fabric portal: <https://app.fabric.microsoft.com>

In each portal:

1. Select the avatar in the upper-right corner.
2. Verify the account address.
3. Verify the organization or tenant name.
4. If the tenant is incorrect, select **Switch directory** and choose the
   tenant provided in the sheet.

> **Checkpoint**
>
> The same customer tenant must be displayed in Azure SRE Agent, Azure, and
> Fabric.

# Part 0 — Discover Azure SRE Agent with Fabric

This part does not yet require the Lakehouse, notebooks, pipeline, Power BI, or
the Basic solution's Fabric Admin MCP service.

## D1. Create the agent from the portal

1. Open <https://sre.azure.com>.
2. Sign in with the approved work account.
3. Select **Create agent**.
4. Under **Subscription**, select the approved subscription.
5. Under **Resource group**, select an existing group or enter the approved
   name for a new group.
6. Under **Agent name**, enter the approved name.
7. Under **Region**, select a supported, approved region.
8. Under **Model provider**, select the provider approved by the customer.
9. Under **Application Insights**, keep the proposed new resource or select the
   approved existing resource.
10. Select **Next**.
11. Verify the subscription, group, name, and region.
12. Select **Create**.
13. Wait for the deployment to show **Succeeded**.
14. Select **Set up your agent**.

Creation normally takes a few minutes. The portal creates the agent, its
managed identities, and the selected monitoring resources.

> **Checkpoint**
>
> The current account must have the **SRE Agent Administrator** role on the new
> agent.

## D2. Add the Fabric connector

Use the Fabric MCP server approved by the organization. Do not invent a URL or
use an unapproved community server.

At <https://sre.azure.com>:

1. Open the agent.
2. Open **Builder**.
3. Select **Connectors**.
4. Select **+ Add connector**.
5. Choose **MCP Server**.
6. Enter the approved Fabric MCP server URL.
7. Choose the authentication method provided by the administrator.
8. Save without placing a secret in the name or description.
9. Wait for the status to change from **Initializing** to **Connected**.
10. Select **Edit** for this connector.
11. Under **MCP Tools**, select only the required Fabric read tools.
12. Select **Save**.

Azure SRE Agent supports up to 80 tools across all connectors. Do not select
every tool by default.

## D3. Test the connection

1. Select **New chat thread**.
2. Send:

```text
Which Microsoft Fabric tools can you use in this conversation? Describe their
scope and identify which ones are read-only.
```

3. Verify that the tool-call cards show **Completed**.
4. Send:

```text
Test the Fabric connection without changing any resource. List the visible
workspaces and clearly state whether this result covers the entire tenant or
only workspaces accessible to your identity.
```

If the call fails, return to **Builder > Connectors** and verify the status,
URL, authentication, and selected tools.

## D4. Start with guided prompts

Use the [prompt catalog](prompts.en.md). For a first session, try these prompts
in order:

```text
Explain in simple terms what you can do for Microsoft Fabric with the tools
currently connected. Also list what you cannot do.
```

```text
Create an executive summary of my visible Fabric environment: number of
capacities, number of workspaces, item count by type, and the main visibility
limitations. Include the collection time.
```

```text
Generate a bar chart of item count by workspace using the visible data. Show
the top ten. If you cannot render the chart, provide a sorted, chart-ready table
and explain why.
```

Charts generated in chat are on-demand results. They do not create a persistent
dashboard, and their filters are not retained between conversations.

## D5. Choose the next step

Remain at Discovery when occasional questions and resources visible to the
identity are sufficient.

Move to **Basic** to:

- obtain read-only tenant-wide inventory;
- add the bilingual Live Report;
- use Capacity Metrics for recent CU when available;
- provide common prompts to all users.

Move to **Advanced** to add durable history, trends, SLOs, a semantic model, and
Power BI reports.

Sections 6 through 13 below prepare Basic and Advanced. They are not required
when remaining at Discovery.

## 6. Record identifiers without guessing

### 6.1 Tenant ID

In the Azure portal:

1. In the top search bar, enter `Microsoft Entra ID`.
2. Select **Microsoft Entra ID**.
3. Under **Overview**, locate **Tenant ID**.
4. Select the copy icon.
5. Compare the value with the preparation sheet.

### 6.2 Subscription ID

In the Azure portal:

1. In the search bar, enter `Subscriptions`.
2. Select **Subscriptions**.
3. Select the subscription provided in the sheet.
4. Under **Overview**, copy **Subscription ID**.
5. Verify that the status is **Active**.

### 6.3 Resource group

Still in the Azure portal:

1. Search for `Resource groups`.
2. Select **Resource groups**.
3. Search for the name provided in the sheet.
4. Open the group and verify the subscription displayed at the top of the page.

If the group does not exist and its creation has been authorized:

1. Select **Create**.
2. Choose the correct subscription.
3. Enter the exact approved name.
4. Choose the approved region.
5. Select **Review + create**, then **Create**.

## 7. Prepare Microsoft Entra and Fabric

This section must be completed by an Entra/Fabric administrator.

### 7.1 Create or verify the security group

In the Azure portal:

1. Search for `Microsoft Entra ID`.
2. In the left menu, select **Groups**.
3. Select **All groups**.
4. Search for the group specified in
   `adminApiSecurityGroupName`.
5. If it exists, open it and confirm that its **Group type** is
   **Security**.

If the group does not exist:

1. Select **New group**.
2. For **Group type**, choose **Security**.
3. Enter the exact name provided in the sheet.
4. For **Membership type**, choose **Assigned**.
5. Do not manually add the Fabric Admin application at this stage: the script
   will do so.
6. Select **Create**.

### 7.2 Allow Fabric public APIs

In the Fabric portal:

1. In the left navigation bar, open **OneLake catalog**.
2. Select **Govern**.
3. Select **Settings**.
4. Select **Tenant settings**.
5. Use the search box and enter
   `Service principals can call Fabric public APIs`.
6. Open the setting.
7. Enable the setting.
8. Choose the option that limits access to specific security groups.
9. Add the group created in step 7.1.
10. Select **Apply**.

### 7.3 Allow read-only admin APIs

On the same **Tenant settings** screen:

1. Search for
   `Service principals can access read-only admin APIs`.
2. Open the setting.
3. Enable the setting.
4. Limit access to the same security group.
5. Select **Apply**.

Do not enable access to update admin APIs for this identity.

### 7.4 Wait for propagation

Tenant settings and group membership can take several minutes to become
effective.

Wait 15 minutes before diagnosing an initial `401` or `403` response.

## 8. Prepare the required Azure resources

### 8.1 Create or verify the managed identity

The deployment script reuses a user-assigned managed identity. It does not
create it.

In the Azure portal:

1. Search for `Managed Identities`.
2. Select **Managed Identities**.
3. Search for the name provided in `managedIdentityName`.
4. If the identity exists, verify its subscription and resource group.

If it does not exist:

1. Select **Create**.
2. Choose the correct subscription.
3. Choose the resource group from the sheet.
4. Choose the approved region.
5. Enter the exact name.
6. Select **Review + create**, then **Create**.

The script will then grant this identity the `AcrPull` role on the registry.

### 8.2 Verify the installer's permissions

In the Azure resource group:

1. Select **Access control (IAM)**.
2. Select **View my access**.
3. Verify that the account has the permissions required to create resources
   and assign a role.

The following are usually required:

- **Contributor** on the resource group;
- **User Access Administrator** or **Owner** to create the `AcrPull`
  assignment;
- the Entra permissions required to create an application and a secret;
- the permissions required to add a member to the security group.

If any of these permissions is missing, stop and contact the Azure
administrator.

## 9. Prepare the installation workstation

### 9.1 Required software

Install:

- Visual Studio Code;
- PowerShell 7;
- Azure CLI;
- Python 3.11 or later;
- Node.js 22;
- Power BI Desktop for Advanced.

To confirm the installations:

1. Open Visual Studio Code.
2. Select **File** > **Open Folder**.
3. Select the root `Azure SRE` folder.
4. Select **Terminal** > **New Terminal**.
5. Verify that the terminal indicates `PowerShell`.
6. Copy and paste the following commands, one line at a time:

```powershell
pwsh --version
az version
python --version
node --version
```

Expected results:

- PowerShell returns version 7;
- Azure CLI returns its version numbers;
- Python returns at least `3.11`;
- Node returns version 22.

If a command displays "not found" or "not recognized," install or repair the
affected software before continuing.

### 9.2 Install project dependencies

In the Visual Studio Code terminal opened at the project root:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
npm install -g @microsoft/powerbi-report-authoring-cli@latest
az extension add --name containerapp --upgrade
```

Wait for the prompt to return after each command.

> **Checkpoint**
>
> No command should end with a red error message. Update warnings are not
> necessarily blocking.

## 10. Sign in to the correct Azure environment

In the terminal:

```powershell
az login --tenant "<ID-DU-TENANT>"
```

1. A sign-in page opens.
2. Sign in with the approved work account.
3. Return to Visual Studio Code.
4. Select the agent subscription:

```powershell
az account set --subscription "<ID-ABONNEMENT-AGENT>"
az account show --output table
```

Compare the displayed subscription name, tenant ID, and account with the
preparation sheet.

If any value differs, do not run any script.

## 11. Create the customer configuration file

### 11.1 Copy the template

In the terminal:

```powershell
Copy-Item .\config\client.parameters.example.yaml `
  .\config\client.parameters.yaml
```

In the Visual Studio Code Explorer:

1. Expand the `config` folder.
2. Select `client.parameters.yaml`.
3. Replace the example values with the approved values.

### 11.2 Required values

| Field | Expected value |
|---|---|
| `client.code` | Short lowercase code, without spaces |
| `client.displayName` | Readable customer name |
| `client.defaultLanguage` | `fr-CA` or `en-CA` |
| `client.timeZone` | IANA time zone, for example `America/Toronto` |
| `azure.tenantId` | Tenant ID |
| `azure.subscriptionIds` | List of subscriptions containing capacities |
| `foundry.subscriptionId` | Agent subscription |
| `foundry.resourceGroup` | Agent resource group |
| `foundry.agentName` | Exact agent name |
| `foundry.fabricAdminMcp.appName` | Container App name |
| `foundry.fabricAdminMcp.environmentName` | Container Apps environment name |
| `foundry.fabricAdminMcp.managedIdentityName` | Identity created in step 8 |
| `foundry.fabricAdminMcp.registryName` | Unique ACR name |
| `foundry.fabricAdminMcp.servicePrincipalDisplayName` | Name of the Entra application to create |
| `foundry.fabricAdminMcp.adminApiSecurityGroupName` | Group created in step 7 |
| `foundry.fabricAdminMcp.location` | Azure region, without spaces |
| `fabric.capacityScope.includeIds` | Included capacities, or `[]` according to the customer decision |
| `fabric.capacityScope.excludeIds` | Excluded capacities |
| `fabric.capacityMetrics.semanticModelId` | Capacity Metrics model ID, or empty |

Do not add a password or API key to this file.

### 11.3 Environment variables

In the active terminal:

```powershell
$env:AZURE_TENANT_ID = "<ID-DU-TENANT>"
$env:AZURE_SUBSCRIPTION_ID = "<ID-ABONNEMENT>"
$env:AZURE_FOUNDRY_SUBSCRIPTION_ID = "<ID-ABONNEMENT-AGENT>"
$env:FOUNDRY_RESOURCE_GROUP = "<GROUPE-DE-RESSOURCES>"
$env:FOUNDRY_AGENT_NAME = "<NOM-DE-L-AGENT>"
$env:AZURE_LOCATION = "<REGION-AZURE>"
```

These values remain active only in the current terminal. If the terminal is
closed, define them again.

### 11.4 Verify the file

In the terminal:

```powershell
$env:PYTHONPATH = ".\src"
python -c "from fabric_sre.config import load_config; load_config(r'.\config\client.parameters.yaml', r'.\config\client.parameters.schema.json'); print('Configuration valide')"
```

Expected result:

```text
Configuration valide
```

Correct every reported error before continuing.

## 12. Validate the package

Still at the project root:

```powershell
.\scripts\validate.ps1
```

The command runs the tests, checks the code, and validates both reports.

Expected result at the end:

```text
Fabric SRE validation succeeded.
```

If validation fails:

1. Do not start the deployment.
2. Copy only the error message, without any secret.
3. Have the technical team correct the package.
4. Restart validation from the beginning.

## 13. Verify the target agent

In the terminal:

```powershell
.\scripts\preflight-agent.ps1 `
  -SubscriptionId "<ID-ABONNEMENT-AGENT>" `
  -ResourceGroup "<GROUPE-DE-RESSOURCES>" `
  -AgentName "<NOM-DE-L-AGENT>" `
  -ExpectedAccount "<COMPTE-PROFESSIONNEL>"
```

The result must display a resource matching the agent name.

If the script reports that the subscription or agent is not visible, do not
continue.

# Part A — Basic installation

Basic reuses the agent and Fabric connector already tested during Discovery. It
adds Fabric Admin MCP, the Live Report, and common prompts; do not create a
second agent.

### Prompt-assisted administration alternative

An administrator can automate part of Basic from a client that supports Azure
MCP Server, such as VS Code or GitHub Copilot CLI. Azure MCP Server exposes
tools that can create or update:

- an MCP connector on an Azure SRE Agent resource;
- reusable common prompts for users.

Example administration intents:

```text
Create or update an HTTP MCP connector named "FabricAdmin" on agent
"<AGENT-NAME>" using the approved Fabric Admin MCP endpoint.
```

```text
Create a common prompt named "fabric-basic-overview" on agent "<AGENT-NAME>"
using the approved Basic summary prompt content.
```

This alternative reduces portal steps but does not perform the full
installation:

- it must run from a client that has Azure MCP Server, not as an ordinary
  prompt in the agent's own chat;
- the Fabric Admin MCP endpoint must already be deployed;
- the account must have permission to modify Azure SRE Agent;
- no API key may be written in clear text in the prompt;
- the Live Report must still be imported or published as a persistent asset.

For a first deployment, or when secure secret storage is not already
configured, follow the portal steps below.

## 14. Deploy Fabric Admin MCP

In the terminal:

```powershell
.\scripts\deploy-fabric-admin-mcp.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml
```

This operation may take several minutes. The script:

1. creates or reuses the read-only Entra application;
2. creates its service principal;
3. adds this principal to the group authorized in Fabric;
4. creates an application secret valid for one year;
5. creates or reuses the Container Apps environment;
6. creates the Azure Container Registry if it does not exist;
7. builds the service image;
8. assigns `AcrPull` to the managed identity;
9. creates or updates the Container App;
10. stores the secrets in Container Apps.

At the end, a JSON block is displayed. It must contain:

- `endpoint` with an address ending in `/mcp`;
- `health` with an address ending in `/health`;
- `apiKeyConfigured` with the value `true`;
- `apiKeyHeader` with the value `x-api-key`.

Copy only the `endpoint` and `health` URLs into the deployment sheet. Do not
copy any secret.

### 14.1 Verify the resource in Azure

In the Azure portal:

1. Open the resource group.
2. Verify that the following resources are present:
   - a **Container App**;
   - a **Container Apps environment**;
   - an **Azure Container Registry**;
   - the **managed identity**.
3. Select the Container App.
4. Under **Overview**, verify that its status is **Running**.
5. Under **Revisions and replicas**, verify that one revision is active and at
   least one replica is ready.

### 14.2 Test the health page

Copy the `health` URL into a browser.

Expected result:

```json
{"status":"ok"}
```

If the page does not respond:

1. In the Container App, select **Logs** or **Log stream**.
2. Look for a startup error.
3. Do not recreate the resource manually.
4. Have the technical team analyze the error.

## 15. Retrieve the connector key securely

The key is stored as a Container App secret. Display it only when the connector
configuration screen is ready.

In the Azure portal:

1. Open the Container App.
2. In the left menu, open **Secrets**.
3. Locate `mcp-api-key`.
4. Select the action that displays or copies its value.
5. Immediately paste the value into the connector's secret field.
6. Do not save the value in a local file.

If the portal cannot read the value, ask an Azure administrator to retrieve it
securely. Do not generate a second key without a rotation procedure.

## 16. Add the FabricAdmin connector to the agent

The exact screens depend on the version of the Azure SRE interface used by the
customer. The connector must support a remote MCP server with a custom header.
If the interface does not offer these options, stop and ask the Azure SRE
administrator; do not replace authentication with "none."

In the Azure SRE administration interface:

1. Open the project specified in the sheet.
2. Open the target agent.
3. Open **Tools** or **Connectors**.
4. Select **Add**.
5. Choose **MCP**.
6. For transport, choose **Streamable HTTP**.
7. For the name, enter `FabricAdmin`.
8. For the URL, paste the `endpoint` value ending in `/mcp`.
9. For authentication, choose **Custom header**.
10. For the header name, enter exactly `x-api-key`.
11. For the value, paste the key retrieved in step 15.
12. Save.
13. Wait until the connection is shown as available.
14. Enable only these tools:
    - `list_workspaces`;
    - `list_items`;
    - `get_cu_metrics` if the Capacity Metrics ID was provided.

The names visible to the agent must be:

- `FabricAdmin_list_workspaces`;
- `FabricAdmin_list_items`;
- `FabricAdmin_get_cu_metrics`, if enabled.

## 17. Verify the Fabric Core connector

On the same screen:

1. Open the connector named `FabricSRE`.
2. Confirm that it points to Fabric Core MCP.
3. Do not add the Fabric Admin tools a second time.
4. Save without changing permissions if the connector is already working.

Fabric Core is used for resources visible to the identity. Fabric Admin is used
for read-only tenant-wide inventory.

## 18. Update the agent configuration

In the Azure SRE interface:

1. Open the `meta_agent` agent configuration.
2. Choose **Import**, **Upload**, or **Edit configuration**, depending on the
   interface.
3. Select the file
   `agent\azure-sre-agent.yaml`.
4. Verify that the name remains `meta_agent`.
5. Verify that the `FabricAdmin_*` and `FabricSRE_*` tools are each listed only
   once.
6. Save.
7. Publish a new version if the interface distinguishes between **Save** and
   **Publish**.

Do not enable any write tool not described in the file.

## 19. Add the routines

If the Azure SRE environment supports importing routines:

1. Open **Routines** or **Schedules**.
2. Select **Import**.
3. Select `agent\routines.yaml`.
4. Verify the time zone.
5. Leave the routines disabled until testing is complete.
6. Save.

If import is unavailable, give the file to the Azure SRE administrator. Do not
recreate scheduling expressions by guesswork.

## 20. Publish the Live Report

In the Azure SRE interface:

1. Open **Live Reports** or **Reports**.
2. Select the latest approved bilingual asset. The validated reference is
   service version 39, but its number can change after import.
3. Link the report to the `meta_agent` agent.
4. Verify that `FabricSRE` for capacities and all three `FabricAdmin` tools are
   offered as sources.
5. Publish.
6. Open the published report.
7. Switch from FR to EN and then back to FR.
8. Verify that the filters remain applied.
9. Run the complete acceptance procedure in the
   [Live Report specification](live-report.en.md), including French
   workspace/item terminology, the cumulative CU-h/CU-s toggle, CU
   calculations, the glossary, contextual titles, and non-overlapping bars.

If no Live Report asset is provided in the environment, stop this step and ask
the solution owner which asset to publish.

For Advanced, recommend a small Fabric capacity dedicated to the SRE
administration workspace. It hosts the Lakehouse, notebooks, pipeline, model,
and reports, but not Azure SRE Agent or Fabric Admin MCP. Degraded behavior and
recovery are documented in
[Stopped Fabric capacity](live-report.en.md#5-stopped-fabric-capacity).

## 21. Basic acceptance testing

In the agent test area, send the following requests:

1. `Give me the health status of the Fabric Admin service.`
2. `List the tenant's non-personal Fabric workspaces.`
3. `List the items in workspace <known name>.`
4. If Capacity Metrics is configured:
   `Summarize CU consumption for the last 7 days.`

Verify:

- [ ] health returns `ok`;
- [ ] the inventory contains the expected workspaces;
- [ ] the agent distinguishes missing data from a zero value;
- [ ] the period actually available is stated;
- [ ] no write action is offered without approval;
- [ ] no secret appears in the response or logs.

Enable the routines only after these checks pass.

If only the Basic edition is requested, go directly to
[Deployment closeout](#34-deployment-closeout).

# Part B — Advanced installation

Advanced requires a successful Basic installation.

## 22. Preview workspace creation

In the Visual Studio Code terminal:

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -WhatIf
```

Read the result. No resource may be created with `-WhatIf`.

Verify the workspace and Lakehouse names. If they are incorrect, modify
`config\client.parameters.yaml`, revalidate the file, and then run the preview
again.

## 23. Create or locate the workspace and Lakehouse

In the terminal:

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -CreateWorkspace
```

The script displays a JSON plan and the identifiers it found. It does not
upload files or publish reports.

In the Fabric portal:

1. Select **Workspaces** in the left navigation.
2. Search for the configured name, `Fabric Administration` by default.
3. Open the workspace.
4. Verify that a Lakehouse named `FabricSRE` is present.

If several workspaces have this name, stop and ask the administrator to resolve
the ambiguity.

## 24. Assign the workspace to a capacity

In the Fabric workspace:

1. Select **Workspace settings**.
2. Open **Workspace type**.
3. Select **Edit**.
4. Choose a Fabric workspace type.
5. Select exactly the capacity specified in the sheet.
6. Select **Apply**.
7. Wait for confirmation.

> **Checkpoint**
>
> The displayed capacity name must exactly match the approved name. A trial
> capacity must not be used for production.

## 25. Create the workspace identity

Under **Workspace settings**:

1. Open **Workspace identity**.
2. Select **Create identity**.
3. Confirm.
4. Wait until the status shows that the identity is ready.
5. Copy the identity name into the deployment sheet.

Then:

1. Return to the workspace.
2. Select **Manage access**.
3. Add the identity used for collection or automation.
4. Assign **Contributor** only if this identity must run and modify the
   notebooks and pipeline.
5. Grant only **Read** and **Build** to identities that consume the model.

Do not assign **Contributor** to the agent's read identity.

## 26. Upload files to the Lakehouse

### 26.1 Expected folder structure

The result must be:

```text
Files/
└── fabric-sre/
    ├── config/
    │   ├── client.parameters.yaml
    │   └── client.parameters.schema.json
    ├── src/
    │   └── fabric_sre/
    │       └── Python package files
    └── queries/
        └── capacity-metrics/
            ├── silver_item_cu.dax
            └── silver_storage.dax
```

The `client.parameters.schema.json` file is required: the notebooks use it to
validate the configuration.

### 26.2 Create the folders

In the Fabric portal:

1. Open the `FabricSRE` Lakehouse.
2. In the Lakehouse explorer, open **Files**.
3. Select the three dots `...` next to **Files**.
4. Choose **New subfolder**.
5. Create `fabric-sre`.
6. In `fabric-sre`, create `config`, `src`, and `queries`.
7. In `src`, create `fabric_sre`.
8. In `queries`, create `capacity-metrics`.

### 26.3 Upload the files

For each folder:

1. Open the target folder in the Lakehouse.
2. Select **Upload**.
3. Choose **Upload files**.
4. Select the files from the corresponding local folder.
5. Wait for the upload to complete.
6. Verify that every name is visible.

Do not upload the entire repository, and do not upload `.git`,
`client.parameters.example.yaml`, caches, or tests.

## 27. Create the six notebooks

The files in the local `notebooks` folder are source files, not exported Fabric
notebooks. For this project version, create the notebooks in the portal and
copy their contents.

### 27.1 Common procedure

For each notebook:

1. Open the `Fabric Administration` workspace.
2. Select **+ New item**.
3. Search for `Notebook`.
4. Select **Notebook**.
5. Rename the notebook with the exact name shown below, without an extension.
6. In the notebook explorer, select **Add Lakehouse**.
7. Choose **Existing Lakehouse**.
8. Select `FabricSRE`.
9. Confirm that `FabricSRE` is the default Lakehouse.
10. Open the corresponding source file in Visual Studio Code.
11. Copy all of its contents.
12. Paste the contents into the notebook's first cell.
13. Save the notebook.

### 27.2 Python notebooks

Create:

| Fabric notebook name | Local source file | Cell language |
|---|---|---|
| `01_collect_inventory` | `notebooks\01_collect_inventory.py` | PySpark (Python) |
| `02_collect_activity_events` | `notebooks\02_collect_activity_events.py` | PySpark (Python) |
| `03_collect_capacity_metrics` | `notebooks\03_collect_capacity_metrics.py` | PySpark (Python) |

### 27.3 SQL notebooks

Create:

| Fabric notebook name | Local source file | Cell language |
|---|---|---|
| `00_bootstrap_lakehouse` | `notebooks\00_bootstrap_lakehouse.sql` | Spark SQL |
| `04_normalize_inventory` | `notebooks\04_normalize_inventory.sql` | Spark SQL |
| `05_build_gold` | `notebooks\05_build_gold.sql` | Spark SQL |

To change a cell's language:

1. Select inside the cell.
2. Open the language list in the cell toolbar.
3. Choose **Spark SQL**.

Do not choose the Lakehouse SQL endpoint: these queries create Delta tables
and must run through Spark.

## 28. Run the bootstrap

1. Open `00_bootstrap_lakehouse`.
2. Confirm that the `FabricSRE` Lakehouse is attached.
3. Select **Run all**.
4. Wait for the green check mark.
5. Return to the Lakehouse.
6. Under **Tables**, select **Refresh**.

The Bronze, Silver, and `collection_run` tables must appear.

If the notebook fails, do not continue with the other notebooks.

## 29. Create the daily pipeline

The file
`pipelines\daily-collection.pipeline.template.json` describes the expected
pipeline, but is not a Fabric export that can be imported directly. Create the
pipeline in the interface.

### 29.1 Create the pipeline

1. In the workspace, select **+ New item**.
2. Search for **Data pipeline**.
3. Select **Data pipeline**.
4. Enter `pl_fabric_sre_daily`.
5. Select **Create**.

### 29.2 Add a Notebook activity

For each row in the following table:

1. In the **Activities** pane, search for **Notebook**.
2. Drag **Notebook** onto the canvas.
3. Select the activity.
4. On the **General** tab, enter the activity name.
5. On the **Settings** tab, choose **Workspace identity** authentication if it
   is offered and approved.
6. Under **Notebook**, select the specified notebook.

| Activity | Notebook |
|---|---|
| `Bootstrap Lakehouse` | `00_bootstrap_lakehouse` |
| `Collect Inventory` | `01_collect_inventory` |
| `Collect Activity` | `02_collect_activity_events` |
| `Collect Capacity Metrics` | `03_collect_capacity_metrics` |
| `Normalize Inventory` | `04_normalize_inventory` |
| `Build Gold` | `05_build_gold` |

### 29.3 Connect the activities

Use the green **Succeeded** dependency:

1. `Bootstrap Lakehouse` to `Collect Inventory`;
2. `Bootstrap Lakehouse` to `Collect Activity`;
3. `Bootstrap Lakehouse` to `Collect Capacity Metrics`;
4. `Collect Inventory` to `Normalize Inventory`;
5. `Normalize Inventory` to `Build Gold`;
6. `Collect Activity` to `Build Gold`;
7. `Collect Capacity Metrics` to `Build Gold`.

The pipeline must form three branches after the bootstrap and then join at
`Build Gold`.

### 29.4 Configure retries

For each activity:

1. Select the activity.
2. Open the general settings or execution policy.
3. Set **Retry** to `3`.
4. Set the interval to `120` seconds.
5. Set the maximum timeout to `2` hours when this field is available.

### 29.5 Save

On the pipeline's **Home** tab:

1. Select **Save**.
2. Wait for confirmation.

## 30. Test the pipeline

1. In the pipeline, select **Run**.
2. Confirm the run.
3. Open the **Output** tab below the canvas.
4. Wait for all activities to finish.
5. Select each activity to view its result.

All activities must be green.

Then, in the Lakehouse:

1. Refresh **Tables**.
2. Verify that tables beginning with `bronze_`, `silver_`, and `gold_` are
   present.
3. Open `gold_capacity_daily`.
4. Verify that it contains rows if Capacity Metrics is enabled and available.
5. Open `gold_item_daily`.
6. Verify that the expected identifiers are not empty.

A pipeline shown as successful with empty Gold tables does not constitute
successful acceptance testing.

## 31. Schedule the pipeline

In the pipeline editor:

1. Select **Home**.
2. Select **Schedule**.
3. Select **Add schedule** if necessary.
4. Choose a **Daily** frequency.
5. Set the approved local time, `01:00` by default.
6. Verify the time zone.
7. Enable the schedule.
8. Save.

In the run history, confirm that the next occurrence is displayed.

## 32. Publish the Power BI model and reports

### 32.1 Retrieve the Lakehouse SQL server

In the Fabric portal:

1. Open the `FabricSRE` Lakehouse.
2. Open **SQL analytics endpoint**.
3. Open the settings or the action for copying the connection string.
4. Copy the server name ending in
   `.datawarehouse.fabric.microsoft.com`.
5. Record `FabricSRE` as the database name, unless the Lakehouse was renamed.

### 32.2 Open the French project

On the workstation:

1. In Windows Explorer, open
   `powerbi\FabricSRE\fr`.
2. Double-click `FabricSRE-fr.pbip`.
3. Wait for Power BI Desktop to open.
4. If Power BI asks you to enable the PBIP feature, accept and then restart
   Power BI Desktop.

### 32.3 Change the parameters

In Power BI Desktop:

1. On the **Home** ribbon, select **Transform data**.
2. Select **Edit parameters**.
3. For `Server`, paste the SQL server recorded in step 32.1.
4. For `Database`, enter the Lakehouse name.
5. Confirm.
6. Select **Refresh**.
7. Authenticate with the work account if prompted.
8. Verify that no data source error is displayed.
9. Save the project.

### 32.4 Publish in French

1. On the **Home** ribbon, select **Publish**.
2. Choose the `Fabric Administration` workspace.
3. Confirm.
4. Wait for the success message.

### 32.5 Publish in English

1. Close the French project.
2. Open
   `powerbi\FabricSRE\en\FabricSRE-en.pbip`.
3. Verify the `Server` and `Database` parameters.
4. Refresh.
5. Publish to the same workspace.

In the workspace, verify the presence of:

- the `Fabric SRE` semantic model;
- the French report;
- the English report.

If Power BI offers to replace an existing model, verify that the target model
is `Fabric SRE` in the administration workspace before accepting.

### 32.6 Configure the cloud connection

In the Fabric portal:

1. In the workspace, locate the `Fabric SRE` semantic model.
2. Select the three dots `...`.
3. Select **Settings**.
4. Open **Gateway and cloud connections**.
5. Under **Cloud connections**, open **Maps to**.
6. Choose **Create a connection**.
7. Select **Workspace identity** authentication if it is available.
8. Select the `Fabric Administration` workspace identity.
9. Save.

### 32.7 Refresh the model

1. Return to the semantic model.
2. Select the three dots `...`.
3. Select **Refresh now**.
4. Open **Refresh history**.
5. Verify that the final status is **Completed**.

### 32.8 Verify the reports

Open both reports.

Verify:

- [ ] the pages open without error;
- [ ] the cards and charts contain data;
- [ ] the French and English totals match;
- [ ] the freshness date is consistent with the latest collection;
- [ ] the filters use the same periods;
- [ ] no sensitive technical identifier is exposed unnecessarily.

## 33. Advanced acceptance testing

All Basic checks must already have passed.

Then verify:

- [ ] the workspace is on the approved capacity;
- [ ] the workspace identity is active;
- [ ] the files are present under `Files/fabric-sre`;
- [ ] all six notebooks are attached to the Lakehouse;
- [ ] the bootstrap creates the expected tables;
- [ ] a complete pipeline run succeeds;
- [ ] the Bronze tables contain the raw collection;
- [ ] the Silver tables contain normalized data;
- [ ] the Gold tables contain usable rows;
- [ ] the daily schedule is active;
- [ ] the semantic model refreshes;
- [ ] both reports display the same totals;
- [ ] the agent uses Gold for history and direct tools for real-time data;
- [ ] no write action runs without human approval.

# Closeout and operations

## 34. Deployment closeout

Record, without secrets:

- the installed edition;
- the date and time;
- the installer's individual account;
- resource names;
- portal and health URLs;
- the schedule time;
- acceptance test results;
- resolved errors;
- remaining actions and their owner.

Do not record:

- the `x-api-key` value;
- the Entra application secret;
- Azure tokens;
- connection strings containing a secret.

## 35. Secure the environment after installation

1. Verify that `config\client.parameters.yaml` is not added to Git.
2. Close the terminal containing the environment variables.
3. Close every window displaying a secret.
4. Verify the expiration date of the Entra application secret.
5. Create a rotation reminder for before one year.
6. Verify that the Container App keeps at least one replica if the customer
   requires responses without a cold start.
7. Verify that read identities do not have the Contributor role.

## 36. Daily monitoring

In Fabric:

1. Open the workspace.
2. Open the `pl_fabric_sre_daily` pipeline.
3. Open the history.
4. Confirm that the latest run succeeded.
5. Verify the most recent date in the Gold tables.

In Azure:

1. Open the Container App.
2. Verify that the active revision is healthy.
3. Review the logs if responses are slow or an error occurs.

In Power BI:

1. Open the model refresh history.
2. Verify the latest refresh.
3. Open both reports after every model change.

## 37. Guided troubleshooting

### The script cannot see the subscription

1. Run `az account show --output table`.
2. Compare the subscription and tenant with the sheet.
3. Run `az login --tenant "<ID-DU-TENANT>"` again.
4. Run `az account set --subscription "<ID-ABONNEMENT>"` again.

### The script cannot find the managed identity

1. Open **Managed Identities** in Azure.
2. Verify the name, resource group, and subscription.
3. Correct the configuration or create the missing identity.
4. Do not replace the name with the client ID.

### Fabric Admin returns 401 or 403

1. Verify both Fabric tenant settings.
2. Verify that the correct security group is selected.
3. In Entra, open the group and verify that the Fabric Admin service principal
   is a member.
4. Wait for propagation.
5. Do not grant Contributor on every workspace to bypass the error.

### The `/health` page does not respond

1. Open the Container App.
2. Verify the active revision.
3. Verify that a replica is ready.
4. Open the log stream.
5. Have the startup error analyzed.

### The notebook cannot find `fabric_sre`

1. Open the Lakehouse.
2. Verify
   `Files/fabric-sre/src/fabric_sre`.
3. Verify that the package's Python files are directly in this folder.
4. Do not add another `src` folder level.

### The notebook cannot find the configuration

Verify the exact presence of:

```text
Files/fabric-sre/config/client.parameters.yaml
Files/fabric-sre/config/client.parameters.schema.json
```

### Capacity Metrics is empty

1. Verify that `collectCapacityMetrics` is `true`.
2. Verify `fabric.capacityMetrics.semanticModelId`.
3. Verify **Read** and **Build** permissions on the Capacity Metrics model.
4. Verify that the Capacity Metrics app has refreshed.
5. Do not interpret missing data as zero CU.

### The pipeline succeeds but Gold is empty

1. Open the result of each notebook.
2. Verify the number of rows collected.
3. Verify the Silver tables.
4. Verify the DAX queries under
   `Files/fabric-sre/queries/capacity-metrics`.
5. Escalate to the technical team with the activity name and run time.

### Power BI refresh fails

1. Verify `Server` and `Database`.
2. Verify the model's cloud connection.
3. Verify the workspace identity.
4. Verify this identity's permissions.
5. Open the error details in the refresh history.

### A 429 message appears

The service has requested that calls be slowed down.

1. Do not immediately run the operation again several times.
2. Let the retry policy honor `Retry-After`.
3. Verify that only one daily schedule is active.

## 38. Rollback

### Basic

To disable Basic without deleting resources:

1. Disable the routines.
2. Remove the `FabricAdmin` connector from the agent.
3. Retain the logs required for auditing.
4. Stop the Container App only after the owner approves.

### Advanced

To disable Advanced without losing data:

1. Disable the pipeline schedule.
2. Disable model refreshes.
3. Export the data required for auditing.
4. Remove links to the reports.
5. Return to Basic operation.

Never delete the workspace to resolve a pipeline problem.

## 39. Official Microsoft documentation

- [Create and set up Azure SRE Agent](https://learn.microsoft.com/azure/sre-agent/create-and-set-up)
- [Set up an MCP connector in Azure SRE Agent](https://learn.microsoft.com/azure/sre-agent/mcp-connector)
- [Manage Azure SRE Agent with Azure MCP Server](https://learn.microsoft.com/azure/developer/azure-mcp-server/tools/azure-sre-agent)
- [Create a Fabric workspace](https://learn.microsoft.com/fabric/fundamentals/create-workspaces)
- [Create a Lakehouse](https://learn.microsoft.com/fabric/data-engineering/create-lakehouse)
- [Use Fabric notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)
- [Add a Notebook activity to a pipeline](https://learn.microsoft.com/fabric/data-factory/notebook-activity)
- [Fabric admin API settings](https://learn.microsoft.com/fabric/admin/service-admin-portal-admin-api-settings)
- [Enable a service principal for admin APIs](https://learn.microsoft.com/fabric/admin/enable-service-principal-admin-apis)
- [Power BI Desktop PBIP projects](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- [Configure a Power BI cloud connection](https://learn.microsoft.com/power-bi/connect-data/service-connect-cloud-data-sources)
- [Workspace identity authentication](https://learn.microsoft.com/fabric/security/workspace-identity-authenticate)
