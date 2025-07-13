import requests
import csv
import json
from datetime import datetime
from flask import Flask, jsonify
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRXapWW-J0RYgfA4lbXIgV0tDDSDrMFt7aB8vmy0GBagRTTi0iMWxIhM9NIsI9DTsPLVFSo96VhpdT1/pub?output=csv'

def game_list():
    global url
    
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)
        
        # Initialize a list to hold game data
        games = []

        # Iterate through the rows in the CSV
        for row in csv_reader:
            # Each row is a list, assuming the format is [date, game_name]
            game_date_str = row[0]
            game_name = row[1]

            try:
                # Parse the game date string into a datetime object
                game_date = datetime.strptime(game_date_str, '%Y-%m-%d')

                # Append the game data to the list
                games.append({
                    "date": game_date,
                    "date_formatted": game_date,
                    "game_name": game_name
                })
            except ValueError:
                # Handle date format errors if any
                pass

        # Sort the games by date
        games.sort(key=lambda x: x["date"])

        # Filter out past games and get the next 4 upcoming games
        upcoming_games = [
            {"date": game["date"].strftime('%B %e'), "game_name": game["game_name"]}
            for game in games if game["date"].date() >= datetime.now().date()
        ][:2]

        return jsonify({"games": upcoming_games})

    else:
        return jsonify({"error": "Failed to retrieve data from CSV"}), response.status_code
