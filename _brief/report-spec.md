# Report Spec

## Report identity

- Report name: Fabric SRE (separate `FabricSRE-fr` and `FabricSRE-en`)
- Semantic model: `FabricSRE.SemanticModel`
- Audience: Fabric administrators and on-call operators
- Primary purpose: detect capacity, refresh, and governance exceptions and drill
  to the responsible item
- Delivery target: local PBIP first; publish to the configured administration
  workspace after preflight

## User decisions and constraints

- Scope: four operational pages, including Top 15 and item drillthrough
- Page count: four per language
- Interactivity: global capacity/workspace/item-type slicers and item drillthrough
- Design direction: calm Azure control-room, dense but accessible
- Publishing: blocked until the target Azure subscription/workspace is visible
- Tooling: PBIP/PBIR, TMDL, deterministic Node generator
- Model edit permissions: local TMDL; service deployment requires Contributor
- Accessibility: WCAG AA, semantic colors plus labels, predictable tab order
- Data caveats: Capacity Metrics app schema is adapter-validated and has no
  stable item-level REST contract

## Narrative

- Core story: surface pressure and exceptions, then attribute them to items
- Audience promise: understand state in ten seconds and reach evidence in one click
- Key questions answered: which capacity is at risk, what consumes CU, why an
  item is anomalous, and what requires operational follow-up

## Design identity

- Tone: Azure control-room calm — pale blue surface, navy text, saturated blue
  analysis, amber warning, red incident
- Signature: a compact full-width composite KPI strip followed by paired
  evidence panels and a content-proportional exception matrix on every page

## Page plan

1. Capacity health — Operational Monitor, variant A
2. Top 15 CU items — Comparative Benchmark, variant B
3. Item detail — Analytical Canvas, variant B, drillthrough
4. Operations and governance — Operational Monitor, variant C

## Design system summary

- Theme: Fabric SRE Control Room; `#F4F8FB` surface, `#0F3B57` text,
  `#0078D4` CU, `#D97706` warning, `#C50F1F` incident
- Typography: Segoe UI Semibold display + Segoe UI body
- Layout: FHD 1920×1080, 32px margins, 24px gutters, 8px grid; default
  browser view fits the report width and vertical space is allocated from each
  page's KPI and detail density
- Accessibility: explicit titles/alt text, no color-only state, keyboard order

## Model requirements

- Existing measures: none (greenfield)
- New measures: CU average/P95/max/trend/share/rank, throttling, failures,
  refresh success/duration, storage growth
- New calculated columns: none; transformations remain upstream
- Relationships: single-direction star schema through Date/Capacity/Workspace/Item

## Canonical design contract

