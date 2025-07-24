import json
import requests
import sys

# Array of coordinates [latitude, longitude, location_name]
coordinates = [
    [38.89828491815215, -77.03054017444893, "1310 G St NW, Washington, DC 20005"],
    [39.10251451643185, -84.50973468978093, "550 Main St, Cincinnati, OH 45202"],
    [39.05715964049667, -76.9008405748496, "6000 Ammendale Rd, Beltsville, MD 20705"]
]

forecasts = []

for latitude, longitude, location_name in coordinates:
    try:
        # Get the weather station for this location
        station_response = requests.get(f"https://api.weather.gov/points/{latitude},{longitude}")
        station_response.raise_for_status()
        station = station_response.json()
        
        # Get the forecast for this location
        forecast_response = requests.get(station["properties"]["forecastHourly"])
        forecast_response.raise_for_status()
        forecast = forecast_response.json()
        
        # Add location information to the forecast
        forecast_with_location = {
            "location": {
                "name": location_name,
                "latitude": latitude,
                "longitude": longitude
            },
            "forecast": forecast
        }
        
        forecasts.append(forecast_with_location)
        
    except requests.exceptions.RequestException as e:
        # If there's an error, add an error entry instead of crashing
        error_entry = {
            "location": {
                "name": location_name,
                "latitude": latitude,
                "longitude": longitude
            },
            "error": str(e),
            "forecast": None
        }
        forecasts.append(error_entry)

json.dump(forecasts, sys.stdout)