# Fabric SRE Accelerator

Reusable solution that retains Microsoft Fabric administration data, feeds
version-controlled PBIP/TMDL Power BI reports, and enriches a `fabricsre` agent
with analysis, anomaly detection, and human-approved actions.

## Contents

- `config/`: client parameters with no hard-coded customer IDs;
- `notebooks/` and `pipelines/`: daily collection into Delta;
- `src/fabric_sre/`: REST clients, 429 handling, and approval guard;
- `agent/`: FR/EN instructions, subagents, and routines;
- `powerbi/FabricSRE/`: shared TMDL model and separate FR/EN reports;
- `docs/`: architecture, permissions, deployment, customization, and tests.

## Progressive quick start

Start without selecting an edition immediately:

1. **Discovery**: create Azure SRE Agent in the portal, connect Fabric Core MCP,
   then ask questions and generate on-demand visuals;
2. **Basic**: add Fabric Admin tenant inventory, the bilingual Live Report, and
   optionally recent CU, without a technical Fabric workspace;
3. **Advanced**: add the `Fabric Administration` workspace, Lakehouse, at least
   60 days of history, semantic model, and Power BI reports.

Read the [deployment guide](docs/deployment.en.md) before installation.
For a detailed procedure suitable for a non-technical audience, follow the
[step-by-step deployment guide](docs/deployment-step-by-step.en.md).
Use the [prompt catalog](docs/prompts.en.md) to start exploring Fabric as soon
as the first connector is operational.
The [Live Report specification](docs/live-report.en.md) defines the functional
release to publish, its acceptance procedure, and its behavior when a capacity
is stopped.

1. Create the agent at <https://sre.azure.com>.
2. Add the Fabric connector under **Builder > Connectors**.
3. Test the Discovery prompts.
4. To install Basic or Advanced, copy `config/client.parameters.example.yaml` to
   `config/client.parameters.yaml` and set client values.
5. Set `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID`.
6. Run `scripts/validate.ps1`.
7. Read `docs/solution.en.md`.
8. For Advanced only, run `scripts/deploy.ps1 -WhatIf`.
9. Open `powerbi/FabricSRE/en/FabricSRE-en.pbip` for the English report.

The preflight script fails explicitly when the active account cannot see the
target subscription, preventing deployment to the wrong environment.
