from flask import Flask, render_template, jsonify
import requests
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
def weather():
    USER_AGENT = "blairs.streamlit.app/1.0 (https://blairs.streamlit.app/contact)"

    # Global cache for storing weather data and expiry timestamp
    weather_cache = {
        "expires": datetime.datetime.utcnow() - datetime.timedelta(seconds=1),  # already expired
        "data": None
    }
    # Check if cache is expired
    if datetime.datetime.utcnow() > weather_cache["expires"]:
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

if __name__ == '__main__':
    app.run(debug=True)
