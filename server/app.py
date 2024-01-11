from flask import Flask, jsonify
import json

app = Flask(__name__)

# Read patterns from the JSON file
def get_patterns_from_db():
    with open('db.json', 'r') as file:
        patterns = json.load(file)
    return patterns

@app.route('/patterns', methods=['GET'])
def get_patterns():
	with open('db.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)

@app.route('/schema', methods=['GET'])
def get_filters():
	with open('schema.json', 'r') as file:
		data = json.load(file)

	return jsonify(data)

@app.route('/pattern/<int:id>', methods=['GET'])
def get_pattern(id):
	patterns = get_patterns_from_db()
	print(patterns)

	pattern = next((p for p in patterns if p.get('id') == id), None )

	if pattern:
		return jsonify(pattern)
	else:
		return jsonify({'error': 'Pattern not found'}), 404
