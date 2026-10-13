import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve("powerbi", "FabricSRE");
const VISUAL_SCHEMA =
  "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json";
const PAGE_SCHEMA =
  "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json";
const PAGES_SCHEMA =
  "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json";
const CANVAS = {
  width: 1920,
  height: 1080,
  margin: 32,
  gutter: 24,
};

const translations = {
  fr: {
    report: "FabricSRE-fr",
    pages: [
      {
        key: "overview",
        name: "Les capacités à risque ressortent en moins de dix secondes",
        cards: [
          ["Capacity", "Capacity Count"],
          ["Capacity Daily", "CU Seconds"],
          ["Capacity Daily", "P95 Daily CU"],
          ["Capacity Daily", "Throttled Days"],
          ["Refresh Daily", "Refresh Success Rate"],
        ],
        charts: [
          ["bar", "Capacity", "Capacity Name", "Capacity Daily", "CU Seconds", "CU par capacité"],
          ["line", "Date", "Date", "Capacity Daily", "CU Seconds", "Tendance quotidienne des CU"],
          ["matrix", "Capacity", "Capacity Name", "Capacity Daily", ["P95 Daily CU", "Throttling Seconds", "Failure Count"], "Risques par capacité"],
        ],
      },
      {
        key: "top15",
        name: "Les 15 éléments les plus coûteux expliquent la pression CU",
        slicers: [
          ["Période", "Period", "Label"],
          ["Capacité", "Capacity", "Capacity Name"],
          ["Espace de travail", "Workspace", "Workspace Name"],
          ["Type d'élément", "Item", "Item Type"],
          ["Type d'opération", "Operation", "Operation Type"],
        ],
        cards: [
          ["Item Daily", "Item CU Selected Period"],
          ["Item Daily", "Item CU Trend Percent"],
          ["Item Daily", "Item Failure Count"],
          ["Item Daily", "Duration Seconds"],
        ],
        charts: [
          ["bar", "Item", "Item Name", "Item Daily", "Item CU Selected Period", "Top 15 des éléments par CU"],
          ["line", "Date", "Date", "Item Daily", "Item CU Seconds", "CU quotidiennes sur 60 jours"],
          ["matrix", "Item", "Item Name", "Item Daily", ["Item CU Selected Period", "Item CU Share", "Item CU Trend Percent", "Item Failure Count"], "Classement détaillé"],
        ],
      },
      {
        key: "item-detail",
        name: "Le détail d'un élément relie tendance, durée, échecs et throttling",
        drillthrough: true,
        cards: [
          ["Item Daily", "Item CU Seconds"],
          ["Item Daily", "Item CU Share"],
          ["Item Daily", "Item CU Trend Percent"],
          ["Item Daily", "User Count"],
          ["Item Daily", "Item Failure Count"],
        ],
        charts: [
          ["line", "Date", "Date", "Item Daily", "Item CU Seconds", "Courbe quotidienne des CU"],
          ["bar", "Workspace", "Workspace Name", "Item Daily", "Duration Seconds", "Durée par espace de travail"],
          ["matrix", "Item", "Item Name", "Item Daily", ["Item CU Seconds", "Duration Seconds", "Item Failure Count", "User Count"], "Métadonnées et contribution"],
        ],
      },
      {
        key: "operations",
        name: "Les exceptions d'actualisation et de gouvernance sont priorisées",
        cards: [
          ["Refresh Daily", "Refresh Count"],
          ["Refresh Daily", "Refresh Failure Count"],
          ["Refresh Daily", "Refresh Success Rate"],
          ["Refresh Daily", "P95 Refresh Minutes"],
          ["Item", "Uncertified Item Count"],
        ],
        charts: [
          ["line", "Date", "Date", "Refresh Daily", "Refresh Failure Count", "Échecs d'actualisation"],
          ["bar", "Workspace", "Workspace Name", "Refresh Daily", "Average Refresh Minutes", "Lenteur par espace de travail"],
          ["matrix", "Item", "Item Name", "Refresh Daily", ["Refresh Count", "Refresh Failure Count", "Average Refresh Minutes", "P95 Refresh Minutes"], "File d'exceptions"],
        ],
      },
    ],
    slicers: ["Capacité", "Espace de travail", "Type d'élément"],
  },
  en: {
    report: "FabricSRE-en",
    pages: [
      {
        key: "overview",
        name: "At-risk capacities stand out in under ten seconds",
        cards: [
          ["Capacity", "Capacity Count"],
          ["Capacity Daily", "CU Seconds"],
          ["Capacity Daily", "P95 Daily CU"],
          ["Capacity Daily", "Throttled Days"],
          ["Refresh Daily", "Refresh Success Rate"],
        ],
        charts: [
          ["bar", "Capacity", "Capacity Name", "Capacity Daily", "CU Seconds", "CU by capacity"],
          ["line", "Date", "Date", "Capacity Daily", "CU Seconds", "Daily CU trend"],
          ["matrix", "Capacity", "Capacity Name", "Capacity Daily", ["P95 Daily CU", "Throttling Seconds", "Failure Count"], "Capacity risk detail"],
        ],
      },
      {
        key: "top15",
        name: "The top 15 items explain most CU pressure",
        slicers: [
          ["Period", "Period", "Label"],
          ["Capacity", "Capacity", "Capacity Name"],
          ["Workspace", "Workspace", "Workspace Name"],
          ["Item type", "Item", "Item Type"],
          ["Operation type", "Operation", "Operation Type"],
        ],
        cards: [
          ["Item Daily", "Item CU Selected Period"],
          ["Item Daily", "Item CU Trend Percent"],
          ["Item Daily", "Item Failure Count"],
          ["Item Daily", "Duration Seconds"],
        ],
        charts: [
          ["bar", "Item", "Item Name", "Item Daily", "Item CU Selected Period", "Top 15 items by CU"],
          ["line", "Date", "Date", "Item Daily", "Item CU Seconds", "Daily CU over 60 days"],
          ["matrix", "Item", "Item Name", "Item Daily", ["Item CU Selected Period", "Item CU Share", "Item CU Trend Percent", "Item Failure Count"], "Detailed ranking"],
        ],
      },
      {
        key: "item-detail",
        name: "Item detail links trend, duration, failures, and throttling",
        drillthrough: true,
        cards: [
          ["Item Daily", "Item CU Seconds"],
          ["Item Daily", "Item CU Share"],
          ["Item Daily", "Item CU Trend Percent"],
          ["Item Daily", "User Count"],
          ["Item Daily", "Item Failure Count"],
        ],
        charts: [
          ["line", "Date", "Date", "Item Daily", "Item CU Seconds", "Daily CU curve"],
          ["bar", "Workspace", "Workspace Name", "Item Daily", "Duration Seconds", "Duration by workspace"],
          ["matrix", "Item", "Item Name", "Item Daily", ["Item CU Seconds", "Duration Seconds", "Item Failure Count", "User Count"], "Metadata and contribution"],
        ],
      },
      {
        key: "operations",
        name: "Refresh and governance exceptions are prioritized",
        cards: [
          ["Refresh Daily", "Refresh Count"],
          ["Refresh Daily", "Refresh Failure Count"],
          ["Refresh Daily", "Refresh Success Rate"],
          ["Refresh Daily", "P95 Refresh Minutes"],
          ["Item", "Uncertified Item Count"],
        ],
        charts: [
          ["line", "Date", "Date", "Refresh Daily", "Refresh Failure Count", "Refresh failures"],
          ["bar", "Workspace", "Workspace Name", "Refresh Daily", "Average Refresh Minutes", "Latency by workspace"],
          ["matrix", "Item", "Item Name", "Refresh Daily", ["Refresh Count", "Refresh Failure Count", "Average Refresh Minutes", "P95 Refresh Minutes"], "Exception queue"],
        ],
      },
    ],
    slicers: ["Capacity", "Workspace", "Item type"],
  },
};

