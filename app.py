from flask import Flask, g, render_template, request, jsonify
import pandas as pd
import sqlite3
import joblib
import datetime

app = Flask(__name__)
DATABASE = 'mtg_cards.db'

# Load the model (assuming it predicts prices based on days and search count)
model = joblib.load('card_price_models.pkl')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    conn = get_db()
    cur = conn.cursor()

    # Fetch card details
    cur.execute("""
        SELECT CARD_NAME, CARD_TYPE, CARD_SET, SET_CODE, CARD_RARITY, COMBINED_KEYWORDS, 
               CARD_FACES, ORACLE_TEXT, PRICE_USD, PRICE_EUR, SCRAPE_DATE, IMAGE_URI, CK_NM_PRICE,
               CK_EX_PRICE, CK_VG_PRICE, CK_G_PRICE
        FROM VW_COMBINED_CARDS_NON_FOIL
        WHERE CARD_NAME LIKE ?
        LIMIT 1
    """, ('%' + query + '%',))
    card = cur.fetchone()

    if card:
        # Fetch search count entry
        cur.execute("""
            SELECT search_count FROM search_count
            WHERE card_name = ? AND card_set = ?
        """, (card[0], card[2]))
        search_count = cur.fetchone()

        if search_count:
            # If the entry exists, increment the search count
            new_search_count = search_count[0] + 1
            cur.execute("""
                UPDATE search_count
                SET search_count = ?
                WHERE card_name = ? AND card_set = ?
            """, (new_search_count, card[0], card[2]))
        else:
            # If the entry does not exist, insert a new one
            cur.execute("""
                INSERT INTO search_count (card_name, card_set, search_count)
                VALUES (?, ?, 1)
            """, (card[0], card[2]))

        conn.commit()

        # Fetch price history
        cur.execute("""
            SELECT PRICE_DATE, PRICE_USD, PRICE_EUR
            FROM VW_COMBINED_CARD_PRICES_NON_FOIL
            WHERE CARD_NAME = ?
            ORDER BY PRICE_DATE ASC
        """, (card[0],))
        price_history = cur.fetchall()

        card_details = {
            'name': card[0],
            'type': card[1],
            'set_name': card[2],
            'set_code': card[3],
            'rarity': card[4],
            'combined_keywords': card[5],
            'card_faces': card[6],
            'oracle_text': card[7],
            'price_usd': card[8],
            'price_eur': card[9],
            'scrape_date': card[10],
            'image_uri': card[11],
            'ck_nm_price': card[12],
            'ck_ex_price': card[13],
            'ck_vg_price': card[14],
            'ck_g_price': card[15],
            'price_history': price_history,
            'search_count': new_search_count if search_count else 1  # Use the updated search count or 1 if it's a new entry
        }
        return render_template('results.html', card=card_details)
    else:
        return render_template('index.html', error="Card not found")

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('query', '')
    cur = get_db().cursor()
    cur.execute("SELECT CARD_NAME FROM VW_COMBINED_CARDS_NON_FOIL WHERE CARD_NAME LIKE ? LIMIT 10", ('%' + query + '%',))
    suggestions = [row[0] for row in cur.fetchall()]
    return jsonify(suggestions)

@app.route('/predict_price', methods=['POST'])
def predict_price():
    card_name = request.form.get('card_name')
    card_set = request.form.get('card_set')

    conn = get_db()
    cur = conn.cursor()

    # Fetch search count
    cur.execute("""
        SELECT search_count FROM search_count
        WHERE card_name = ? AND card_set = ?
    """, (card_name, card_set))
    search_count_result = cur.fetchone()

    if search_count_result:
        search_count = search_count_result[0]
        
        # Prepare the feature for the model (here it's just search_count)
        feature = [[search_count]]
        
        # Use the model to predict the price
        predicted_price = model.predict(feature)[0]  # Assuming 'model' is your trained LinearRegression model
        
        return jsonify({'predicted_price': round(predicted_price, 2)})
    else:
        return jsonify({'error': f"No search count found for card: {card_name} in set: {card_set}"})

app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to monitor the status of the application.
    Returns:
        JSON object with a status message.
    """
    try:
        # Perform a simple query to check the database connection
        with get_db() as conn:
            conn.execute('SELECT 1')

        # You can also add more checks here (e.g., model loaded, external services available, etc.)
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        # If an exception occurs, return a failed status
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
