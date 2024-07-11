import requests
import csv
from collections import Counter
from math import cos, sin, radians
from pie_chart_svg import pie_chart_svg

def who_read(name):
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"
    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Count rows where the first column starts with name
        name = name.strip().lower()
        return sum(1 for row in csv_reader if row and row[0].strip().lower() == name)
    else:
        return False

def gwen_read():
    return who_read(name="gwen")

def will_read():
    return who_read(name="will")

def reader_count():
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"

    # Fetch the CSV data from the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Create a Counter to count the books read by each person
        reader_count = Counter(row[0] for row in csv_reader)

        return reader_count
    else:
        return None


def summer_reads_total():
    # Fetch the CSV data from the URL
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRTRhgd6hpw5XvVvS-dRtPPcQQTVigYRk7zzKCXiEtrW-LbwJn9qI8LEa8RFnz5mNd95h8Zb_bjWkaJ/pub?gid=0&single=true&output=csv"
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Decode the content to text and split it into lines
        lines = response.content.decode('utf-8').splitlines()

        # Use csv.reader to read the lines
        csv_reader = csv.reader(lines)

        # Count the number of rows
        return sum(1 for row in csv_reader)
    else:
        return False

def summer_reads_svg():
    counter = reader_count()
    return pie_chart_svg(counter)
