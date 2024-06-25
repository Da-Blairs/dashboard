import os
import datetime
import streamlit as st
from time import sleep
from datetime import datetime
import pytz
from google_calendar import get_credentials, get_google_calendar_events
from streamlit_calendar import calendar

st.set_page_config(layout="wide")
st.title("Blair Family Dashboard")

# Define columns
col1, col2, col3 = st.columns((2, 1, 1))

# Streamlit setup
with col1:
    # Create a placeholder for the clock
    clock_placeholder = st.empty()

with col2:
    # Get credentials and handle OAuth flow if needed
    creds, auth_url = get_credentials(st.experimental_get_query_params())
    if auth_url:
        st.write(f"Please go to this URL for authorization: {auth_url}", auth_url)
        st.stop()
    elif not creds:
        st.error("Failed to obtain credentials.")
        st.stop()

    # Fetch events from Google Calendar
    calendar_events = get_google_calendar_events(creds)

    # Define calendar options
    calendar_options = {
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:00:00",
        "initialView": "list",
    }

    # Custom CSS
    custom_css = """
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
    current_time = datetime.now(toronto_tz).strftime('%I:%M:%S %p')

    # Update the clock placeholder with the current time
    clock_placeholder.write(current_time)

    # Wait for 1 second before updating the time again
    sleep(1)