function id(value) {
  return crypto.createHash("sha256").update(value).digest("hex").slice(0, 20);
}

function column(table, property) {
  return {
    field: { Column: { Expression: { SourceRef: { Entity: table } }, Property: property } },
    queryRef: `${table}.${property}`,
    nativeQueryRef: property,
  };
}

function measure(table, property) {
  return {
    field: { Measure: { Expression: { SourceRef: { Entity: table } }, Property: property } },
    queryRef: `${table}.${property}`,
    nativeQueryRef: property,
  };
}

function position(x, y, width, height, z) {
  return { x, y, z, width, height, tabOrder: z };
}

function titleVisual(name, text, bounds, z = 1000) {
  return {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(bounds.x, bounds.y, bounds.width, bounds.height, z),
    visual: {
      visualType: "textbox",
      objects: {
        general: [{
          properties: {
            paragraphs: [{
              textRuns: [{
                value: text,
                textStyle: {
                  fontFamily: "Segoe UI Semibold",
                  fontSize: "26px",
                  color: "#0F3B57",
                },
              }],
              horizontalTextAlignment: "left",
            }],
          },
        }],
      },
      visualContainerObjects: {
        background: [{ properties: { show: { expr: { Literal: { Value: "false" } } } } }],
        border: [{ properties: { show: { expr: { Literal: { Value: "false" } } } } }],
        padding: [{ properties: Object.fromEntries(["top", "bottom", "left", "right"].map((side) => [side, { expr: { Literal: { Value: "0D" } } }])) }],
      },
    },
  };
}

