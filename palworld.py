import requests
import csv
import json
from datetime import datetime
from flask import Flask, jsonify
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSADEBeWEIvwDyLvn4Mk6C0szFCJ555miRjjSEXchKvQEUviIJldsg9r-CsDtYS2A_cbXwDeFpSws6Y/pub?output=csv'

def palworld_list():
    global url
    
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)
        
        # Initialize a list to hold movie data
        palworld = []

        # Iterate through the rows in the CSV
        for row in csv_reader:
            try:
                # Each row is a list, assuming the format is [person, palworld, done]
                # Append the movie data to the list
                palworld.append({
                    "person": row[0],
                    "palworld": row[1],
                    "status": 1 if (len(row) > 2 and row[2]) else 0
                })
            except ValueError:
                # Handle date format errors if any
                pass

        # Sort the palworld by date
        palworld.sort(key=lambda x: x["person"])
        return jsonify({"palworld": upcoming_palworld})

    else:
        return jsonify({"error": "Failed to retrieve data from CSV"}), response.status_code
