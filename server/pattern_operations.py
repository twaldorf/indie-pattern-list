import csv
from bson import ObjectId

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

def prep_patterns(patterns):
	for pattern in patterns:
		pattern['_id'] = str(pattern['_id'])
	return patterns