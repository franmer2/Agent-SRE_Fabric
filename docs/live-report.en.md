# Fabric monitoring Live Report

This document is the functional reference specification for the
**Fabric Capacity Monitoring** Live Report integrated with Azure SRE Agent. It
complements the [deployment guide](deployment.en.md) and the
[step-by-step procedure](deployment-step-by-step.en.md).

## 1. Publication reference

The reference validated on October 27, 2026 corresponds to service version 40.
That number belongs to the Azure SRE asset used during validation; importing
the asset into another environment can produce a different number. Compliance
must therefore be established with this document's checklist, not only with a
version number.

The repository does not currently contain the exported Live Report HTML.
Before a customer deployment:

1. obtain the latest approved asset from the solution owner;
2. publish or update the same Live Report without creating a duplicate;
3. retain an export of the approved asset in the organization's controlled
   release package;
4. run the complete acceptance procedure in section 4.

Do not reconstruct the report from screenshots or an old authoring
conversation.

## 2. Sources and expected behavior

The Live Report calls four read-only tools:

- `FabricSRE` for capacity inventory visible to the identity;
- `FabricAdmin_list_workspaces`;
- `FabricAdmin_list_items`;
- `FabricAdmin_get_cu_metrics` when Capacity Metrics is configured.

The response parser must accept structured responses and text responses with
or without a separator before the `RequestId` and `Date` metadata. It must
search for a valid data block instead of assuming that the first block always
contains the inventory.

The interface must remain generic: no customer, tenant, subscription,
workspace, capacity, or item identifier may be hard-coded.

The French UI uses **espace de travail** and **artefact** throughout. The
English UI retains **workspace** and **item**.

## 3. Reference-version capabilities

### Presentation

- bilingual FR/EN interface and light/dark themes;
- full-width view and responsive layout;
- contextual titles that include the selected workspace;
- dependent global capacity and workspace filters;
- capacity table and **Items per Capacity** chart side by side on wide screens
  and stacked on narrow screens;
- chart height based on category count, at least 44 px per category, bars no
  thicker than 28 px, and vertical scrolling beyond 560 px;
- no overlapping bars or horizontal page overflow;
- resizable table columns.
- tolerant parsing of legacy and current `FabricSRE` connector response
  formats, including responses where `RequestId` and `Date` are no longer
  preceded by the historical separator;
- when a capacity response is still unreadable, counters display **–** rather
  than a false zero and a localized alert reports the unexpected format.

### CU indicators

- segmented **CU-h / CU-s** control applied to every cumulative-consumption
  display, with CU-h as the default mode;
- in CU-h mode, **Cumulative consumption** calculated as `CU-s / 3,600` and
  displayed with two decimal places;
- in CU-s mode, raw cumulative consumption displayed with zero decimal places;
- **Sustained average** in CU with three decimal places;
- **Daily average peak** in CU with three decimal places;
- capacity, workspace, and item tables harmonized with the same units and
  precision: cumulative consumption follows the selected mode, while
  average/peak remain in CU with three decimal places;
- instantaneous unit switching without another API call, retaining raw CU-s
  values as the source of truth;
- selected unit retained during navigation, language changes, and detail-dialog
  use within the session;
- headers, accessible descriptions, notes, tooltips, charts, Tree Map,
  summaries, and the temporal detail dialog aligned with the selected unit;
- CU-column sorting based on raw numeric values rather than localized display
  strings;
- utilization percentages under average and peak when one numeric capacity
  denominator can be resolved;
- no invented percentage when multiple capacities or a non-numeric SKU make
  the denominator ambiguous;
- guidance to select a capacity when utilization cannot be calculated;
- temporal detail dialog using the same units, precision, and percentages;
- explicit distinction between a present zero and unavailable telemetry.

### CU glossary

The **CU Glossary** button must explain:

- CU, CU-s, and CU-h;
- cumulative consumption, sustained average, and daily average;
- the difference between a daily-average peak and an instantaneous peak;
- the SKU utilization formula;
- the effect of active filters.

The dialog must be keyboard accessible, close through its button, backdrop, or
`Escape`, update `aria-expanded`, and return focus to the trigger.

## 4. Mandatory post-publication acceptance

### Connectors and data

- [ ] all four expected tools are offered to the report;
- [ ] no tool is duplicated;
- [ ] capacity, workspace, and item inventory loads;
- [ ] response formats with and without a separator before `RequestId` and
      `Date` produce the same capacity inventory;
