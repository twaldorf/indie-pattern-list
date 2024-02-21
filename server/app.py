from flask import Flask, jsonify, request
from flask_cors import CORS
import json, csv

csv_path = 'db.csv'

app = Flask(__name__)

origins = [
	"https://ips-client.vercel.app",
	"https://www.superpatternlist.com",
	"http://localhost:5173"
]

CORS(app, resources={r"/*": {"origins": origins}})


@app.route('/patterns', methods=['GET'])
def index():
		# paginate
		page_index = int(request.args.get('page', 1))
		page_size = int(request.args.get('page_length', 50))
		front = (page_index - 1) * page_size
		back = front + page_size

		patterns = read_csv('db.csv')[front : back]

		#sort 
		sortBy = request.args.get('SortBy')
		
		if sortBy == 'Cost':
			for row in patterns:
				if row['Cost'][0] != '':
					row['Cost'] = float(row['Cost'][0]) 
				else:
					row['Cost'] = 0.0
			if sortBy:
				patterns.sort(key=lambda x: x.get( sortBy, ''))

		return jsonify(patterns)


def read_csv(file_path):
	patterns = []

	with open(file_path, newline='', encoding='utf-8') as csvfile:
			csv_reader = csv.DictReader(csvfile)
			for row in csv_reader:
				newrow = row
				for col in row:
					newrow[col] = newrow[col].split(',')
					newrow[col] = [entry.strip() for entry in newrow[col]]
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
