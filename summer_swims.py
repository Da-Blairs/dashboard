import requests
import csv
from collections import Counter
import datetime
from math import cos, sin, radians
from pie_chart_svg import pie_chart_svg

swim_days = 10

def summer_swims_total():
    global swim_days
    return swim_days

def swim_count():
    global swim_days

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