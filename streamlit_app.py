import json
import os
import csv
import json
import datetime
import pytz
import streamlit as st 
import requests
import pprint
import threading
import gspread
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
                                          maxResults=7, singleEvents=True,
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

def update_weather():
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
    
    

# Streamlit setup
col3, col1, col0, col2 = st.columns((1,1,1.5,2))

with col0:
    # Create a container to hold the image
    image_container = st.empty()
    
    # Gwen Goals
    gwen_read = gwen_read()
    html_content = f'''
    <div id="gwen-goals">
        <i class="fa-solid fa-feather"></i>
        <em>Gwen Summer Goals</em>
        <input type="checkbox" checked="checked" id="icecream"> <label for="icecream">Eat Icecream</label><br>
        <input type="checkbox" id="audiobooks"> <label for="audiobooks">{gwen_read}/30 books read</label><br>
        <input type="checkbox" id="dnd"> <label for="dnd">1/4 D&D Sessions</label><br>
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
        <input type="checkbox" checked="checked" id="icecream"> <label for="icecream">Eat Icecream</label><br>
        <input type="checkbox" id="audiobooks"> <label for="audiobooks">{will_read}/5 Ascendant Series</label><br>
        <input type="checkbox" id="dnd"> <label for="dnd">1/4 D&D Sessions</label><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Sadie Goals
    html_content = '''
    <div id="sadie-goals">
        <i class="fa-solid fa-heart"></i>
        <em>Sadie Summer Goals</em>
        <input type="checkbox" checked="checked" id="icecream"> <label for="icecream">Learn to Swim</label><br>
        <input type="checkbox" id="audiobooks"> <label for="audiobooks">Learn to Read</label><br>
        <input type="checkbox" checked="checked" id="dnd"> <label for="dnd">Play D&D</label><br>
    </div>
    '''
    
    # Render the HTML content
    st.markdown(html_content, unsafe_allow_html=True)
    
    

with col1:

    weather = st.markdown(f'<div id="weather"></div>' , unsafe_allow_html= True)
    try: 
      update_weather()
    except:
      pass

    books_read = books_read()
    if(books_read):
        st.markdown(f'<div id="steps"><span><span class="count">{books_read}</span>&nbsp;summer reads</span><span></span><i class="fa-solid fa-book"></i></div>' , unsafe_allow_html= True)
    
    #st.markdown(f'<div id="swims"><span class="count">0</span><span>hours swimming</span></div>' , unsafe_allow_html= True)

    dinner = st.markdown(f'<div id="food"><i class="fa-solid fa-utensils"></i><p><span class="count">Dinner Today</span><br><span>No plans</span></p><p><span class="count">Dinner Tomorrow</span><br><span>No plans</span></p></div>' , unsafe_allow_html= True)
    
    # Create a placeholder for the clock
    clock_placeholder = st.empty() 

    
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

# Define the timezone for Toronto
toronto_tz = pytz.timezone('America/Toronto')

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
    
updateDinner()

# Function to update the image
def updateImage():
    # Get the image from the URL
    response = requests.get(f'http://generationgeneration.ca/frame.jpg')
    image = Image.open(BytesIO(response.content))
    # Display the image in the container
    image_container.image(image, use_column_width=True)
 
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

        if current_second % 2 == 0:
            try:
                updateImage()
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

updateImage()
run_schedule()

