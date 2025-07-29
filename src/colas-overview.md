# Public COLA Registry Analysis

```js
const colaData = FileAttachment("./data/scraped_colas.parquet").parquet();
const colas_file = FileAttachment("./data/scraped_colas.parquet");
```

```js
// Convert parquet data to array format if needed
const colas = Array.isArray(colaData) ? colaData : Array.from(colaData);

// Get file metadata for display
const fileSize = (colas_file.size / 1024).toFixed(1); // Convert to KB
const lastModified = new Date(colas_file.lastModified);
const href = colas_file.href;
const downloadName = "scraped_colas_" + lastModified.toISOString().replace(/[:.]/g, "-") + ".parquet";
// display(colas.slice(0, 5)); // Show first 5 records for debugging
```

<div style="margin-bottom: 1rem;">
  <small style="color: #666; font-size: 0.75em;">
    Data as of ${lastModified.toLocaleString()}| <a href="./data/scraped_colas.parquet" download="scraped_colas.parquet" style="color: #0066cc;">Download raw data</a>
  </small>
</div>

```js
display(colas_file)
display(href)
display(colas_file.href)
// Group data by weekly date and commodity type
const colasByWeekAndCommodity = d3.rollup(
  colas,
  v => v.length,
  d => {
    if (!d.completed_date) return "Unknown";
    const date = new Date(d.completed_date);
    // Get the start of the week (Sunday)
    const startOfWeek = new Date(date);
    startOfWeek.setDate(date.getDate() - date.getDay());
    return startOfWeek.toISOString().split('T')[0]; // Return YYYY-MM-DD format
  },
  d => d.ct_commodity || "Unknown"
);

// Get all unique commodity types and sort them by frequency (most frequent first)
const commodityFrequency = d3.rollup(
  colas.filter(d => d.ct_commodity), // Filter out null/undefined commodities
  v => v.length,
  d => d.ct_commodity
);

const allCommodityTypes = [...commodityFrequency.entries()]
  .sort((a, b) => b[1] - a[1]) // Sort by count descending (most frequent first)
  .map(d => d[0]); // Extract just the commodity names

// Add "Unknown" at the end if it exists in the data
if (colas.some(d => !d.ct_commodity)) {
  allCommodityTypes.push("Unknown");
}

// Convert to array format for plotting, ensuring all weeks have all commodity types
const chartData = [];
for (const [week, commodityMap] of colasByWeekAndCommodity) {
  if (week === "Unknown") continue;
  
  const weekDate = new Date(week);
  if (isNaN(weekDate)) continue;
  
  // For each commodity type, add an entry (even if count is 0)
  for (const commodity of allCommodityTypes) {
    chartData.push({
      date: weekDate,
      ct_commodity: commodity,
      count: commodityMap.get(commodity) || 0
    });
  }
}

// Sort by date first, then by commodity type for consistent stacking
chartData.sort((a, b) => {
  const dateCompare = a.date - b.date;
  if (dateCompare !== 0) return dateCompare;
  return a.ct_commodity.localeCompare(b.ct_commodity);
});
```


```js
// Create a chart with the actual data if we have any
if (chartData.length > 0) {
  display(Plot.plot({
    title: "Scraped COLA Applications by Completed Week and Commodity Type",
    x: {
      label: "Week",
      type: "time"
    },
    y: {
      label: "Number of COLAs",
      grid: true
    },
    color: {
      legend: true,
      scheme: "category10",
      domain: allCommodityTypes // Most frequent at top of legend
    },
    marks: [
      Plot.areaY(chartData, {
        x: "date",
        y: "count",
        fill: "ct_commodity",
        order: allCommodityTypes, // Most frequent at top of stack
        curve: "step",
        tip: true
      })
    ],
    marginLeft: 60,
    marginBottom: 60,
    height: 400
  }))
} else {
  display(html`<p>No valid chart data available. Check the data structure above.</p>`)
}
```
