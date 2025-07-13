import requests
import csv
import json
from datetime import datetime
from flask import Flask, jsonify
from collections import Counter

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTW9iBHCZxmlNNVbYycml0fGrJZ-g1gAn3uo3yt2sBkd90weEJ9jVgyMvgu28sQfeOMHSOwhDD5yZuV/pub?gid=0&single=true&output=csv'

def movie_list():
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
        movies = []

        # Iterate through the rows in the CSV
        for row in csv_reader:
            # Each row is a list, assuming the format is [date, movie_name]
            movie_date_str = row[0]
            movie_name = row[1]

            try:
                # Parse the movie date string into a datetime object
                movie_date = datetime.strptime(movie_date_str, '%Y-%m-%d')

                # Append the movie data to the list
                movies.append({
                    "date": movie_date,
                    "date_formatted": movie_date,
                    "movie_name": movie_name
                })
            except ValueError:
                # Handle date format errors if any
                pass

        # Sort the movies by date
        movies.sort(key=lambda x: x["date"])

        # Filter out past movies and get the next 4 upcoming movies
        upcoming_movies = [
            {"date": movie["date"].strftime('%B %e'), "movie_name": movie["movie_name"]}
            for movie in movies if movie["date"].date() >= datetime.now().date()
        ][:2]

        return jsonify({"movies": upcoming_movies})

    else:
        return jsonify({"error": "Failed to retrieve data from CSV"}), response.status_code
