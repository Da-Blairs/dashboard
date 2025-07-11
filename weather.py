import datetime
import requests
import json 
from flask import Flask, request, jsonify

def weather_forecast():
    USER_AGENT = "blairs.streamlit.app/1.0 (https://blairs.streamlit.app/contact)"

    weather_icons = {
        "clearsky_day" : "wi-day-sunny",
        "clearsky_night" : "wi-night-clear",
        "fair_day" : "wi-day-sunny-overcast",
        "fair_night" : "wi-night-alt-partly-cloudy",
        "partlycloudy_day" : "wi-day-cloudy",
        "partlycloudy_night" : "wi-night-alt-cloudy",
        "cloudy" : "wi-cloudy",
        "lightrainshowers_day" : "wi-day-showers",
        "lightrainshowers_night" : "wi-night-alt-showers",
        "rainshowers_day" : "wi-day-rain",
        "rainshowers_night" : "wi-night-alt-rain",
        "heavyrainshowers_day" : "wi-day-rain-wind",
        "heavyrainshowers_night" : "wi-night-alt-rain-wind",
        "lightsnowshowers_day" : "wi-day-snow",
        "lightsnowshowers_night" : "wi-night-alt-snow",
        "snowshowers_day" : "wi-day-snow-wind",
        "snowshowers_night" : "wi-night-alt-snow-wind",
        "heavysnowshowers_day" : "wi-day-snow-thunderstorm",
        "heavysnowshowers_night" : "wi-night-alt-snow-thunderstorm",
        "lightrain" : "wi-rain-mix",
        "rain" : "wi-rain",
        "heavyrain" : "wi-rain-wind",
        "lightsnow" : "wi-snow",
        "snow" : "wi-snow",
        "heavysnow" : "wi-snow-wind",
        "sleet" : "wi-sleet",
        "thunderstorm" : "wi-thunderstorm",
        "fog" : "wi-fog",
    }

    # Global cache for storing weather data and expiry timestamp
    weather_cache = {
        "expires": datetime.datetime.utcnow() - datetime.timedelta(seconds=1),  # already expired
        "data": None
    }
    # Check if cache is expired
    if datetime.datetime.utcnow() > weather_cache["expires"]:
        lat = "42.9836"
        lng = "-81.2497"
        headers = {"User-Agent": USER_AGENT}
        response_current = requests.get(
            f'https://api.met.no/weatherapi/locationforecast/2.0/complete?lat={lat}&lon={lng}',
            headers=headers
        )

        if response_current.status_code == 200:
            result_current = response_current.json()
            temp = round(result_current["properties"]["timeseries"][0]["data"]["instant"]["details"]["air_temperature"])
            uv = round(result_current["properties"]["timeseries"][0]["data"]["instant"]["details"]["ultraviolet_index_clear_sky"])
            weathersymbol = result_current["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"]["symbol_code"]
            weathercode = weather_icons.get(weathersymbol, "wi-alien")

            # Update cache
            weather_cache["data"] = (temp, uv, weathercode)
            weather_cache["expires"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # assuming data is valid for 1 hour
        else:
            return jsonify({"error": "Failed to fetch weather data"}), 500
    else:
        # Use cached data
        temp, uv, weathercode = weather_cache["data"]

    return jsonify({
        "temperature": f"{temp}°C",
        "uv": f"UV {uv}",
        "weathercode": weathercode
    })