- [ ] an unreadable capacity response displays **–** and an unexpected-format
      alert, never three false zero counters;
- [ ] missing CU data displays **Unavailable**, never a false zero;
- [ ] the actually covered period is displayed.

### French and English

- [ ] the report opens in French;
- [ ] no French label uses `Workspace` or `Item`;
- [ ] switching to English displays `Workspace` and `Item`;
- [ ] switching back to French preserves filters;
- [ ] workspace chart and inventory titles include the selected workspace name.

### Layout

- [ ] at 720 px, cards in the Capacities section are stacked;
- [ ] at 1,024, 1,440, and 2,000 px, the page has no horizontal overflow;
- [ ] **Items per Capacity** bars never overlap;
- [ ] CU values remain on one line;
- [ ] tables remain usable through internal scrolling.

### CU calculations

- [ ] CU-h is the default mode and the segmented control clearly exposes its
      selected state to keyboard and assistive-technology users;
- [ ] `7,514 CU-s` becomes `2.09 CU-h` in English and `2,09 CU-h` in French;
- [ ] switching to CU-s displays `7,514 CU-s` with no decimal places in the
      KPI, all three tables, charts, tooltips, and temporal detail dialog;
- [ ] cumulative columns in all three tables follow the selected mode, while
      average and peak remain in CU with three decimal places;
- [ ] for `Load_Activities_E2E`, `5,009 CU-s`, `0.00414 CU`, and `0.058 CU`
      become `1.39 CU-h`, `0.004 CU`, and `0.058 CU` in CU-h mode, then
      `5,009 CU-s`, `0.004 CU`, and `0.058 CU` in CU-s mode;
- [ ] averages, peaks, and utilization percentages do not change when the
      cumulative unit is switched;
- [ ] headers, accessible descriptions, and notes mention CU-h and two decimal
      places in CU-h mode, then CU-s and zero decimal places in CU-s mode, in
      both French and English;
- [ ] ascending and descending cumulative-column sorting remains numeric and
      preserves the same order in both modes;
- [ ] missing telemetry displays **Unavailable**, while an actual zero remains
      visible;
- [ ] `0.0062 CU` becomes `0.006 CU` in English;
- [ ] `0.085 CU` remains displayed with three decimal places;
- [ ] for an F16 SKU, `0.0062 / 16 × 100` is approximately `0.04%`;
- [ ] for an F16 SKU, `0.085 / 16 × 100` is approximately `0.53%`;
- [ ] percentages disappear when the SKU is ambiguous;
- [ ] the glossary opens, closes with `Escape`, and returns focus to its button.

## 5. Stopped Fabric capacity

The Live Report and `FabricAdmin` are external to the Advanced Fabric
workspace. Stopping the capacity that hosts the Lakehouse, notebooks, and
pipeline therefore does not prevent the report itself from opening.

| Function | Expected behavior |
|---|---|
| Opening the Live Report | Works |
| Capacity, workspace, and item inventory | Should work because it comes from Fabric Admin APIs through the external MCP; cache can serve the previous collection during refresh |
| Capacity state | Should appear suspended or inactive after the cache refreshes |
| Recent CU data | Can become **unavailable** when the queried Fabric Capacity Metrics model is hosted on the stopped capacity |
| Lakehouse and Bronze/Silver/Gold tables | Data remains stored, but capacity-dependent compute and access stop |
| Notebooks and daily pipeline | Do not run while the capacity is stopped |
| Advanced history and associated Power BI reports | No longer refresh; model queries can fail |

The report must continue to show available inventory and mark CU values as
**Unavailable** when their source cannot respond.

After restart:

1. confirm that the capacity is active;
2. verify the Fabric Admin MCP `/health` endpoint;
3. rerun or await the next pipeline according to the recovery plan;
4. check Bronze, Silver, and Gold freshness;
5. refresh the semantic model;
6. reconcile Live Report and Power BI CU;
7. document any history gap. Capacity Metrics Compute normally retains only
   about 14 days.

## 6. Resilience recommendation

For Advanced, preferably use a **small Fabric capacity dedicated to the SRE
administration workspace** that contains the Lakehouse, notebooks, pipeline,
semantic model, and Power BI reports. Size it for the actual collection
workload and keep it active during monitoring windows.

This capacity does not host Azure SRE Agent or Fabric Admin MCP: the agent
remains in Azure SRE and MCP remains in Azure Container Apps. The separation
prevents a production-capacity outage from also disabling its own history and
monitoring chain.
