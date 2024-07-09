import json
import os
import base64
import csv
import json
import datetime
import pytz
import streamlit as st 
import requests
import pprint
import threading
import gspread
from math import cos, radians, sin
from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit.components.v1 as components
from PIL import Image 
from time import sleep, strftime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from streamlit_calendar import calendar
from io import BytesIO
 
st.set_page_config(page_title="Blair Dashboard", layout="wide") 

#For the new weather service
USER_AGENT = "blairs.streamlit.app/1.0 (https://blairs.streamlit.app/contact)"

# Global cache for storing weather data and expiry timestamp
weather_cache = {
    "expires": datetime.datetime.utcnow() - datetime.timedelta(seconds=1),  # already expired
    "data": None
}

# Define the timezone for Toronto
toronto_tz = pytz.timezone('America/Toronto')
  
with open( "app/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

with open( "app/weather-icons.min.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """, unsafe_allow_html=True)

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables for client ID and client secret
client_id = os.getenv('GOOGLE_CREDENTIALS_CLIENT_ID') or st.secrets["GOOGLE_CREDENTIALS_CLIENT_ID"]
client_secret = os.getenv('GOOGLE_CREDENTIALS_CLIENT_SECRET') or st.secrets["GOOGLE_CREDENTIALS_CLIENT_SECRET"]
redirect_uri = os.getenv('GOOGLE_REDIRECT_URI') or st.secrets["GOOGLE_CREDENTIALS_CLIENT_SECRET"]

# Ensure environment variables are set
if not client_id or not client_secret or not redirect_uri:
    st.error("Please set the GOOGLE_CREDENTIALS_CLIENT_ID, GOOGLE_CREDENTIALS_CLIENT_SECRET, and GOOGLE_REDIRECT_URI environment variables.")
    st.stop()

# Define OAuth 2.0 configuration
credentials_info = {
    "web": {
        "client_id": client_id,
        "project_id": "your_project_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": client_secret,
        "redirect_uris": [redirect_uri],
    }
}

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# Get the current URL query parameters
query_params = st.query_params
if hasattr(query_params, "code"):
    query_string = "&".join(f"{key}={value}" for key, value in query_params.items())
    auth_response = f"{redirect_uri}?{query_string}"
    flow = Flow.from_client_config(credentials_info, SCOPES)
    flow.redirect_uri = redirect_uri
    flow.fetch_token(authorization_response=auth_response)

    creds = flow.credentials
    # Store the new credentials in an environment variable
    os.environ['GOOGLE_CREDENTIALS_TOKEN'] = creds.to_json()
    
    # Optionally, remove the query parameters from the URL to avoid repeated processing
    st.query_params.clear()

def get_credentials():
    creds = None
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
 
    # Check for existing credentials in environment variable
    token = os.getenv('GOOGLE_CREDENTIALS_TOKEN')
    if token:
        creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)
    
    # Refresh or perform OAuth flow if credentials are invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update the environment variable with the refreshed token
            os.environ['GOOGLE_CREDENTIALS_TOKEN'] = creds.to_json()
        else:
            flow = Flow.from_client_config(credentials_info, SCOPES)
            flow.redirect_uri = redirect_uri
            
            auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
            st.write(f"Please go to this URL for authorization: {auth_url}", auth_url)

    return creds

def midnight_toronto_iso():
    # Get the current UTC time
    now_utc = datetime.datetime.utcnow()
    
    # Define the Toronto timezone
    toronto_tz = pytz.timezone('America/Toronto')
    
    # Convert the current UTC time to Toronto time
    now_toronto = now_utc.astimezone(toronto_tz)
    
    # Replace the time to midnight
    midnight_toronto = now_toronto.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Convert to ISO format
    return midnight_toronto.isoformat()


