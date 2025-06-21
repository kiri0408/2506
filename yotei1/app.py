from flask import Flask, jsonify, request, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')

DATA_FILE = 'schedules.json'

def load_schedules():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_schedules(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({'error': 'year and month parameters are required'}), 400
    try:
        year = int(year)
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return jsonify({'error': 'Invalid year or month'}), 400

    schedules = load_schedules()
    # Filter schedules for the requested year and month
    result = {}
    for date_str, text in schedules.items():
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if dt.year == year and dt.month == month:
                result[date_str] = text
        except ValueError:
            continue
    return jsonify(result)

@app.route('/api/schedules', methods=['POST'])
def post_schedule():
    data = request.get_json()
    if not data or 'date' not in data or 'text' not in data:
        return jsonify({'error': 'date and text are required'}), 400
    date_str = data['date']
    text = data['text']
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    schedules = load_schedules()
    if text.strip() == '':
        # Remove schedule if text is empty
        if date_str in schedules:
            del schedules[date_str]
    else:
        schedules[date_str] = text
    save_schedules(schedules)
    return jsonify({'message': 'Schedule saved'})

if __name__ == '__main__':
    app.run(debug=True)
