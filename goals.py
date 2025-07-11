import requests
import csv
import json
from datetime import datetime
from flask import Flask, jsonify
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSADEBeWEIvwDyLvn4Mk6C0szFCJ555miRjjSEXchKvQEUviIJldsg9r-CsDtYS2A_cbXwDeFpSws6Y/pub?output=csv'

def goal_list():
    global url
    
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)
        
        # Initialize a DICTIONARY to hold goals grouped by person
        people_goals = {}

        # Iterate through the rows in the CSV
        for row in csv_reader:
            try:
                person = row[0]
                goal_text = row[1]
                # Status is 1 if row[2] exists and is not empty, otherwise 0
                status = 1 if (len(row) > 2 and row[2].strip()) else 0
                
                # If we haven't seen this person before, create an entry
                if person not in people_goals:
                    people_goals[person] = {
                        "person": person,
                        "goals": []
                    }
                
                # Add the goal to this person's list
                people_goals[person]["goals"].append({
                    "goal": goal_text,
                    "status": status
                })
            except (IndexError, ValueError):
                # Skip rows that don't have enough columns or have format issues
                continue
        
        return jsonify({"goals": people_goals})

    else:
        return jsonify({"error": "Failed to retrieve data from CSV"}), response.status_code