def get_google_calendar_events():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        
    events_result = service.events().list(calendarId='primary', timeMin=midnight_toronto_iso(),
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    calendar_events = []
    for event in events:
        calendar_events.append({
            'title': event['summary'],
            'start': event['start'],
            'end': event['end'],
            'allday': 'date' in event['start']
        })
    return calendar_events

def get_event_dates(events):
    date_list = []
    for event in events:
        start_date = event['start'].get('date', event['start'].get('dateTime', 'ZoeTZoe').split('T')[0])
        end_date = event['end'].get('date', event['end'].get('dateTime', 'ZoeTZoe').split('T')[0])
        date_list.append(start_date)
        if start_date != end_date:
            #this should be a loop
            date_list.append(end_date)
    date_list = list(sorted(set(date_list)))
    return date_list

# Event icon dictionary
event_icons = {
    "swim": "<i class='fa-solid fa-person-swimming'></i>",
    "pool": "<i class='fa-solid fa-person-swimming'></i>",
    "among": "<i class='fa-solid fa-user-astronaut'></i>",
    "game": "<i class='fa-solid fa-dice'></i>",
    "birthday": "<i class='fa-solid fa-cake-candles'></i>",
    "d&d": "<i class='fa-solid fa-dragon'></i>",
    "oma": "<i class='fa-solid fa-face-grin-hearts'></i>",
    "goderich": "<i class='fa-solid fa-face-grin-hearts'></i>",
    "movie": "<i class='fa-solid fa-clapperboard'></i>",
    "plorin": "<i class='fa-solid fa-person-hiking'></i>",
    "exercise": "<i class='fa-solid fa-dumbbell'></i>",
    "dentist": "<i class='fa-solid fa-tooth'></i>",
    "zoub": "<i class='fa-solid fa-dog'></i>",
    "tv": "<i class='fa-solid fa-gamepad'></i>",
    "wincelsea": "<i class='fa-solid fa-tractor'></i>",
    "cottage": "<i class='fa-solid fa-house-chimney-window'></i>",
    "school": "<i class='fa-solid fa-pencil'></i>",
    "home": "<i class='fa-solid fa-suitcase'></i>",
    "camp": "<i class='fa-solid fa-campground'></i>",
 
}
    
def generate_events_markdown(events):
    date_list = get_event_dates(events)
    markdown_output = []
    
    for date in date_list:
        header = datetime.datetime.strptime(date, "%Y-%m-%d")
        markdown_output.append(f"<span class='date'><span>{header.strftime('%a')}</span><span>{header.strftime('%b %d')}</span></span>")
        
        for event in events:
            icon = ""
            event_title = event['title']
            for keyword, event_icon in event_icons.items():
                if keyword.lower() in event_title.lower():
                    icon = event_icon
                    break  # Stop after finding the first matching keyword
            
            if 'date' in event['start']:
                if event['start'].get('date') == date:
                    markdown_output.append(f'<div class="event"><span class="time">All Day</span><br>{icon} {event_title}</div>')
            
            if 'dateTime' in event['start']:
                if event['start']['dateTime'].split('T')[0] == date:
                    start_datetime = datetime.datetime.fromisoformat(event['start']['dateTime'][:-6])
                    start_time = start_datetime.strftime('%I:%M %p').lower().lstrip('0')
                    end_datetime = datetime.datetime.fromisoformat(event['end']['dateTime'][:-6])
                    end_time = end_datetime.strftime('%I:%M %p').lower().lstrip('0')
                    markdown_output.append(f'<div class="event"><span class="time">{start_time}-{end_time}</span><br>{icon} {event_title}</div>')

    return "\n".join(markdown_output)

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

def update_weather():
    lat = "42.9836"
    lng = "-81.2497"
    headers = {
        "User-Agent": USER_AGENT
    }
    
    # Check if cache is expired
    if datetime.datetime.utcnow() > weather_cache["expires"]:
        response_current = requests.get(f'https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lng}', headers=headers)
        
        if response_current.status_code == 200:
            result_current = response_current.json()
            temp = round(result_current["properties"]["timeseries"][0]["data"]["instant"]["details"]["air_temperature"])
            weathersymbol = result_current["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"]["symbol_code"]
            if weathersymbol in weather_icons:
                weathercode = weather_icons[weathersymbol]
            else:
                weathercode = "wi-alien"

            # Update cache
            weather_cache["data"] = (temp, weathercode)
            weather_cache["expires"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # assuming data is valid for 1 hour
            
            weather.markdown(f'<div id="weather">{temp}°C<i class="big-icon wi {weathercode}"></i></div>', unsafe_allow_html=True)
        else:
            weather.error("Failed to fetch weather data")
    else:
        # Use cached data
        temp, weathercode = weather_cache["data"]
        weather.markdown(f'<div id="weather">{temp}°C<i class="big-icon wi {weathercode}"></i></div>', unsafe_allow_html=True)

def old_update_weather():
    lat = "42.9836"
    lng = "-81.2497"
    response_current = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&daily=weather_code&timezone=America%2FNew_York')
    result_current = json.loads(response_current._content)

    current = result_current["current_weather"]
    temp = current["temperature"]
    weathercode = current["weathercode"]
    if weathercode == 0 or weathercode == 2: 
        pprint.pp(result_current["daily"]["weather_code"])
        weathercode = result_current["daily"]["weather_code"][0]
    is_day = current["is_day"]
    weather.markdown(f'<div id="weather">{temp}°C<i class="big-icon wi wi-wmo4680-{weathercode}"></i></div>', unsafe_allow_html=True)

def books_read(url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"):
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Count the number of rows
        return sum(1 for row in csv_reader)
    else:
        return False

def who_read(name):
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Count rows where the first column starts with name
        name = name.strip().lower();
        return sum(1 for row in csv_reader if row and row[0].strip().lower() == name)
    else:
        return False

def gwen_read():
    return who_read(name="gwen")

def will_read():
    return who_read(name="will")

def updateDinner():    
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId='d784fd49eb9057cf7c36c7d91c36b40613c3a86da4e351020ae0d1eaa4568cc2@group.calendar.google.com',
                                          timeMin=midnight_toronto_iso(),
                                          maxResults=2, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    dinners = []
    for event in events:
        dinners.append(event['summary'])

    dinner_today = dinners[0] if len(dinners) > 0 else "No plans"
    dinner_tomorrow = dinners[1] if len(dinners) > 1 else "No plans"

    dinner.markdown(f'<div id="food"><i class="fa-solid fa-utensils"></i><p><span class="count">Dinner Today</span><br><span>{dinner_today}</span></p><p><span class="count">Dinner Tomorrow</span><br><span>{dinner_tomorrow}</span></p></div>' , unsafe_allow_html= True)

def reader_count(url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"):
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Create a Counter to count the books read by each person
        reader_count = Counter(row[0] for row in csv_reader)

        return reader_count
    else:
        return None

def generate_donut_chart_svg_from_counter(counter, colors):
    total_books = sum(counter.values())
    labels = list(counter.keys())
    values = list(counter.values())

    # Adjust colors if there are more categories than provided colors
    if len(colors) < len(labels):
        colors = colors * len(labels)

    # Generate donut chart SVG
    cx, cy = 50, 50  # Center of the pie chart
    outer_radius = 50  # Outer radius of the pie chart
    inner_radius = 30  # Inner radius for the donut hole

    start_angle = 0
    segments = []

    for i, value in enumerate(values):
        angle = value / total_books * 360

        # Calculate outer arc points
        x1_outer = cx + outer_radius * cos(radians(start_angle))
        y1_outer = cy + outer_radius * sin(radians(start_angle))
        x2_outer = cx + outer_radius * cos(radians(start_angle + angle))
        y2_outer = cy + outer_radius * sin(radians(start_angle + angle))

        # Calculate inner arc points
        x1_inner = cx + inner_radius * cos(radians(start_angle))
        y1_inner = cy + inner_radius * sin(radians(start_angle))
        x2_inner = cx + inner_radius * cos(radians(start_angle + angle))
        y2_inner = cy + inner_radius * sin(radians(start_angle + angle))

        large_arc_flag = 1 if angle > 180 else 0

        # Construct path for the segment
        segment_path = f'''
            M {x1_outer},{y1_outer}
            A {outer_radius},{outer_radius} 0 {large_arc_flag},1 {x2_outer},{y2_outer}
            L {x2_inner},{y2_inner}
            A {inner_radius},{inner_radius} 0 {large_arc_flag},0 {x1_inner},{y1_inner}
            Z
        '''

        # Calculate position for text label
        label_angle = start_angle + angle / 2
        label_radius = inner_radius + (outer_radius - inner_radius) / 2
        label_x = cx + label_radius * cos(radians(label_angle))
        label_y = cy + label_radius * sin(radians(label_angle))

        # Create SVG elements for segment and label
        segment = f'<path d="{segment_path}" fill="{colors[i]}" />'
        label = f'<text font-size="5" x="{label_x}" y="{label_y}" text-anchor="middle" alignment-baseline="middle">{labels[i]}</text>'
        
        segments.append(segment)
        segments.append(label)

        start_angle += angle

    svg_content = f'''
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        {''.join(segments)}
    </svg>
    '''
    return svg_content

def render_svg_in_div(svg, div_id):
    """Renders the given svg string inside a <div> with the specified id."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    books_read = 9
    html = f'<div id="{div_id}"><span class="count">{books_read}</span><span>swim<br>days</span><img src="data:image/svg+xml;base64,{b64}" /></div>'
    st.write(html, unsafe_allow_html=True)

def render_donut_chart_from_counter(counter, colors, div_id='steps'):
    svg = generate_donut_chart_svg_from_counter(counter, colors)
    render_svg_in_div(svg, div_id)

    
# Streamlit setup
col3, col1, col0, col2 = st.columns((1,1,1.5,2), vertical_alignment="bottom")

with col3:
    weather = st.markdown(f'<div id="weather"></div>' , unsafe_allow_html= True)
    try: 
      update_weather()
    except:
      pass

    html_content = f'''
    <div id="movie-list">
        <i class="fa-solid fa-clapperboard"></i>
        <em>Movie List</em><br>
        July 4<br>
        <em>Frozen 2</em><br>
        July 11<br>
        <em>Kiki's Delivery Service</em><br>
        July 18<br>
        <em>Inside Out 2</em><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
 
    # Create a placeholder for the clock
    clock_placeholder = st.empty() 
    
with col0:
    # Create a container to hold the image
    image_container = st.empty()
    html_content = '''
    <style>
        iframe {
            border: none;
            width: 100%;
            height: 13em;
            border-radius: 20px;
        }
    </style>
    <iframe src="http://192.168.4.200:8081/frame.html" scrolling="no" frameborder="0" allowfullscreen></iframe>
    '''
    image_container.markdown(html_content, unsafe_allow_html=True)
    
    # Gwen Goals
    gwen_read = gwen_read()
    html_content = f'''
    <div id="gwen-goals">
        <i class="fa-solid fa-feather"></i>
        <em>Gwen Summer Goals</em>
        <i class="fa-solid fa-circle-check"></i> <label for="icecream">Eat Icecream</label><br>
        <i class="fa-regular fa-circle"></i> <label for="audiobooks">{gwen_read}/30 books read</label><br>
        <i class="fa-regular fa-circle"></i> <label for="dnd">1/4 D&D Sessions</label><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
 
    # William Goals
    will_read = will_read() + 2
    html_content = f'''
    <div id="william-goals">
        <i class="fa-solid fa-book-skull"></i>
        <em>Will Summer Goals</em>
        <i class="fa-solid fa-circle-check"></i> <label for="icecream">Eat Icecream</label><br>
        <i class="fa-regular fa-circle"></i> <label for="audiobooks">{will_read}/5 Ascendant Series</label><br>
        <i class="fa-regular fa-circle"></i> <label for="dnd">1/4 D&D Sessions</label><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Sadie Goals
    html_content = '''
    <div id="sadie-goals">
        <i class="fa-solid fa-heart"></i>
        <em>Sadie Summer Goals</em>
        <i class="fa-solid fa-circle-check"></i> <label for="icecream">Learn to Swim</label><br>
        <i class="fa-regular fa-circle"></i> <label for="audiobooks">Learn to Read</label><br>
        <i class="fa-solid fa-circle-check"></i> <label for="dnd">Play D&D</label><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
    
    

with col1:

    books_read = books_read()

    colors = [
        '#92d050',  # Light Green
        '#ffc000',  # Gold
        '#ff9999',  # Light Salmon
        '#b6d7a8',  # Pale Green
        '#cfe2f3',  # Light Blue
        '#ffcc99',  # Peach
        '#ffccff',  # Light Pink
        '#ffeb99',  # Light Yellow
        '#f0f8ff',  # Alice Blue
        '#ffe4c4'   # Bisque
    ]
    
    reader_counts = reader_count()
    if reader_counts:
        render_donut_chart_from_counter(reader_counts, colors)
    else:
        st.error("Failed to fetch reader counts.")

    st.markdown(f'<div id="swims"><span class="count">6</span><span>swim<br>days</span><i class="fa-solid fa-person-swimming"></i></div>' , unsafe_allow_html= True)
 
    dinner = st.markdown(f'<div id="food"><i class="fa-solid fa-utensils"></i><p><span class="count">Dinner Today</span><br><span>No plans</span></p><p><span class="count">Dinner Tomorrow</span><br><span>No plans</span></p></div>' , unsafe_allow_html= True)
    try: 
        updateDinner()
    except:
        pass
    
with col2:     
    # Get credentials
    creds = get_credentials()
    if not creds:
        st.error("Failed to obtain credentials.")
        st.stop()
    
    # Fetch events from Google Calendar
    calendar_events = []
    try:
      calendar_events = get_google_calendar_events()
    except:
      pass
    # pprint.pp(calendar_events)
    
    if calendar_events:
        calendar_markdown = generate_events_markdown(calendar_events)
        st.markdown(f'<div class="event-list">{calendar_markdown}</div>', unsafe_allow_html=True)
    else:
        st.write("No events found.")

# Function to update the image
def updateClock(use_colon=True):
    # Get the current time
    current_time = datetime.datetime.now(toronto_tz).strftime('%I:%M %p' if use_colon else '%I %M %p')
    current_date = datetime.datetime.now(toronto_tz).strftime('%b %d')
     # Update the clock placeholder with the current time
    clock_placeholder.markdown(f'<div class="clock-placeholder"><span class="time">{current_time}</span><br>{current_date}</div>', unsafe_allow_html=True)

# Run the schedule in a loop
def run_schedule():
    # Start an infinite loop to update the clock
    while True:
        current_time = datetime.datetime.now()
        current_minute = current_time.minute
        current_second = current_time.second

        try:
            updateClock(current_second % 2)
        except: 
            pass

        if current_minute % 5 == 0:
            try: 
                update_weather()
            except: 
                pass
            try:
                updateDinner()
            except: 
                pass    
        
        # Wait for 1 second before updating the time again
        sleep(1)

run_schedule()
