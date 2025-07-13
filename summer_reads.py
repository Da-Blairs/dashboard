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

def sadie_read():
    return who_read(name="sadie")

def gavin_read():
    return who_read(name="gavin")

def zoe_read():
    return who_read(name="zoe")

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

import base64

def bar_chart_svg(counter, colors):
    if not counter:
        return "<svg></svg>"
    
    # Load and encode Raleway font
    with open("static/Raleway/Raleway-VariableFont_wght.ttf", "rb") as font_file:
        font_data = font_file.read()
        base64_font = base64.b64encode(font_data).decode('utf-8')
    
    # Configuration constants
    bar_height = 40
    bar_spacing = 15
    label_width = 70
    chart_width = 375
    margin_left = 0
    margin_top = 0
    text_padding = 15
    
    # Sort readers by count (descending)
    sorted_readers = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    max_count = max(counter.values()) if counter else 1
    
    # Calculate total SVG height
    total_bars = len(counter)
    total_height = margin_top * 2 + total_bars * (bar_height + bar_spacing)
    
    # Calculate total SVG width
    total_width = margin_left + label_width + chart_width
    
    # Create SVG with embedded font
    svg = [
        f'<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        f'  <style type="text/css">',
        f'    @font-face {{',
        f'        font-family: "Raleway";',
        f'        src: url("data:font/ttf;base64,{base64_font}") format("truetype");',
        f'        font-weight: 100 900;',
        f'        font-style: normal;',
        f'    }}',
        f'    .bar-label {{ font: 20px Raleway, sans-serif; dominant-baseline: middle; fill: #fee9c5; }}',
        f'    .count-label {{ font: bold 20px Raleway, sans-serif; fill: #fee9c5; }}',
        f'  </style>',
        f'</defs>'
    ]
    
    y_pos = margin_top
    color_idx = 0
    
    for reader, count in sorted_readers:
        # Calculate bar dimensions
        bar_width = (count / max_count) * chart_width
        
        # Add reader label on the left
        svg.append(f'<text x="{margin_left}" y="{y_pos + bar_height/2}" text-anchor="start" class="bar-label">{reader}</text>')
        
        # Add bar starting after the label
        color = colors[color_idx % len(colors)]
        bar_x = margin_left + label_width
        svg.append(f'<rect x="{bar_x}" y="{y_pos}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="4" ry="4" />')
        
        # Add count label inside the bar
        if bar_width > 50:
            # Inside the bar (right-aligned)
            svg.append(f'<text x="{bar_x + bar_width - text_padding}" y="{y_pos + 3 + bar_height/2}" text-anchor="end" class="count-label">{count}</text>')
        else:
            # Outside the bar (matching color)
            svg.append(f'<text x="{bar_x + bar_width + text_padding}" y="{y_pos + 3 + bar_height/2}" text-anchor="start" class="bar-label" fill="#fee9c5">{count}</text>')
        
        # Update positions
        y_pos += bar_height + bar_spacing
        color_idx += 1
    
    svg.append('</svg>')
    return '\n'.join(svg)

def summer_reads_bar_chart():
    counter = reader_count()
    colors = [
        '#4f9d50',  # Light Green
        '#d88036',  # Gold
        '#009391',  # Light Blue
        '#ce336f',  # Light Salmon
        '#d88036',  # Gold
    ]
    return bar_chart_svg(counter, colors)