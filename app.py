import base64
from flask import Flask, request, redirect, session, render_template, jsonify
import requests
import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os
import pytz
from summer_reads import summer_reads_total, summer_reads_svg
from summer_swims import summer_swims_total, summer_swims_svg
from gcal import google_authorize, google_callback, gcal_dinner, gcal_work, gcal_events

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Read CSS files
def read_css(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@app.route('/')
def home():
    if 'credentials' not in session:
        return redirect('/authorize')
    credentials = Credentials(**session['credentials'])
    styles_css = read_css(os.path.join(app.root_path, 'static', 'style.css'))
    weather_icons_css = read_css(os.path.join(app.root_path, 'static', 'weather-icons.min.css'))

    toronto_tz = pytz.timezone('America/Toronto')
    current_date = datetime.datetime.now(toronto_tz).strftime('%b %d')
    return render_template(
        'index.html',
        styles_css=styles_css,
        weather_icons_css=weather_icons_css,
        current_date=current_date,
        gwen_read=6,
        will_read=3
    )

@app.route('/weather')
def weather():
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

@app.route('/dinner')
def dinner():
    return gcal_dinner()

@app.route('/work')
def work():
    return gcal_work()

@app.route('/events')
def event():
    return gcal_events()

@app.route('/summer_reads')
def summer_reads():
    count = summer_reads_total()
    svg = summer_reads_svg()
    svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")

    return jsonify({'count': count, 'svg': svg})

@app.route('/summer_swims')
def summer_swims():
    count = summer_swims_total()
    svg = summer_swims_svg()
    svg = base64.b64encode(svg.encode('utf-8')).decode("utf-8")

    return jsonify({'count': count, 'svg': svg})

@app.route('/authorize')
def authorize():
    return google_authorize(redirect)

@app.route('/callback')
def callback():
    return google_callback(request, redirect)


if __name__ == '__main__':
    print("Running on host:", app.config['SERVER_NAME'])
    print("Running on port:", app.config['SERVER_PORT'])
    app.run(host='::', port=5000, debug=True)
