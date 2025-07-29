# Public COLA LLM Analysis

```js
const llmSummaryData = FileAttachment("./data/llm_summary.parquet").parquet();
const llmSummaryFile = FileAttachment("./data/llm_summary.parquet");
const violationsData = FileAttachment("./data/llm_violations_list.parquet").parquet();
const violationsFile = FileAttachment("./data/llm_violations_list.parquet");
const analysisData = FileAttachment("./data/llm_analysis.parquet").parquet();
const analysisFile = FileAttachment("./data/llm_analysis.parquet");

const commodity_color_map = {
  'wine': "#DD35DD",
  'beer': "#ECA349",
  'distilled_spirits': "#5DCB8B"
};
```

```js
// Convert parquet data to array format if needed
const llmSummary = Array.isArray(llmSummaryData) ? llmSummaryData : Array.from(llmSummaryData);
const violations = Array.isArray(violationsData) ? violationsData : Array.from(violationsData);
const analysis = Array.isArray(analysisData) ? analysisData : Array.from(analysisData);
```

### LLM Analysis Summary
The table below summarizes the extent to which LLM analysis has been conducted on public COLAs. Generally, each different 'Analysis Type' represents a change to how the LLM was prompted.
```js
Inputs.table(llmSummary, {
  layout: "auto",
  width: {
  "model_version": 80,
  "analysis_type": 400,
  "total_colas_analyzed": 90,
  "num_colas_with_violations": 90,
  "percent_colas_with_violations": 80
  },
  header: {
    "model_version": "Model",
    "analysis_type": "Analysis Type",
    "ct_commodity": "Commodity",
    "total_colas_analyzed": "# Analyzed",
    "num_colas_with_violations": "# Violations",
    "percent_colas_with_violations": "% Violations",
    "tokens_per_cola": "Tokens/Cola",
    "first_analysis": "First",
    "last_analysis": "Last"
  },
  format: {
    "first_analysis": d => d ? new Date(d).toLocaleDateString() : "N/A",
    "last_analysis": d => d ? new Date(d).toLocaleDateString() : "N/A",
    "percent_colas_with_violations": d => d != null ? d.toFixed(1) + "%" : "N/A"
  }
})
```
### LLM Characteristic Analysis
We prompt the LLM to assess certain characteristics of the product from the COLA images. Summaries of these characteristics follow.

