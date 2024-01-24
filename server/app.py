from flask import Flask, jsonify
from flask_cors import CORS
import json, csv

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "https://ips-client-git-main-twaldorf.vercel.app"}})

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

@app.route('/schema', methods=['GET'])
def get_filters():
	# get column names
	with open('schema.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)

@app.route('/pattern/<string:Image>', methods=['GET'])
def get_pattern(Image):
	patterns = read_csv('./db.csv') 

	pattern = next( (p for p in patterns if p.get('Image') == Image), None )

	if pattern:
		return jsonify(pattern)
	else:
		return jsonify({'error': 'Pattern not found'}), 404

if __name__ == "__main__":
    app.run(debug=False)