```yaml
Design Brief:
  generated_by: powerbi-report-design
  contract_version: 1
  mode: brownfield
  design_identity:
    tone: "Azure control-room calm: pale blue surface, navy text, blue analysis, amber warning, red incident"
    signature: "Compact composite KPI strip, paired evidence panels, and content-proportional exception matrix repeated across pages"
    current_tone: "Azure control-room calm with fixed-height visual bands"
    current_signature: "Composite KPI strip, paired evidence panels, and equally sized exception matrix"
  viewport_behavior: "FitToWidth on a fixed 16:9 canvas; generated visual bands adapt to KPI and detail density without overlap."
  bar_density: "Horizontal bars use 18% inner padding, a 32px minimum category band, and low-emphasis dotted gridlines."
  archetype: Operational
  color_map:
    - { measure: "Capacity Daily[CU Seconds]", color: "#0078D4", tint: "#DCEEFF" }
    - { measure: "Capacity Daily[Throttling Seconds]", color: "#D97706", tint: "#FEF3C7" }
    - { measure: "Capacity Daily[Failure Count]", color: "#C50F1F", tint: "#FDE7E9" }
    - { measure: "Item Daily[Item CU Seconds]", color: "#0078D4", tint: "#DCEEFF" }
    - { measure: "Refresh Daily[Refresh Failure Count]", color: "#C50F1F", tint: "#FDE7E9" }
  pages:
    - name: "Capacity health"
      role: landing
      archetype: Operational
      layout_variant: A
      variant_rationale: "Four golden signals and a capacity exception queue require balanced surveillance and triage."
      page_background: "#F4F8FB"
      layout_contract:
        canvas: { width: 1920, height: 1080, margin: 32, gutter: 24, snap: 8, display_option: FitToWidth }
        grid:
          columns: 12
          rows: 12
          regions:
            header: [1, 1, 8, 2]
            filters: [8, 1, 13, 2]
            kpis: [1, 2, 13, 4]
            left: [1, 4, 7, 9]
            right: [7, 4, 13, 9]
            detail: [1, 9, 13, 13]
        placements:
          - { id: page_title, region: header, kind: textbox, text: "At-risk capacities stand out in under ten seconds" }
          - { id: capacity_slicer, region: filters, kind: slicer, field_bindings: "Capacity[Capacity Name]", slot: 1, of: 3 }
          - { id: workspace_slicer, region: filters, kind: slicer, field_bindings: "Workspace[Workspace Name]", slot: 2, of: 3 }
          - { id: item_type_slicer, region: filters, kind: slicer, field_bindings: "Item[Item Type]", slot: 3, of: 3 }
          - id: health_kpis
            region: kpis
            kind: cardVisual
            purpose: "What is the current capacity health context?"
            field_bindings: ["Capacity[Capacity Count]", "Capacity Daily[CU Seconds]", "Capacity Daily[P95 Daily CU]", "Capacity Daily[Throttled Days]", "Refresh Daily[Refresh Success Rate]"]
          - { id: cu_by_capacity, region: left, kind: barChart, purpose: "Which capacity consumes the most CU?", field_bindings: { Category: "Capacity[Capacity Name]", Y: "Capacity Daily[CU Seconds]" } }
          - { id: cu_trend, region: right, kind: lineChart, purpose: "How is CU changing daily?", field_bindings: { Category: "Date[Date]", Y: "Capacity Daily[CU Seconds]" } }
          - { id: capacity_risk, region: detail, kind: pivotTable, purpose: "Which capacities need follow-up?", field_bindings: ["Capacity[Capacity Name]", "Capacity Daily[P95 Daily CU]", "Capacity Daily[Throttling Seconds]", "Capacity Daily[Failure Count]"] }
        space_audit: { content_cell_count: 132, placed_cell_count: 132, empty_cell_pct: 0, unplaced_regions: [], largest_region: { name: left, pct_of_content: 38 }, balance_rationale: "Monitoring and trend receive the height released by the compact three-measure triage matrix." }
    - name: "Top 15 CU items"
      role: detail
      archetype: Comparative
      layout_variant: B
      variant_rationale: "A ranked entity comparison and 60-day evidence trend are equally important."
      page_background: "#F4F8FB"
      layout_contract:
        canvas: { width: 1920, height: 1080, margin: 32, gutter: 24, snap: 8, display_option: FitToWidth }
        grid:
          columns: 12
          rows: 12
          regions: { header: [1, 1, 8, 2], filters: [8, 1, 13, 2], kpis: [1, 2, 13, 4], ranking: [1, 4, 7, 9], trend: [7, 4, 13, 9], detail: [1, 9, 13, 13] }
        placements:
          - { id: page_title, region: header, kind: textbox, text: "The top 15 items explain most CU pressure" }
          - { id: period_slicer, region: filters, kind: slicer, field_bindings: "Period[Label]", slot: 1, of: 5 }
          - { id: capacity_slicer, region: filters, kind: slicer, field_bindings: "Capacity[Capacity Name]", slot: 2, of: 5 }
          - { id: workspace_slicer, region: filters, kind: slicer, field_bindings: "Workspace[Workspace Name]", slot: 3, of: 5 }
          - { id: item_type_slicer, region: filters, kind: slicer, field_bindings: "Item[Item Type]", slot: 4, of: 5 }
          - { id: operation_type_slicer, region: filters, kind: slicer, field_bindings: "Operation[Operation Type]", slot: 5, of: 5 }
          - { id: item_kpis, region: kpis, kind: cardVisual, purpose: "How much CU, trend, failure, and duration are present?", field_bindings: ["Item Daily[Item CU Selected Period]", "Item Daily[Item CU Trend Percent]", "Item Daily[Item Failure Count]", "Item Daily[Duration Seconds]"] }
          - { id: top_items, region: ranking, kind: barChart, purpose: "Which items are the top CU consumers?", field_bindings: { Category: "Item[Item Name]", Y: "Item Daily[Item CU Selected Period]" } }
          - { id: item_trend, region: trend, kind: lineChart, purpose: "How did CU change over 60 days?", field_bindings: { Category: "Date[Date]", Y: "Item Daily[Item CU Seconds]" } }
          - { id: item_ranking_detail, region: detail, kind: pivotTable, purpose: "What share and trend does each item have?", field_bindings: ["Item[Item Name]", "Item Daily[Item CU Selected Period]", "Item Daily[Item CU Share]", "Item Daily[Item CU Trend Percent]"] }
        space_audit: { content_cell_count: 132, placed_cell_count: 132, empty_cell_pct: 0, unplaced_regions: [], largest_region: { name: ranking, pct_of_content: 35 }, balance_rationale: "Ranking and time evidence gain height while the four-measure detail table remains compact and usable." }
    - name: "Item detail"
      role: drillthrough
      archetype: Analytical
      layout_variant: B
      variant_rationale: "Three inline filters leave full width for trend, attribution, and metadata."
      page_background: "#F4F8FB"
      layout_contract:
        canvas: { width: 1920, height: 1080, margin: 32, gutter: 24, snap: 8, display_option: FitToWidth }
        grid:
          columns: 12
          rows: 12
          regions: { header: [1, 1, 8, 2], filters: [8, 1, 13, 2], kpis: [1, 2, 13, 4], trend: [1, 4, 7, 9], attribution: [7, 4, 13, 9], detail: [1, 9, 13, 13] }
        placements:
          - { id: page_title, region: header, kind: textbox, text: "Item detail links trend, duration, failures, and throttling" }
          - { id: capacity_slicer, region: filters, kind: slicer, field_bindings: "Capacity[Capacity Name]", slot: 1, of: 3 }
          - { id: workspace_slicer, region: filters, kind: slicer, field_bindings: "Workspace[Workspace Name]", slot: 2, of: 3 }
          - { id: item_type_slicer, region: filters, kind: slicer, field_bindings: "Item[Item Type]", slot: 3, of: 3 }
          - { id: item_detail_kpis, region: kpis, kind: cardVisual, purpose: "What is the selected item's current footprint?", field_bindings: ["Item Daily[Item CU Seconds]", "Item Daily[Item CU Share]", "Item Daily[Item CU Trend Percent]", "Item Daily[User Count]", "Item Daily[Item Failure Count]"] }
          - { id: daily_curve, region: trend, kind: lineChart, purpose: "What is the 60-day CU trajectory?", field_bindings: { Category: "Date[Date]", Y: "Item Daily[Item CU Seconds]" } }
          - { id: duration_attribution, region: attribution, kind: barChart, purpose: "Where does duration accumulate?", field_bindings: { Category: "Workspace[Workspace Name]", Y: "Item Daily[Duration Seconds]" } }
          - { id: item_metadata, region: detail, kind: pivotTable, purpose: "What metadata and effects explain this item?", field_bindings: ["Item[Item Name]", "Item Daily[Item CU Seconds]", "Item Daily[Duration Seconds]", "Item Daily[Item Failure Count]", "Item Daily[User Count]"] }
        space_audit: { content_cell_count: 132, placed_cell_count: 132, empty_cell_pct: 0, unplaced_regions: [], largest_region: { name: trend, pct_of_content: 35 }, balance_rationale: "Trend and attribution gain height while the five-measure evidence table keeps only the space it needs." }
    - name: "Operations and governance"
      role: detail
      archetype: Operational
      layout_variant: C
      variant_rationale: "Operators need the exception queue as the working surface."
      page_background: "#F4F8FB"
      layout_contract:
        canvas: { width: 1920, height: 1080, margin: 32, gutter: 24, snap: 8, display_option: FitToWidth }
        grid:
          columns: 12
          rows: 12
          regions: { header: [1, 1, 8, 2], filters: [8, 1, 13, 2], kpis: [1, 2, 13, 4], failures: [1, 4, 7, 9], latency: [7, 4, 13, 9], exceptions: [1, 9, 13, 13] }
        placements:
          - { id: page_title, region: header, kind: textbox, text: "Refresh and governance exceptions are prioritized" }
          - { id: capacity_slicer, region: filters, kind: slicer, field_bindings: "Capacity[Capacity Name]", slot: 1, of: 3 }
          - { id: workspace_slicer, region: filters, kind: slicer, field_bindings: "Workspace[Workspace Name]", slot: 2, of: 3 }
          - { id: item_type_slicer, region: filters, kind: slicer, field_bindings: "Item[Item Type]", slot: 3, of: 3 }
          - { id: operations_kpis, region: kpis, kind: cardVisual, purpose: "What is the refresh and governance state?", field_bindings: ["Refresh Daily[Refresh Count]", "Refresh Daily[Refresh Failure Count]", "Refresh Daily[Refresh Success Rate]", "Refresh Daily[P95 Refresh Minutes]", "Item[Uncertified Item Count]"] }
          - { id: failure_trend, region: failures, kind: lineChart, purpose: "When do refresh failures occur?", field_bindings: { Category: "Date[Date]", Y: "Refresh Daily[Refresh Failure Count]" } }
          - { id: latency_rank, region: latency, kind: barChart, purpose: "Which workspaces have slow refreshes?", field_bindings: { Category: "Workspace[Workspace Name]", Y: "Refresh Daily[Average Refresh Minutes]" } }
          - { id: exception_queue, region: exceptions, kind: pivotTable, purpose: "Which items need immediate follow-up?", field_bindings: ["Item[Item Name]", "Refresh Daily[Refresh Count]", "Refresh Daily[Refresh Failure Count]", "Refresh Daily[Average Refresh Minutes]", "Refresh Daily[P95 Refresh Minutes]"] }
        space_audit: { content_cell_count: 132, placed_cell_count: 132, empty_cell_pct: 0, unplaced_regions: [], largest_region: { name: failures, pct_of_content: 35 }, balance_rationale: "Diagnostic panels gain readable height while the five-measure exception queue remains a compact working surface." }
  interaction_pattern:
    drill_targets: ["Item detail"]
    cross_filter_rules: "Charts filter the detail matrix; Top 15 rows drill through by ItemId."
  accessibility:
    alt_text_strategy: "State the analytical question, selected period, and primary comparison."
    contrast_notes: "All text/background pairs meet WCAG AA; warning and incident state include labels."
  theme:
    base: "Fluent2-CY26SU10 with Fabric SRE palette and base safeguards preserved"
    typography: "Segoe UI Semibold display, Segoe UI body"
```

## Implementation notes

- Model changes: deterministic TMDL, Import against parameterized Lakehouse SQL endpoint
- PBIR/report authoring: deterministic `scripts/generate-report.mjs`
- Validation: `powerbi-report-author validate` for both reports
- Desktop screenshot verification: required after binding the model to a
  populated client Lakehouse
- Publishing boundary: no publish until target subscription/workspace preflight passes
- Risks: client Capacity Metrics model schema and source connection credentials
