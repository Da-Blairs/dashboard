from flask import Flask, render_template, jsonify
import requests
import plotly.graph_objs as go
import plotly.offline as po

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
def weather():
    # Fetch weather data (replace with actual API call)
    weather_data = {
        'temperature': '22°C',
        'condition': 'Sunny'
    }
    return jsonify(weather_data)

@app.route('/plot')
def plot():
    # Example plot (replace with your plot logic)
    data = [go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])]
    plot_div = po.plot(data, output_type='div')
    return render_template('plot.html', plot_div=plot_div)

if __name__ == '__main__':
    app.run(debug=True)
