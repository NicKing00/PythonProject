from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["wetterdb"]
collection = db["abfragen"]

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def weather():
    city = request.json.get('city')

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=de"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        weather_data = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        collection.insert_one(weather_data)
        weather_data.pop('_id', None)
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Stadt nicht gefunden'}), 404

@app.route('/history', methods=['GET'])
def history():
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)

if __name__ == '__main__':
    collection.delete_many({})
    app.run()