function slicerVisual(name, x, width, label, table, property, z) {
  return {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(x, 24, width, 80, z),
    visual: {
      visualType: "slicer",
      query: { queryState: { Values: { projections: [column(table, property)] } } },
      objects: {
        data: [{ properties: { mode: { expr: { Literal: { Value: "'Dropdown'" } } } } }],
        header: [{ properties: {
          show: { expr: { Literal: { Value: "true" } } },
          text: { expr: { Literal: { Value: `'${label}'` } } },
        } }],
      },
      visualContainerObjects: {
        padding: [{ properties: Object.fromEntries(["top", "bottom", "left", "right"].map((side) => [side, { expr: { Literal: { Value: "8D" } } }])) }],
      },
    },
  };
}

function cardVisual(name, cards, bounds, z) {
  return {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(bounds.x, bounds.y, bounds.width, bounds.height, z),
    visual: {
      visualType: "cardVisual",
      query: { queryState: { Data: { projections: cards.map(([table, metric]) => measure(table, metric)) } } },
      objects: {
        outline: [{ selector: { id: "default" }, properties: { show: { expr: { Literal: { Value: "false" } } } } }],
      },
    },
  };
}

function titleVco(text) {
  return {
    title: [{ properties: {
      show: { expr: { Literal: { Value: "true" } } },
      text: { expr: { Literal: { Value: `'${text.replaceAll("'", "''")}'` } } },
    } }],
  };
}

function top15RankFilter(language, target) {
  return {
    name: `Filter${id(`${language}:top15:rank:${target}`).padEnd(24, "0")}`,
    field: measure("Item Daily", "Item CU Rank").field,
    type: "Advanced",
    filter: {
      Version: 2,
      From: [{ Name: "d", Entity: "Item Daily", Type: 0 }],
      Where: [{
        Condition: {
          Between: {
            Expression: {
              Measure: {
                Expression: { SourceRef: { Source: "d" } },
                Property: "Item CU Rank",
              },
            },
            LowerBound: { Literal: { Value: "1L" } },
            UpperBound: { Literal: { Value: "15L" } },
          },
        },
      }],
    },
    howCreated: "User",
  };
}

function cartesianVisual(name, type, x, y, width, height, categoryTable, category, metricTable, metric, title, z, filterConfig) {
  const isBarChart = type === "bar";
  const result = {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(x, y, width, height, z),
    visual: {
      visualType: isBarChart ? "barChart" : "lineChart",
      query: {
        queryState: {
          Category: { projections: [column(categoryTable, category)] },
          Y: { projections: [measure(metricTable, metric)] },
        },
        sortDefinition: {
          sort: [{ field: measure(metricTable, metric).field, direction: "Descending" }],
        },
      },
      visualContainerObjects: titleVco(title),
    },
  };
  if (isBarChart) {
    result.visual.objects = {
      categoryAxis: [{
        properties: {
          preferredCategoryWidth: { expr: { Literal: { Value: "32D" } } },
          maxMarginFactor: { expr: { Literal: { Value: "32L" } } },
          innerPadding: { expr: { Literal: { Value: "18L" } } },
        },
      }],
      valueAxis: [{
        properties: {
          start: { expr: { Literal: { Value: "0D" } } },
          labelPrecision: { expr: { Literal: { Value: "0L" } } },
          gridlineTransparency: { expr: { Literal: { Value: "85D" } } },
          gridlineStyle: { expr: { Literal: { Value: "'dotted'" } } },
        },
      }],
    };
  }
  if (filterConfig) result.filterConfig = filterConfig;
  return result;
}

