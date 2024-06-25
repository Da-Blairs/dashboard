import json
import os
import json
import datetime
import pytz
import streamlit as st
from time import sleep, strftime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from streamlit_calendar import calendar

st.set_page_config(layout="wide")

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables for client ID and client secret
client_id = os.getenv('GOOGLE_CREDENTIALS_CLIENT_ID', st.secrets["GOOGLE_CREDENTIALS_CLIENT_ID"])
client_secret = os.getenv('GOOGLE_CREDENTIALS_CLIENT_SECRET', st.secrets["GOOGLE_CREDENTIALS_CLIENT_SECRET"])
redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', st.secrets["GOOGLE_CREDENTIALS_CLIENT_SECRET"])

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

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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

# Streamlit setup
st.title("Blair Family Dashboard!")

col1, col2 = st.columns((1,2))

with col1:
    # Create a placeholder for the clock
    clock_placeholder = st.empty()

with col2:     
    # Get credentials
    creds = get_credentials()
    if not creds:
        st.error("Failed to obtain credentials.")
        st.stop()
    
    def get_google_calendar_events():
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
    
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
    
        calendar_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            calendar_events.append({
                'title': event['summary'],
                'start': start,
                'end': end,
            })
        return calendar_events
    
    # Fetch events from Google Calendar
    calendar_events = get_google_calendar_events()
    
    # Define calendar options
    calendar_options = {
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "list",
    }
    
    # Custom CSS
    custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """
    
    # Calendar component with events
    calendar_component = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
    st.write(calendar_component)

# Define the timezone for Toronto
toronto_tz = pytz.timezone('America/Toronto')

# Start an infinite loop to update the clock
while True:
    # Get the current time
    current_time = datetime.datetime.now(toronto_tz).strftime('%I:%M:%S %p')
    
    # Update the clock placeholder with the current time
    clock_placeholder.title(current_time)
    
    # Wait for 1 second before updating the time again
    sleep(1)
