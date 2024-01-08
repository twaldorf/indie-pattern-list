from flask import Flask, jsonify
import json

app = Flask(__name__)

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