from collections import Counter
from math import cos, sin, radians

def pie_chart_svg(counter):
    colors = [
        '#4f9d50',  # Light Green
        '#d88036',  # Gold
        '#009391',  # Light Blue
        '#ce336f',  # Light Salmon
        '#d88036',  # Gold
    ]

    total_books = sum(counter.values())
    labels = list(counter.keys())
    values = list(counter.values())

    # Adjust colors if there are more categories than provided colors
    if len(colors) < len(labels):
        colors = colors * len(labels)

    # Generate donut chart SVG
    cx, cy = 50, 50  # Center of the pie chart
    outer_radius = 50  # Outer radius of the pie chart
    inner_radius = 30  # Inner radius for the donut hole

    start_angle = 0
    segments = []

    for i, value in enumerate(values):
        angle = value / total_books * 360

        # Calculate outer arc points
        x1_outer = cx + outer_radius * cos(radians(start_angle))
        y1_outer = cy + outer_radius * sin(radians(start_angle))
        x2_outer = cx + outer_radius * cos(radians(start_angle + angle))
        y2_outer = cy + outer_radius * sin(radians(start_angle + angle))

        # Calculate inner arc points
        x1_inner = cx + inner_radius * cos(radians(start_angle))
        y1_inner = cy + inner_radius * sin(radians(start_angle))
        x2_inner = cx + inner_radius * cos(radians(start_angle + angle))
        y2_inner = cy + inner_radius * sin(radians(start_angle + angle))

        large_arc_flag = 1 if angle > 180 else 0

        # Construct path for the segment
        segment_path = f'''
            M {x1_outer},{y1_outer}
            A {outer_radius},{outer_radius} 0 {large_arc_flag},1 {x2_outer},{y2_outer}
            L {x2_inner},{y2_inner}
            A {inner_radius},{inner_radius} 0 {large_arc_flag},0 {x1_inner},{y1_inner}
            Z
        '''

        # Calculate position for text label
        label_angle = start_angle + angle / 2
        label_radius = inner_radius + (outer_radius - inner_radius) / 2
        label_x = cx + label_radius * cos(radians(label_angle))
        label_y = cy + label_radius * sin(radians(label_angle))

        # Create SVG elements for segment and label
        segment = f'<path d="{segment_path}" fill="{colors[i]}" />'
        label = f'<text fill="#fee9c5" font-family="Arial, Helvetica, sans-serif" font-size="5" x="{label_x}" y="{label_y}" text-anchor="middle" alignment-baseline="middle">{labels[i]}</text>'

        segments.append(segment)
        segments.append(label)

        start_angle += angle

    svg_content = f'''
    <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        {''.join(segments)}
    </svg>
    '''
    return svg_content