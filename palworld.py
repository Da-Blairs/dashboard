import requests
from flask import Flask, jsonify

app = Flask(__name__)
SERVER_URL = "http://192.168.4.200:3000/player-count"

def palworld_list():

    try:
        response = requests.get(SERVER_URL, timeout=5)
        response.raise_for_status()
        players = response.json()
        # Extract just the names from each player object
        player_names = [player['name'] for player in players if 'name' in player]
        return {
            "total_players": len(player_names),
            "player_list": player_names
        }
    except Exception as e:
        return False
