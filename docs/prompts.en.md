# Getting-started prompts for Azure SRE Agent and Microsoft Fabric

This catalog helps users who are new to Azure SRE Agent explore Microsoft
Fabric progressively after connecting a Fabric MCP server to the agent.

The prompts on this page:

- query only the tools the agent can actually access;
- ask the agent to state its scope and data freshness;
- do not replace the Basic or Advanced installation;
- do not create a persistent report unless a dedicated publishing tool has
  been added to the agent.

## 1. First contact with the agent

```text
Explain in simple terms what you can do for Microsoft Fabric with the tools
currently connected. Also list what you cannot do.
```

```text
Which Fabric connectors and tools can you use in this conversation? For each
tool, state whether it is read-only and describe its scope.
```

```text
Test the Fabric connection without changing any resource. Give the result of
each call and explain any authorization error.
```

## 2. Discover the visible scope

```text
List the Fabric capacities, workspaces, and item types you can see. Start by
stating whether the result covers the whole tenant or only workspaces accessible
to your identity. Do not invent missing data.
```

```text
Create an executive summary of my visible Fabric environment: number of
capacities, number of workspaces, item count by type, and the main visibility
limitations. Include the collection time.
```

```text
Which workspaces appear most important to review first? Rank them by item count
and explain the limitations of this ranking.
```

With the Fabric Core connector alone, results are limited to resources visible
to the identity. Do not present this result as an exhaustive tenant inventory.

## 3. Examine a workspace

```text
Analyze the "<WORKSPACE-NAME>" workspace. List its items by type, flag duplicate
names, and propose three useful administrative checks. Remain read-only.
```

```text
In the "<WORKSPACE-NAME>" workspace, which reports, semantic models,
Lakehouses, Warehouses, notebooks, and pipelines are visible? Present the
result as a table.
```

```text
Compare the "<WORKSPACE-A>" and "<WORKSPACE-B>" workspaces by visible item
type. Explicitly identify any data you cannot retrieve.
```

## 4. Capacity and consumption

These prompts require an accessible Capacity Metrics source.

```text
Summarize the available CU consumption for the last seven days. Distinguish
total CU-seconds, sustained average, and peak. State the period actually
available and never convert missing data to zero.
```

```text
Which capacities and items consume the most CU over the available period?
Provide the top five, their contribution, and the source limitations.
```

```text
Look for signs of saturation or throttling in the available data. Separate
observations, hypotheses, and recommendations.
```

Without Advanced, the Capacity Metrics Compute window is normally limited to
about 14 days. A prompt requesting 30 or 60 days cannot recreate expired data.

## 5. Governance and hygiene

```text
Based on visible metadata, identify workspaces or items that deserve a
governance review: ambiguous name, apparent duplicate, owner not visible,
missing certification, or potentially inactive content. Do not conclude that
something is anomalous when the data is unavailable.
```

```text
Prepare ten governance questions to ask Fabric administrators based on the
visible inventory. Rank them by impact.
```

```text
Create a weekly Fabric review checklist based only on signals you can actually
read.
```

## 6. Generate on-demand visuals

Azure SRE Agent can produce visualizations in the conversation when the
experience and returned data support them. These visuals are dynamic and do not
replace a published Live Report.

```text
Generate a bar chart of item count by workspace using the visible data. Show
the top ten. If you cannot render the chart, provide a sorted, chart-ready table
and explain why.
```

```text
Generate a chart showing the distribution of items by type. Include the scope,
date, and number of unknown values. If a pie chart would be hard to read, use
horizontal bars.
```

```text
If CU data is available, chart the daily CU trend for the period actually
available. Do not extend the series artificially. Add a short interpretation
below the chart.
```

```text
Create a summary view with four indicators: visible capacities, visible
workspaces, visible items, and data freshness. Then add a chart of the ten
workspaces with the most items. If visual cards are not supported, use a
Markdown table.
```

Layouts, filters, and visuals generated in a conversation are not guaranteed
across sessions. Install Basic for a stable Live Report, or Advanced for Power
BI reports and durable history.

## 7. Prepare for Basic

```text
Assess whether my agent is ready for Fabric SRE Basic. Check the connected
Fabric tools, current scope, Capacity Metrics availability, and missing
permissions. Do not change anything.
```

```text
Explain the difference between my current experience and Fabric SRE Basic:
tenant inventory, Fabric Admin MCP, bilingual Live Report, and Capacity
Metrics. Provide an installation checklist without displaying any secret.
```

```text
After Basic installation, verify that FabricAdmin_list_workspaces,
FabricAdmin_list_items, and, when configured, FabricAdmin_get_cu_metrics are
available. Compare the Fabric Admin scope with the Fabric Core scope.
```

## 8. Prepare for Advanced

```text
Assess whether we need Fabric SRE Advanced. Base the recommendation on the need
for more than 14 days of history, trends, SLOs, cost, Power BI reports, and data
retention. Separate confirmed requirements from assumptions.
```

```text
Prepare an Advanced prerequisite checklist: Azure subscription, Fabric
capacity, administration workspace, workspace identity, Lakehouse, notebooks,
pipeline, semantic model, and reports. Do not create any resource.
```

```text
Explain to a non-technical decision maker what Advanced adds to Basic, the
additional operating costs, and the maintenance responsibilities.
```

## 9. Prompts to avoid

Avoid ambiguous requests such as:

```text
Optimize all of Fabric.
```

```text
Fix the capacities.
```

```text
Create and publish the dashboard.
```

Prefer a request that specifies:

- the scope;
- the period;
- the desired source;
- the expected format;
- the requirement to remain read-only;
- what to do when data is missing.
