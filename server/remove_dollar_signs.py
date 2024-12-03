from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['patternlistdev']

collection = db['patterns']

# Update all documents to remove dollar signs from the 'price' field
collection.update_many(
    { 'price': { '$type': 'string' } },  # Match documents where 'price' is a string
    [
        { 
            '$set': { 
                'price': { 
                    '$replaceAll': { 
                        'input': '$price', 
                        'find': '$', 
                        'replacement': '' 
                    }
                }
            }
        }
    ]
)

print("Dollar signs removed from 'price' field.")
