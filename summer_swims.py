import requests
import csv
from collections import Counter
import datetime
from math import cos, sin, radians
from pie_chart_svg import pie_chart_svg
import os

def get_swim_days_from_file():
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    file_path = os.path.join(static_folder, 'swim_days.txt')
    try:
        with open(file_path, 'r') as file:
            swim_days = int(file.read().strip())
            return swim_days
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading swim days from file: {e}")
        return 0  # Default value if file not found or invalid

def summer_swims_total():
    return get_swim_days_from_file()

def swim_count():
    swim_days = get_swim_days_from_file()

    summer_start = datetime.datetime(2024, 6, 29)

    # Get today's date
    today = datetime.datetime.now()

    # Calculate the difference in days
    days_summer = (today - summer_start).days

    no_swim = max(0, days_summer - swim_days)

    return Counter({'Swashbuckler': swim_days, 'Landlubber': no_swim})

def summer_swims_svg():
    counter = swim_count()
    return pie_chart_svg(counter)