#### Net Contents
The top 10 net contents from the LLM analysis, per commodity, are shown below:
```js
// Group analysis data by 'ai_net_contents' and count, then group top 10 and summarize the rest as 'All Other'
// Normalize ai_net_contents for grouping (e.g., '750 ML', '750 ml', '750ML' -> '750 ml')
function normalizeNetContents(val) {
  if (!val) return "Unknown";
  // Remove parentheticals
  let cleaned = val.replace(/\([^)]*\)/g, "");
  // Ignore text after comma or slash
  cleaned = cleaned.split(/[,\/]/)[0];
  // Replace number words with digits
  const numberWords = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19", "twenty": "20"
  };
  cleaned = cleaned.replace(/\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b/gi,
    match => numberWords[match.toLowerCase()]);
  // Remove all spaces, lowercase, and trailing punctuation
  cleaned = cleaned.replace(/\s+/g, "").toLowerCase().replace(/[.,;:]+$/, "");
    // Remove trailing zeros in decimals, e.g. '5.0%' -> '5%'
    cleaned = cleaned.replace(/(\d+)\.0+%$/, "$1%");
    // Also handle cases like '5.00%' -> '5%'
    cleaned = cleaned.replace(/(\d+)\.0+([a-z%]*)$/, "$1$2");
    return cleaned;
}
// Group by commodity and normalized ai_net_contents, count distinct cola_id
let grouped = Array.from(
  d3.rollup(
    analysis,
    v => new Set(v.map(d => d.cola_id)).size,
    d => d.ct_commodity ?? "Unknown",
    d => normalizeNetContents(d.ai_net_contents)
  ),
  ([ct_commodity, netMap]) =>
    Array.from(netMap, ([ai_net_contents, count]) => ({ct_commodity, ai_net_contents, count}))
).flat();
// For each commodity, get top 10 ai_net_contents, group rest as 'All Other'
let aiNetSummary = [];
for (const commodity of Array.from(new Set(grouped.map(d => d.ct_commodity)))) {
  const items = grouped.filter(d => d.ct_commodity === commodity);
  items.sort((a, b) => b.count - a.count);
  const top10 = items.slice(0, 10);
  const allOtherCount = items.slice(10).reduce((sum, d) => sum + d.count, 0);
  if (allOtherCount > 0) {
    aiNetSummary.push(...top10, {ct_commodity: commodity, ai_net_contents: "All Other", count: allOtherCount});
  } else {
    aiNetSummary.push(...top10);
  }
}
// Display the three commodity bar charts side by side
const commodities = ["distilled_spirits", "wine", "beer"];
function toCamelTitle(str) {
  return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
const chartNodes = commodities.map(commodity => {
  const data = aiNetSummary.filter(d => d.ct_commodity === commodity && d.ai_net_contents.toLowerCase() !== "unknown");
  const title = `${toCamelTitle(commodity)}`;
  return Plot.plot({
    x: {label: `# COLAS (${title})`},
    y: {label: "ai_net_contents", domain: data.map(d => d.ai_net_contents)},
    marks: [
      Plot.barX(data, {y: "ai_net_contents", x: "count", fill: d => commodity_color_map[d.ct_commodity], tip: true})
    ],
    width: 350,
    height: 400,
    marginLeft: 120,
    title
  });
});
display(html`<div style="display: flex; flex-direction: row; gap: 24px; align-items: flex-start;">${chartNodes.map(node => html`<div>${node}</div>`)}</div>`);
```

#### Alcohol by Volume Percentage
The top 10 Alcohol by Volume (ABV) Percentage values from the LLM analysis, per commodity, are shown below:
```js
// Group analysis data by 'ai_abv_percentage' and count, then group top 10 and summarize the rest as 'All Other'
// Normalize ai_abv_percentage for grouping (e.g., '750 ML', '750 ml', '750ML' -> '750 ml')
function normalizeAbv(val) {
  if (!val) return "Unknown";
  // Remove parentheticals
  let cleaned = val.replace(/\([^)]*\)/g, "");
  // Ignore text after comma or slash
  cleaned = cleaned.split(/[,\/]/)[0];
  // Remove all spaces, lowercase, and trailing punctuation
  cleaned = cleaned.replace(/\s+/g, "").toLowerCase().replace(/[.,;:]+$/, "");
  // Remove trailing zeros in decimals, e.g. '5.0%' -> '5%'
  cleaned = cleaned.replace(/(\d+)\.0+%$/, "$1%");
  cleaned = cleaned.replace(/(\d+)\.0+([a-z%]*)$/, "$1$2");
  return cleaned;
}
// Group by commodity and normalized ai_abv_percentage, count distinct cola_id
let grouped = Array.from(
  d3.rollup(
    analysis,
    v => new Set(v.map(d => d.cola_id)).size,
    d => d.ct_commodity ?? "Unknown",
    d => normalizeAbv(d.ai_abv_percentage)
  ),
  ([ct_commodity, netMap]) =>
    Array.from(netMap, ([ai_abv_percentage, count]) => ({ct_commodity, ai_abv_percentage, count}))
).flat();
// For each commodity, get top 10 ai_abv_percentage, group rest as 'All Other'
let abvSummary = [];
for (const commodity of Array.from(new Set(grouped.map(d => d.ct_commodity)))) {
  const items = grouped.filter(d => d.ct_commodity === commodity);
  items.sort((a, b) => b.count - a.count);
  const top10 = items.slice(0, 10);
  const allOtherCount = items.slice(10).reduce((sum, d) => sum + d.count, 0);
  if (allOtherCount > 0) {
    abvSummary.push(...top10, {ct_commodity: commodity, ai_abv_percentage: "All Other", count: allOtherCount});
  } else {
    abvSummary.push(...top10);
  }
}
// Display the three commodity bar charts side by side
const commodities = ["distilled_spirits", "wine", "beer"];
function toCamelTitle(str) {
  return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
const abvChartNodes = commodities.map(commodity => {
  const data = abvSummary.filter(d => d.ct_commodity === commodity && d.ai_abv_percentage.toLowerCase() !== "unknown");
  const title = `${toCamelTitle(commodity)}`;
  return Plot.plot({
    x: {label: `# COLAS (${title})`},
    y: {label: "ai_abv_percentage", domain: data.map(d => d.ai_abv_percentage)},
    marks: [
      Plot.barX(data, {y: "ai_abv_percentage", x: "count", fill: d => commodity_color_map[d.ct_commodity], tip: true})
    ],
    width: 350,
    height: 400,
    marginLeft: 120,
    title
  });
});
display(html`<div style="display: flex; flex-direction: row; gap: 24px; align-items: flex-start;">${abvChartNodes.map(node => html`<div>${node}</div>`)}</div>`);
```

```js
display(aiNetSummary)
display(analysis)
display(violations)
```