from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'diary.json'

def load_diary():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_diary(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return "Test route is working"
@app.route('/api/diary', methods=['GET'])
def get_diary():
    year = request.args.get('year')
    month = request.args.get('month')
    if not year or not month:
        return jsonify({'error': 'year and month parameters are required'}), 400
    diary = load_diary()
    # Filter entries for the requested year and month
    result = {}
    for date_str, content in diary.items():
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if dt.year == int(year) and dt.month == int(month):
                result[date_str] = content
        except ValueError:
            continue
    return jsonify(result)

@app.route('/api/diary', methods=['POST'])
def save_diary_entry():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    date = data.get('date')
    content = data.get('content')
    if not date or content is None:
        return jsonify({'error': 'date and content fields are required'}), 400
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'date must be in YYYY-MM-DD format'}), 400
    diary = load_diary()
    diary[date] = content
    save_diary(diary)
    return jsonify({'message': 'Diary entry saved'})

if __name__ == '__main__':
    app.run(debug=True)
