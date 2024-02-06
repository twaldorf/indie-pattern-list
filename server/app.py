from flask import Flask, jsonify
from flask_cors import CORS
import json, csv

csv_path = 'db.csv'

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://ips-client.vercel.app", "https://www.superpatternlist.com"]}})

@app.route('/patterns', methods=['GET'])
def index():
    patterns = read_csv('db.csv')
    return jsonify(patterns) 

def read_csv(file_path):
	patterns = []

	with open(file_path, newline='', encoding='utf-8') as csvfile:
			csv_reader = csv.DictReader(csvfile)
			for row in csv_reader:
				newrow = row
				for col in row:
					newrow[col] = newrow[col].split(',')
				patterns.append(newrow)
	return patterns

# @app.route('/patterns', methods=['GET'])
# def get_patterns():
# 	with open('db.json', 'r') as file:
# 		data = json.load(file)

# 	return jsonify(data)

def get_pattern_by_image(image_name):
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if row['Image'] == image_name:
                return row

    # If no matching row is found, return None
    return None



@app.route('/schema', methods=['GET'])
def get_filters():
	# get column names
	with open('schema.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)

@app.route('/pattern/<string:Image>', methods=['GET'])
def get_pattern(Image):
	patterns = read_csv('./db.csv') 

	pattern_data = get_pattern_by_image(Image)

	if not pattern_data:
		return jsonify({'error': 'Pattern not found'}), 404
	return jsonify(pattern_data)

if __name__ == "__main__":
    app.run(debug=False)
