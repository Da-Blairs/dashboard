import datetime
from dotenv import load_dotenv
import json
import os
import pprint
import pytz
from flask import Flask, request, redirect, session, render_template, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

toronto_tz = pytz.timezone('America/Toronto')

# Fetch environment variables for client ID and client secret
client_id = os.getenv('GOOGLE_CREDENTIALS_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CREDENTIALS_CLIENT_SECRET')
redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
token = os.getenv('GOOGLE_CREDENTIALS_TOKEN')
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

# Allow insecure transport for development purposes
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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


CREDENTIALS_FILE = 'credentials.json'

def save_credentials_to_file(credentials):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials_to_dict(credentials), f)

def load_credentials_from_file():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials_data = json.load(f)
            return Credentials.from_authorized_user_info(credentials_data)
    return None

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_credentials():
    creds = None

    # Check if credentials exist in the session
    if 'credentials' in session:
        creds = Credentials(**session['credentials'])

    # Check for existing credentials in the JSON file
    if not creds or not creds.valid:
        creds = load_credentials_from_file()

    # Refresh the token if it's expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save the refreshed credentials to the session and JSON file
            session['credentials'] = creds_to_dict(creds)
            save_credentials_to_file(creds)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    # Perform OAuth flow if credentials are invalid or do not exist
    if not creds or not creds.valid:
        return None

    return creds

def google_authorize(redirect):
    global redirect_uri
    global credentials_info
    global SCOPES

    flow = Flow.from_client_config(
        credentials_info,
        scopes=SCOPES
    )

    flow.redirect_uri = redirect_uri
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

def google_callback(request, redirect):
    flow = Flow.from_client_config(credentials_info, scopes=SCOPES)
    flow.redirect_uri = redirect_uri

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    # Save credentials to file
    save_credentials_to_file(credentials)

    return redirect('/')

def midnight_toronto_iso():
    global toronto_tz

    # Current Toronto time
    now_toronto = datetime.datetime.now(toronto_tz)

    # Replace the time to midnight
    midnight_toronto = now_toronto.replace(hour=0, minute=0, second=0, microsecond=0)

    # Convert to ISO format
    return midnight_toronto.isoformat()

def day_end_iso():
    global toronto_tz
    # Get the current Toronto time
    now_toronto = datetime.datetime.now(toronto_tz)

    # Replace the time to midnight + add a day
    end_of_today = now_toronto.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

    # Convert to ISO format
    return end_of_today.isoformat()

def tomorrow_iso():
    global toronto_tz
    # Get the current Toronto time
    now_toronto = datetime.datetime.now(toronto_tz)

    # Replace the time to midnight + add a day
    end_of_tomorrow = now_toronto.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=2)

    # Convert to ISO format
    return end_of_tomorrow.isoformat()



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
    "grad": "<i class='fa-solid fa-graduation-cap'></i>",
    "retire": "<i class='fa-solid fa-umbrella-beach'></i>",
    "babysit": "<i class='fa-solid fa-children'></i>",
    "québec": "<i class='fa-solid fa-compass'></i>",
    "quebec": "<i class='fa-solid fa-compass'></i>",
    "sleepover": "<i class='fa-solid fa-moon'></i>",
    "c25k": "<i class='fa-solid fa-person-running'></i>",
    "western": "<i class='fa-solid fa-building-columns'></i>",
    "recital": "<i class='fa-solid fa-music'></i>",
    "d&d": "<i class='fa-solid fa-dragon'></i>",
    "d&d": "<i class='fa-brands fa-d-and-d'></i>",
    "oma": "<i class='fa-solid fa-face-grin-hearts'></i>",
    "goderich": "<i class='fa-solid fa-face-grin-hearts'></i>",
    "movie": "<i class='fa-solid fa-clapperboard'></i>",
    "plorin": "<i class='fa-solid fa-person-hiking'></i>", 
    "hike": "<i class='fa-solid fa-person-hiking'></i>",
    "exercise": "<i class='fa-solid fa-dumbbell'></i>",
    "dentist": "<i class='fa-solid fa-tooth'></i>",
    "zoub": "<i class='fa-solid fa-dog'></i>",
    "tv": "<i class='fa-solid fa-gamepad'></i>",
    "wincelsea": "<i class='fa-solid fa-tractor'></i>",
    "cottage": "<i class='fa-solid fa-house-chimney-window'></i>",
    "school": "<i class='fa-solid fa-pencil'></i>",
    "home": "<i class='fa-solid fa-suitcase'></i>",
    "camp": "<i class='fa-solid fa-campground'></i>",
    "tania": "<i class='fa-solid fa-fire'></i>",

}