function matrixVisual(name, bounds, rowTable, rowProperty, metricTable, metrics, title, z, filterConfig) {
  const result = {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(bounds.x, bounds.y, bounds.width, bounds.height, z),
    visual: {
      visualType: "pivotTable",
      query: {
        queryState: {
          Rows: { projections: [column(rowTable, rowProperty)] },
          Values: { projections: metrics.map((metric) => measure(metricTable, metric)) },
        },
      },
      objects: {
        columnHeaders: [{ properties: {
          columnAdjustment: { expr: { Literal: { Value: "'growToFit'" } } },
          autoSizeColumnWidth: { expr: { Literal: { Value: "true" } } },
        } }],
      },
      visualContainerObjects: titleVco(title),
    },
  };
  if (filterConfig) result.filterConfig = filterConfig;
  return result;
}

function backButton(name, label, z) {
  return {
    $schema: VISUAL_SCHEMA,
    name,
    position: position(CANVAS.margin, 32, 160, 64, z),
    visual: {
      visualType: "actionButton",
      objects: {
        text: [{
          selector: { id: "default" },
          properties: {
            show: { expr: { Literal: { Value: "true" } } },
            text: { expr: { Literal: { Value: `'${label}'` } } },
          },
        }],
      },
      visualContainerObjects: {
        visualLink: [{
          properties: {
            show: { expr: { Literal: { Value: "true" } } },
            type: { expr: { Literal: { Value: "'Back'" } } },
          },
        }],
      },
    },
  };
}

function writeVisual(pageDir, visual) {
  const visualDir = path.join(pageDir, "visuals", visual.name);
  fs.mkdirSync(visualDir, { recursive: true });
  fs.writeFileSync(path.join(visualDir, "visual.json"), `${JSON.stringify(visual, null, 2)}\n`);
}

function pageLayout(page) {
  const slicerCount = (page.slicers ?? [null, null, null]).length;
  const slicerStart = slicerCount > 3 ? 880 : 1120;
  const slicerGap = 8;
  const slicerWidth = Math.floor(
    (
      CANVAS.width
      - CANVAS.margin
      - slicerStart
      - slicerGap * (slicerCount - 1)
    ) / slicerCount / 8,
  ) * 8;
  const cardHeight = page.cards.length > 4 ? 144 : 128;
  const cardY = 120;
  const analysisY = cardY + cardHeight + CANVAS.gutter;
  const detailMetricCount = page.charts[2][4].length;
  const detailHeight = detailMetricCount > 3 ? 272 : 224;
  const detailY = CANVAS.height - CANVAS.margin - detailHeight;
  const analysisHeight = detailY - CANVAS.gutter - analysisY;
  const contentWidth = CANVAS.width - CANVAS.margin * 2;
  const panelWidth = (contentWidth - CANVAS.margin) / 2;
  const titleX = page.drillthrough ? 216 : CANVAS.margin;

  return {
    title: {
      x: titleX,
      y: 32,
      width: slicerStart - titleX - CANVAS.gutter,
      height: 64,
    },
    slicers: { count: slicerCount, start: slicerStart, width: slicerWidth, gap: slicerGap },
    cards: {
      x: CANVAS.margin,
      y: cardY,
      width: contentWidth,
      height: cardHeight,
    },
    left: {
      x: CANVAS.margin,
      y: analysisY,
      width: panelWidth,
      height: analysisHeight,
    },
    right: {
      x: CANVAS.margin + panelWidth + CANVAS.margin,
      y: analysisY,
      width: panelWidth,
      height: analysisHeight,
    },
    detail: {
      x: CANVAS.margin,
      y: detailY,
      width: contentWidth,
      height: detailHeight,
    },
  };
}

