from pymongo import MongoClient
import pytest 
from .app import create_app
from bson import ObjectId
import json
from .json_loader import load_json

# init a new test database
# get data from a json file (using json_loader.py)
# test each route
# test search with dirty
# test category and page counts with bananas inputs
# test pen operations

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'MONGO_URI': 'mongodb://127.0.0.1:27017',
        'DB_NAME': 'patternlistdev',
        'COLLECTION': 'test_patterns',
        'PEN_COLLECTION': 'test_pen',
        'GARBAGE_COLLECTION': 'test_garbage'
    })
    
    with app.test_client() as client:
        with app.app_context():
            load_json("uploads/mnm_all_ai_url_imageids.json", app.collection)
        yield client

def test_index(client):
    response = client.get('/patterns')
    assert response.status_code == 200
    data = response.get_json()
    assert 'metadata' in data
    assert 'data' in data

@pytest.mark.skip
def test_get_pattern_not_found(client):
    non_existent_id = '000000000000000000000000'
    response = client.get(f'/pattern/{non_existent_id}')
    assert response.status_code == 404
    assert response.get_json() == {'error': 'Pattern not found'}

@pytest.mark.skip
def test_set_pattern(client):
    new_pattern = {
        "name": "Test Pattern",
        "price": "$10.00",
        # Include other necessary fields
    }
    response = client.post('/pattern/new', json=new_pattern)
    assert response.status_code == 201

    # Verify the pattern exists in the pen collection
    with client.application.app_context():
        pen_collection = client.application.pen_collection
        inserted_pattern = pen_collection.find_one({"name": "Test Pattern"})
        assert inserted_pattern is not None
        assert inserted_pattern['price'] == "$10.00"

def test_update_pattern(client):
    # Insert a pattern to update
    new_pattern = {
        "name": "Old Pattern",
        "price": "$5.00",
    }
    client.post('/pattern/new', json=new_pattern)

    with client.application.app_context():
        pen_collection = client.application.pen_collection
        pattern = pen_collection.find_one({"name": "Old Pattern"})
        pattern_id = str(pattern['_id'])

    # Update the pattern
    updated_pattern = {
        "_id": pattern_id,
        "name": "Updated Pattern",
        "price": "$15.00",
    }
    response = client.post('/pattern/update', json=updated_pattern, query_string={'_id': pattern_id})
    assert response.status_code == 201

    # Verify the update
    with client.application.app_context():
        updated = pen_collection.find_one({"_id": ObjectId(pattern_id)})
        assert updated['name'] == "Updated Pattern"
        assert updated['price'] == "$15.00"

def test_delete_pattern(client):
    # Insert a pattern to delete
    new_pattern = {
        "name": "Pattern to Delete",
        "price": "$8.00",
    }
    response = client.post('/pattern/new', json=new_pattern)

    pid = ObjectId(response.json['ObjectId'])

    # Verify the pattern was created and is gettable from the pen
    pattern = client.get(f'pen/pattern/{pid}').json
    assert pattern['name'] == new_pattern['name']

    with client.application.app_context():
        pen_collection = client.application.pen_collection
        pattern = pen_collection.find_one({"name": "Pattern to Delete"})
        #  print(pattern)

    # Delete the pattern
    response = client.delete(f'/pen/{pid}')
    assert response.status_code == 204

    # Verify deletion
    with client.application.app_context():
        deleted_pattern = pen_collection.find_one({"_id": pid})
        assert deleted_pattern is None

@pytest.mark.skip
def test_search_patterns(client):
    # Insert patterns for searching
    patterns = [
        {"name": "UniqueSearchPattern1", "price": "$20.00"},
        {"name": "UniqueSearchPattern2", "price": "$25.00"},
    ]
    for pattern in patterns:
        client.post('/pattern/new', json=pattern)

    response = client.get('/patterns/search', query_string={'query': 'UniqueSearchPattern'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert 'metadata' in data
    assert data['metadata']['count'] >= 2
    returned_names = [p['name'] for p in data['data']]
    assert "UniqueSearchPattern1" in returned_names
    assert "UniqueSearchPattern2" in returned_names


