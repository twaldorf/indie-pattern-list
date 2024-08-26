from bson import ObjectId

def get_patterns_from_db(collection):
	patterns = list(collection.find({}))
	for pattern in patterns:
		pattern['_id'] = str(pattern['_id'])
	
	return patterns


def get_pattern_by_id(id, collection):
	pattern = collection.find_one({'_id': ObjectId(id)})
	pattern['_id'] = str(pattern['_id'])
	return pattern

