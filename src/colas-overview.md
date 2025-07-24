# An overview of Scraped COLAs

```js
const colas = FileAttachment("./data/scraped_colas.json").json();
```

```js
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

// Get all unique commodity types and sort them for consistent ordering
const allCommodityTypes = [...new Set(colas.map(d => d.ct_commodity || "Unknown"))].sort();

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
    title: "COLA Applications by Week and Commodity Type",
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
      domain: allCommodityTypes // Ensure consistent color mapping
    },
    marks: [
      Plot.areaY(chartData, {
        x: "date",
        y: "count",
        fill: "ct_commodity",
        order: "ct_commodity", // Ensure consistent stacking order
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
