from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
def weather():
    # Fetch weather data from an API (replace with your actual API and logic)
    api_key = 'YOUR_API_KEY'
    city = 'London, Ontario'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_data = {
            'temperature': f"{data['main']['temp']}°C",
            'condition': data['weather'][0]['description']
        }
    else:
        weather_data = {
            'temperature': 'N/A',
            'condition': 'N/A'
        }

    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)