for (const [language, config] of Object.entries(translations)) {
  const reportDir = path.join(ROOT, language, `${config.report}.Report`);
  const pagesRoot = path.join(reportDir, "definition", "pages");
  fs.rmSync(pagesRoot, { recursive: true, force: true });
  fs.mkdirSync(pagesRoot, { recursive: true });
  const pageOrder = [];

  config.pages.forEach((page, pageIndex) => {
    const layout = pageLayout(page);
    const pageId = id(`${language}:${page.key}`);
    const pageDir = path.join(pagesRoot, pageId);
    fs.mkdirSync(path.join(pageDir, "visuals"), { recursive: true });
    const pageJson = {
      $schema: PAGE_SCHEMA,
      name: pageId,
      displayName: page.name,
      displayOption: "FitToWidth",
      height: CANVAS.height,
      width: CANVAS.width,
      objects: {
        background: [{ properties: {
          color: { solid: { color: { expr: { Literal: { Value: "'#F4F8FB'" } } } } },
          transparency: { expr: { Literal: { Value: "0D" } } },
        } }],
      },
    };
    if (page.drillthrough) {
      const drillFilterName = `Filter${id(`${language}:drill:item`).padEnd(24, "0")}`;
      const drillField = {
        Column: { Expression: { SourceRef: { Entity: "Item" } }, Property: "ItemId" },
      };
      pageJson.pageBinding = {
        name: "Pod",
        type: "Drillthrough",
        parameters: [{
          name: `Param_${drillFilterName}`,
          boundFilter: drillFilterName,
          fieldExpr: drillField,
        }],
      };
      pageJson.filterConfig = {
        filters: [{
          name: drillFilterName,
          field: drillField,
          type: "Categorical",
          howCreated: "Drillthrough",
        }],
      };
    }
    fs.writeFileSync(path.join(pageDir, "page.json"), `${JSON.stringify(pageJson, null, 2)}\n`);
    let z = 1000;
    writeVisual(pageDir, titleVisual(
      id(`${language}:${page.key}:title`),
      page.name,
      layout.title,
      z,
    ));
    z += 1000;
    if (page.drillthrough) {
      writeVisual(pageDir, backButton(
        id(`${language}:${page.key}:back`),
        language === "fr" ? "Retour" : "Back",
        z,
      ));
      z += 1000;
    }
    const slicers = page.slicers ?? [
      [config.slicers[0], "Capacity", "Capacity Name"],
      [config.slicers[1], "Workspace", "Workspace Name"],
      [config.slicers[2], "Item", "Item Type"],
    ];
    slicers.forEach(([label, table, property], index) => {
      const x = layout.slicers.start + index * (layout.slicers.width + layout.slicers.gap);
      const visual = slicerVisual(
        id(`${language}:${page.key}:slicer:${index}`),
        x,
        layout.slicers.width,
        label,
        table,
        property,
        z,
      );
      writeVisual(pageDir, visual);
      z += 1000;
    });
    writeVisual(pageDir, cardVisual(id(`${language}:${page.key}:cards`), page.cards, layout.cards, z));
    z += 1000;
    const [left, right, detail] = page.charts;
    const rankChartFilter = page.key === "top15"
      ? { filters: [top15RankFilter(language, "chart")] }
      : undefined;
    const rankTableFilter = page.key === "top15"
      ? { filters: [top15RankFilter(language, "table")] }
      : undefined;
    writeVisual(pageDir, cartesianVisual(
      id(`${language}:${page.key}:left`), left[0],
      layout.left.x, layout.left.y, layout.left.width, layout.left.height,
      left[1], left[2], left[3], left[4], left[5], z, rankChartFilter,
    ));
    z += 1000;
    writeVisual(pageDir, cartesianVisual(
      id(`${language}:${page.key}:right`), right[0],
      layout.right.x, layout.right.y, layout.right.width, layout.right.height,
      right[1], right[2], right[3], right[4], right[5], z,
    ));
    z += 1000;
    writeVisual(pageDir, matrixVisual(
      id(`${language}:${page.key}:detail`), layout.detail,
      detail[1], detail[2], detail[3], detail[4], detail[5], z, rankTableFilter,
    ));
    pageOrder.push(pageId);
  });

  fs.writeFileSync(
    path.join(pagesRoot, "pages.json"),
    `${JSON.stringify({ $schema: PAGES_SCHEMA, pageOrder, activePageName: pageOrder[0] }, null, 2)}\n`,
  );
}