def gcal_events():
    url = 'e47c4628e6961718557b31f77a397c46c53367a2b87ca027ceb7b1aff272b546@group.calendar.google.com'
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId=url,
        timeMin=midnight_toronto_iso(),
        maxResults=15,
        singleEvents=True,
        timeZone='America/Toronto',
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    date_list = get_event_dates(events)
    html_output = []

    for date in date_list:
        header = datetime.datetime.strptime(date, "%Y-%m-%d")
        header_toronto = toronto_tz.localize(header)
    
        # Skip if before midnight Toronto time
        if header_toronto.isoformat() < midnight_toronto_iso():
            continue

        html_output.append(f"<span class='date'><span>{header.strftime('%A')}, {header.strftime('%B %d')}</span><span></span></span>")

        for event in events:
            icon = ""
            event_title = event['summary']
            for keyword, event_icon in event_icons.items():
                if keyword.lower() in event_title.lower():
                    icon = event_icon
                    break  # Stop after finding the first matching keyword

            if 'date' in event['start']:
                if event['start'].get('date') == date:
                    html_output.append(f'<div class="event">All Day<br>{icon} <span class="title">{event_title}</span></div>')

            if 'dateTime' in event['start']:
                start_datetime = datetime.datetime.fromisoformat(event['start']['dateTime'])
                start_time = start_datetime.strftime('%I:%M %p').lower().lstrip('0')
                end_datetime = datetime.datetime.fromisoformat(event['end']['dateTime'])
                end_time = end_datetime.strftime('%I:%M %p').lower().lstrip('0')
                    
                if event['start']['dateTime'].split('T')[0] == date and event['end']['dateTime'].split('T')[0] == date:
                    html_output.append(f'<div class="event">{start_time}-{end_time}<br>{icon}<span class="title">{event_title}</span></div>')

                elif event['start']['dateTime'].split('T')[0] <= date and event['end']['dateTime'].split('T')[0] == date:
                    html_output.append(f'<div class="event">Until {end_time}<br>{icon}<span class="title">{event_title}</span></div>')

                elif event['start']['dateTime'].split('T')[0] == date and event['end']['dateTime'].split('T')[0] >= date:
                    html_output.append(f'<div class="event">Starting at {start_time}<br>{icon}<span class="title">{event_title}</span></div>')
                
                elif event['start']['dateTime'].split('T')[0] < date and event['end']['dateTime'].split('T')[0] > date:
                    html_output.append(f'<div class="event">Ongoing<br>{icon}<span class="title">{event_title}</span></div>')

    return jsonify({'html': "\n".join(html_output)})

def gcal_dinner():
    url = 'd784fd49eb9057cf7c36c7d91c36b40613c3a86da4e351020ae0d1eaa4568cc2@group.calendar.google.com'
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId=url,
                                          timeMin=midnight_toronto_iso(),
                                          timeMax=tomorrow_iso(),
                                          maxResults=2,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    dinners = []
    for event in events:
        dinners.append(event['summary'])

    dinner_today = dinners[0] if len(dinners) > 0 else "No plans"
    dinner_tomorrow = dinners[1] if len(dinners) > 1 else "No plans"

    return jsonify({
        "dinner_today": dinner_today,
        "dinner_tomorrow": dinner_tomorrow,
    })

def gcal_work():
    url = 'e8342c59acacdfd8607daa42f2696eee46f300f96ac7d1149c484502c04102a8@group.calendar.google.com'
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId=url,
                                          timeMin=midnight_toronto_iso(),
                                          timeMax=day_end_iso(),
                                          maxResults=2,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    events = events_result.get('items', [])
    work = []
    for event in events:
        work.append(event['summary'])

    if work:
        return jsonify({
                "work1": work[0],
                "work2": work[1],
            })

    return jsonify({})
