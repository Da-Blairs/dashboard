import base64
from weather import weather_forecast
from flask import Flask, request, redirect, session, render_template, jsonify
import requests
import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
import os
import pytz
from summer_reads import summer_reads_total, summer_reads_svg, gwen_read, will_read
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
        gwen_read=gwen_read(),
        will_read=will_read()
    )

@app.route('/weather')
def weather():
    return weather_forecast()

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
