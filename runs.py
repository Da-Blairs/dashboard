import requests
import requests
import csv
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQVWx6A9isQ8g3mYnjpvoLZKqNbaUn10PfYt6ORKzft63nNobKHWsJmRENt0yRK8T0jaT_0taaam6u1/pub?output=csv'

def run_list():
    global url
    
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)
        
        # Initialize a list to hold run data
        runs = []

        # Iterate through the rows in the CSV
        for row in csv_reader:
            # Each row is a list, assuming the format is [date, run_name]
            run_date_str = row[0]
            run_name = row[1]

            # try:
                # Parse the run date string into a datetime object
            run_date = datetime.strptime(run_date_str, '%Y-%m-%d')

            # Append the run data to the list
            runs.append({
                "date": run_date,
                "date_formatted": run_date,
                "run_name": run_name
            })
            # except ValueError:
                # Handle date format errors if any
                # pass

        # Sort the runs by date
        runs.sort(key=lambda x: x["date"])

        # Get today's date
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        upcoming_runs = [
            run for run in runs if run["date"].date() >= today
        ]

        if upcoming_runs:
            next_run = upcoming_runs[0]
            run_date = next_run["date"].date()
            
            if run_date == today:
                display_date = "Today"
            elif run_date == tomorrow:
                display_date = "Tomorrow"
            else:
                # Format as "On Tuesday", "On Wednesday", etc.
                display_date = f"On {run_date.strftime('%A')}"
            
            upcoming_run = [{
                "date": display_date,
                "run_name": next_run["run_name"]
            }]
        else:
            upcoming_run = []

        return jsonify({"runs": upcoming_run})

    else:
        return jsonify({"error": "Failed to retrieve data from CSV"}), response.status_code
