---
theme: dashboard
toc: false
---

# Weather forecasts

```js
const forecasts = FileAttachment("./data/forecast.json").json();
```

```js
// Flatten all forecast periods with location information
const allPeriods = forecasts.flatMap(forecast => 
  forecast.forecast ? forecast.forecast.properties.periods.map(period => ({
    ...period,
    locationName: forecast.location.name,
    latitude: forecast.location.latitude,
    longitude: forecast.location.longitude
  })) : []
);

// Get unique locations for consistent coloring
const locations = [...new Set(forecasts.map(f => f.location.name))].sort();

function temperaturePlot(data, {width} = {}) {
  return Plot.plot({
    title: "Hourly temperature forecast by location",
    width,
    x: {type: "utc", ticks: "day", label: null},
    y: {grid: true, inset: 10, label: "Degrees (F)"},
    color: {
      legend: true,
      domain: locations,
      scheme: "category10"
    },
    marks: [
      Plot.lineY(data, {
        x: "startTime",
        y: "temperature",
        stroke: "locationName",
        curve: "step-after",
        tip: true
      })
    ]
  });
}

function humidityPlot(data, {width} = {}) {
  return Plot.plot({
    title: "Hourly relative humidity by location",
    width,
    x: {type: "utc", ticks: "day", label: null},
    y: {grid: true, inset: 10, label: "Percent (%)"},
    color: {
      legend: true,
      domain: locations,
      scheme: "category10"
    },
    marks: [
      Plot.lineY(data, {
        x: "startTime",
        y: d => d.relativeHumidity.value,
        stroke: "locationName",
        curve: "step-after",
        tip: true
      })
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">${resize((width) => temperaturePlot(allPeriods, {width}))}</div>
  <div class="card">${resize((width) => humidityPlot(allPeriods, {width}))}</div>
</div>