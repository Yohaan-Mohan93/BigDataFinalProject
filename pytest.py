import pytest
from app import app, get_db
import os
import tempfile

@pytest.fixture
def client():
    # Set up a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            from migrate import migrate_db  # Assuming migrate_db is a function in your migrate.py
            migrate_db()
        yield client

    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)

def test_search_existing_card(client):
    # Insert test data into the database
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO VW_COMBINED_CARDS_NON_FOIL (CARD_NAME, CARD_TYPE, CARD_SET, SET_CODE, CARD_RARITY, COMBINED_KEYWORDS, CARD_FACES, ORACLE_TEXT, PRICE_USD, PRICE_EUR, SCRAPE_DATE, IMAGE_URI, CK_NM_PRICE, CK_EX_PRICE, CK_VG_PRICE, CK_G_PRICE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   ("Test Card", "Creature", "Test Set", "TS", "Rare", "Flying", "Face 1", "Some text", 10.00, 8.50, "2023-01-01", "http://example.com/image.jpg", 12.00, 11.00, 10.00, 9.00))
        db.commit()

    # Perform the search
    response = client.post('/search', data={'query': 'Test Card'})
    assert b'Test Card' in response.data
    assert b'Creature' in response.data
    assert response.status_code == 200

def test_suggest_endpoint(client):
    # Insert test data into the database
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO VW_COMBINED_CARDS_NON_FOIL (CARD_NAME) VALUES (?)", ("Suggestion Test",))
        db.commit()

    # Test the suggestion endpoint
    response = client.get('/suggest', query_string={'query': 'Sug'})
    assert b'Suggestion Test' in response.data
    assert response.status_code == 200

def test_predict_price_valid_card(client):
    # Mock the trained model for prediction
    from app import model
    model['Test Card'] = lambda x: [15.00]  # Replace with actual model loading and prediction logic

    # Predict price
    response = client.post('/predict_price', data={'card_name': 'Test Card', 'future_search_count': 100})
    assert b'15.00' in response.data
    assert response.status_code == 200

def test_predict_price_invalid_card(client):
    # Predict price for a non-existing card
    response = client.post('/predict_price', data={'card_name': 'Nonexistent Card', 'future_search_count': 100})
    assert b"No model found for card: Nonexistent Card" in response.data
    assert response.status_code == 200

def test_search_count_increment(client):
    # Insert test data into the database
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO search_count (card_name, card_set, search_count) VALUES (?, ?, ?)", 
                   ("Increment Test Card", "Test Set", 0))
        db.commit()

    # Perform the search
    client.post('/search', data={'query': 'Increment Test Card'})

    # Check if search count incremented
    with app.app_context():
        db = get_db()
        cur = db.execute("SELECT search_count FROM search_count WHERE card_name = ? AND card_set = ?", 
                         ("Increment Test Card", "Test Set"))
        search_count = cur.fetchone()[0]
        assert search_count == 1
