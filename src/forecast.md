---
theme: dashboard
toc: false
---

# TTB Weather

```js
const forecasts = FileAttachment("./data/forecast.json").json();
const forecast_file = FileAttachment("./data/forecast.json");
```

```js
// Get file metadata for display
const fileSize = (forecast_file.size / 1024).toFixed(1); // Convert to KB
const lastModified = new Date(forecast_file.lastModified); // Current time as we don't have access to file modification time
//display(forecasts)
```

<div style="margin-bottom: 1rem;">
  <small style="color: #666; font-size: 0.85em;">
    Data as of ${lastModified.toLocaleString()} (${fileSize} KB), from https://api.weather.gov
  </small>
</div>

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

function timelinePlot(data, {width} = {}) {
  // Filter to show only every 6 hours to reduce clutter
  const filteredData = data.filter((d, i) => {
    const hour = new Date(d.startTime).getHours();
    return hour % 6 === 0;
  });

  const startTime = new Date(Math.min(...data.map(d => new Date(d.startTime))));

  // Function to truncate text if too long
  const truncateText = (text, maxLength = 25) => {
    return text.length > maxLength ? text.substring(0, maxLength - 3) + '...' : text;
  };

  return Plot.plot({
    title: "Weather forecast timeline (every 6 hours)",
    width,
    height: 220,
    marginLeft: 200,
    x: {type: "utc", ticks: "day", label: null},
    y: {type: "point", domain: locations, label: null, axis: null, padding: 0.5},
    marks: [
      Plot.text(locations, {
        x: startTime,
        y: (d) => d,
        text: (d) => truncateText(d),
        textAnchor: "end",
        dx: -20,
        fontSize: 11,
        fill: "#ffffff",
        fontWeight: "500"
      }),
      Plot.image(filteredData, {
        x: "startTime",
        y: "locationName",
        src: "icon",
        width: 40,
        height: 40,
        title: d => `${d.locationName}: ${d.shortForecast} at ${new Date(d.startTime).toLocaleTimeString()}`
      }),
      Plot.gridY({strokeDasharray: "2,2", stroke: "#ddd"})
    ]
  });
}

function temperaturePlot(data, {width} = {}) {
  const currentTime = new Date();
  const minTemp = Math.min(...data.map(d => d.temperature));
  const maxTemp = Math.max(...data.map(d => d.temperature));
  const labelY = minTemp + (maxTemp - minTemp) * 0.1; // 10% from bottom
  
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
        curve: "catmull-rom",
        tip: true
      }),
      Plot.ruleX([currentTime], {stroke: "white", strokeWidth: 2, strokeDasharray: "4,4"}),
      Plot.text([{x: currentTime, label: "NOW"}], {
        x: "x",
        y: () => labelY,
        text: "label",
        fill: "white",
        fontSize: 12,
        fontWeight: "bold",
        textAnchor: "start",
        dx: 3
      })
    ]
  });
}

function humidityPlot(data, {width} = {}) {
  const currentTime = new Date();
  const minHumidity = Math.min(...data.map(d => d.relativeHumidity.value));
  const maxHumidity = Math.max(...data.map(d => d.relativeHumidity.value));
  const labelY = minHumidity + (maxHumidity - minHumidity) * 0.1; // 10% from bottom
  
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
        curve: "catmull-rom",
        tip: true
      }),
      Plot.ruleX([currentTime], {stroke: "white", strokeWidth: 2, strokeDasharray: "4,4"}),
      Plot.text([{x: currentTime, label: "NOW"}], {
        x: "x",
        y: () => labelY,
        text: "label",
        fill: "white",
        fontSize: 12,
        fontWeight: "bold",
        textAnchor: "start",
        dx: 3
      })
    ]
  });
}

function precipitationPlot(data, {width} = {}) {
  const currentTime = new Date();
  const precipValues = data.map(d => d.probabilityOfPrecipitation?.value || 0);
  const minPrecip = Math.min(...precipValues);
  const maxPrecip = Math.max(...precipValues);
  const labelY = minPrecip + (maxPrecip - minPrecip) * 0.1; // 10% from bottom
  
  return Plot.plot({
    title: "Probability of precipitation by location",
    width,
    x: {type: "utc", ticks: "day", label: null},
    y: {grid: true, inset: 10, label: "Probability (%)", domain: [0, 100]},
    color: {
      legend: true,
      domain: locations,
      scheme: "category10"
    },
    marks: [
      Plot.lineY(data, {
        x: "startTime",
        y: d => d.probabilityOfPrecipitation?.value || 0,
        stroke: "locationName",
        curve: "catmull-rom",
        tip: true
      }),
      Plot.ruleX([currentTime], {stroke: "white", strokeWidth: 2, strokeDasharray: "4,4"}),
      Plot.text([{x: currentTime, label: "NOW"}], {
        x: "x",
        y: () => labelY,
        text: "label",
        fill: "white",
        fontSize: 12,
        fontWeight: "bold",
        textAnchor: "start",
        dx: 3
      })
    ]
  });
}
```

<div class="grid grid-cols-1" style="grid-auto-rows: auto;">
  <div class="card">${resize((width) => temperaturePlot(allPeriods, {width}))}</div>
  <div class="card">${resize((width) => humidityPlot(allPeriods, {width}))}</div>
  <div class="card">${resize((width) => precipitationPlot(allPeriods, {width}))}</div>
  <div class="card">${resize((width) => timelinePlot(allPeriods, {width}))}</div>
</div>