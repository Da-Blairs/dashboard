import requests
import csv
import json
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
            # Each row is a list, we assume the format is [date, movie_name]
            movie_data = {
                "date": row[0],
                "movie_name": row[1]
            }
            # Append the movie data to the movies list
            movies.append(movie_data)

        # Convert the list of movies to JSON
        movies_json = json.dumps(movies, indent=4)

        return movies_json
        
    else:
        return False
