# google_calendar.py

import json
import os
import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables for client ID and client secret
client_id = os.getenv('GOOGLE_CREDENTIALS_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CREDENTIALS_CLIENT_SECRET')
redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')

# Ensure environment variables are set
if not client_id or not client_secret or not redirect_uri:
    raise ValueError("Please set the GOOGLE_CREDENTIALS_CLIENT_ID, GOOGLE_CREDENTIALS_CLIENT_SECRET, and GOOGLE_REDIRECT_URI environment variables.")

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

def get_credentials(query_params):
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

            if 'code' in query_params:
                query_string = "&".join(f"{key}={value}" for key, value in query_params.items())
                auth_response = f"{redirect_uri}?{query_string}"
                flow.fetch_token(authorization_response=auth_response)
                creds = flow.credentials
                # Store the new credentials in an environment variable
                os.environ['GOOGLE_CREDENTIALS_TOKEN'] = creds.to_json()
            else:
                auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
                return None, auth_url

    return creds, None

def get_google_calendar_events(creds):
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
