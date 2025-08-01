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
import pprint
import pytz
from runs import run_list
from movies import movie_list
from games import game_list
from goals import goal_list
from palworld import palworld_list
from summer_reads import summer_reads_total, summer_reads_svg, summer_reads_bar_chart, gwen_read, will_read, sadie_read, zoe_read, gavin_read
from summer_swims import summer_swims_total, summer_swims_svg
from gcal import get_credentials, google_authorize, google_callback, gcal_dinner, gcal_work, gcal_events

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Read CSS files
def read_css(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@app.route('/')
def home():
    credentials = get_credentials()
    if not credentials:
        return redirect('/authorize')

    styles_css = read_css(os.path.join(app.root_path, 'static', 'css', 'style.css'))
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

@app.route('/runs')
def runs():
    runs_data = run_list()
    if runs_data:
        runs = runs_data.json
        html_content = render_template('run_list.html', runs=runs['runs'])
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch movie list."

@app.route('/movies')
def movies():
    movies_data = movie_list()
    if movies_data:
        movies = movies_data.json  # Assuming movie_list() returns a response object
        html_content = render_template('movie_list.html', movies=movies['movies'])
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch movie list."

@app.route('/games')
def games():
    games_data = game_list()
    if games_data:
        games = games_data.json
        html_content = render_template('game_list.html', games=games['games'])
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch game list."

@app.route('/goals')
def goals():
    goals_data = goal_list()
    if goals_data:
        goals = goals_data.json  # Assuming goals_list() returns a response object
        html_content = render_template('goals.html', 
            goals=goals['goals'], 
            gwen_read=gwen_read(),
            sadie_read=sadie_read(),
            zoe_read=zoe_read(),
            gavin_read=gavin_read(),
            will_read=will_read()
        )
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch goal list."

@app.route('/palworld')
def palworld():
    palworld_data = palworld_list()
    if palworld_data:
        palworld = palworld_data.json
        html_content = render_template('palworld.html', palworld=palworld['palworld'])
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch palworld data."

@app.route('/weather')
def weather():
    return weather_forecast()

@app.route('/dinner')
def dinner():
    return gcal_dinner()

@app.route('/work')
def work():
    work_data = gcal_work()
    if work_data:
        work = work_data.json
        html_content = ''
        if work:
            html_content = render_template('work.html', work1=work['work1'], work2=work['work2'])
        return jsonify({'html': html_content})
    else:
        return "Failed to fetch work data"

@app.route('/events')
def event():
    return gcal_events()

@app.route('/summer_reads')
def summer_reads():
    count = summer_reads_total()
    svg = summer_reads_svg()
    svg = summer_reads_bar_chart()
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

@app.route('/save_dashboard', methods=['POST'])
def save_dashboard():
    # Get plain text content from request body
    content = request.data.decode('utf-8')
    
    # Hardcoded filename
    filename = "dashboard_content.txt"
    save_path = os.path.join('saved_files', filename)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save content to file
    try:
        with open(save_path, 'w') as f:
            f.write(content)
        return jsonify({
            'message': 'Dashboard content saved successfully',
            'path': save_path
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Running on host:", app.config['SERVER_NAME'])
    print("Running on port:", app.config['SERVER_PORT'])
    app.run(host='::', port=5000, debug=True)
