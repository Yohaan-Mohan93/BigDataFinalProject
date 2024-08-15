import csv
import json
import os
import random
from datetime import date
from helper import remove_non_unicode_chars
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the database tables
Base = declarative_base()

class SearchCount(Base):
    __tablename__ = 'search_count'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_name = Column(String, nullable=False)
    card_set = Column(String, nullable=False)
    search_count = Column(Integer, nullable=False, default=0)

class CardKingdomNonFoil(Base):
    __tablename__ = 'card_kingdom_non_foil'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    set = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    nm_price = Column(Float, nullable=True)
    ex_price = Column(Float, nullable=True)
    vg_price = Column(Float, nullable=True)
    g_price = Column(Float, nullable=True)
    card_text = Column(String, nullable=False)
    scrape_date = Column(Date, nullable=False)

class CardKingdomFoil(Base):
    __tablename__ = 'card_kingdom_foil'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    set = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    nm_price = Column(Float, nullable=True)
    ex_price = Column(Float, nullable=True)
    vg_price = Column(Float, nullable=True)
    g_price = Column(Float, nullable=True)
    card_text = Column(String, nullable=False)
    scrape_date = Column(Date, nullable=False)

class MTGCard(Base):
    __tablename__ = 'mtg_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    set_name = Column(String, nullable=False)
    set_code = Column(String, nullable=False)
    rarity = Column(String, nullable=False)
    combined_keywords = Column(String, nullable=False)
    card_faces = Column(String, nullable=False)
    oracle_text = Column(String, nullable=False)
    price_usd = Column(Float, nullable=False, default=0.0)
    price_eur = Column(Float, nullable=False, default=0.0)
    image_uri = Column(String, nullable=False)
    scrape_date = Column(Date, nullable=False)

# Initialize the database connection
engine = create_engine('sqlite:///mtg_cards.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Function to read CK prices files
def read_ck_prices_file(file_path, is_foil):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='|')
        next(reader)  # Skip the header line
        for row in reader:
            if is_foil:
                card = CardKingdomFoil(
                    name=row[1],
                    type=row[2],
                    set=row[3],
                    rarity=row[4],
                    nm_price=float(row[5]) if row[5] else None,
                    ex_price=float(row[6]) if row[6] else None,
                    vg_price=float(row[7]) if row[7] else None,
                    g_price=float(row[8]) if row[8] else None,
                    card_text=row[9],
                    scrape_date=date.today()
                )
            else:
                card = CardKingdomNonFoil(
                    name=row[1],
                    type=row[2],
                    set=row[3],
                    rarity=row[4],
                    nm_price=float(row[5]) if row[5] else None,
                    ex_price=float(row[6]) if row[6] else None,
                    vg_price=float(row[7]) if row[7] else None,
                    g_price=float(row[8]) if row[8] else None,
                    card_text=row[9],
                    scrape_date=date.today()
                )
            session.add(card)

# Function to read Oracle cards JSON file
def read_oracle_cards_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
       cards = json.load(file)
       for card in cards:
           name = card['name']
           type = ''
           set_name = remove_non_unicode_chars(card['set_name'])
           set_code = card['set']
           rarity = card['rarity']
           keywords = ['']
           card_faces = ''
           oracle_text = ''
           price_usd = 0.0
           price_eur = 0.0   
           # Handling 'oracle_text'
           if 'oracle_text' in card.keys():
               oracle_text = remove_non_unicode_chars(card['oracle_text']).replace('\n', ' ')
           
           # Handling 'keywords'
           if 'keywords' in card.keys():
               keywords = card['keywords']
           combined_keywords = ', '.join(keywords)  # Convert list to string
           
           # Handling 'card_faces'
           if 'card_faces' in card.keys():
               card_faces_list = card['card_faces']
               for card_face in card_faces_list:
                   card_faces += ',' + card_face.get('name', '')
           
           # Handling 'type_list'
           if 'type_list' in card.keys():
               type = ' '.join([str(types) for types in card['type_list']])
           
           # Handling 'prices'
           if 'prices' in card.keys():
               price_usd = float(card['prices']['usd']) if card['prices']['usd'] else 0.0
               price_eur = float(card['prices']['eur']) if card['prices']['eur'] else 0.0
           
           if 'image_uris' in card.keys():
               image_uri = card['image_uris']['normal']
            
           # Create the card object
           mtg_card = MTGCard(
               name=name,
               type=type,
               set_name=set_name,
               set_code=set_code,
               rarity=rarity,
               combined_keywords=combined_keywords,
               card_faces=card_faces,
               oracle_text=oracle_text,
               price_usd=price_usd,
               price_eur=price_eur,
               image_uri=image_uri,
               scrape_date=date.today()
           )     
           session.add(mtg_card)

def create_card_view():
    with engine.connect() as conn:
        create_view_sql = text("""
        CREATE VIEW IF NOT EXISTS VW_COMBINED_CARDS_NON_FOIL AS
        SELECT 
            NAME AS CARD_NAME,
            TYPE AS CARD_TYPE,
            "SET" AS CARD_SET,
            RARITY AS CARD_RARITY,
            NM_PRICE AS CK_NM_PRICE,
            EX_PRICE AS CK_EX_PRICE,
            VG_PRICE AS CK_VG_PRICE,
            G_PRICE  AS CK_G_PRICE,
            CARD_TEXT AS CARD_TEXT,
            NULL AS SET_CODE,
            NULL AS COMBINED_KEYWORDS,
            NULL AS CARD_FACES,
            NULL AS ORACLE_TEXT,
            NULL AS PRICE_USD,
            NULL AS PRICE_EUR,
            NULL AS IMAGE_URI,
            SCRAPE_DATE AS SCRAPE_DATE
        FROM 
            CARD_KINGDOM_NON_FOIL
        UNION
        SELECT 
            NAME AS CARD_NAME,
            TYPE AS CARD_TYPE,
            SET_NAME AS CARD_SET,
            RARITY AS CARD_RARITY,
            NULL AS CK_NM_PRICE,
            NULL AS CK_EX_PRICE,
            NULL AS CK_VG_PRICE,
            NULL  AS CK_G_PRICE,
            NULL AS CARD_TEXT,
            SET_CODE AS SET_CODE,
            COMBINED_KEYWORDS AS COMBINED_KEYWORDS,
            CARD_FACES AS CARD_FACES,
            ORACLE_TEXT AS ORACLE_TEXT,
            PRICE_USD AS PRICE_USD,
            PRICE_EUR AS PRICE_EUR,
            IMAGE_URI AS IMAGE_URI,
            SCRAPE_DATE AS SCRAPE_DATE
        FROM 
            MTG_CARDS;
        """)
        conn.execute(create_view_sql)

def create_price_view():
    with engine.connect() as conn:
        create_view_sql = text("""
        CREATE VIEW IF NOT EXISTS VW_COMBINED_CARD_PRICES_NON_FOIL AS
        SELECT 
            NAME AS CARD_NAME,
            "SET" AS CARD_SET,
            NM_PRICE AS CK_NM_PRICE,
            NULL AS PRICE_USD,
            NULL AS PRICE_EUR,
            SCRAPE_DATE AS PRICE_DATE
        FROM 
            CARD_KINGDOM_NON_FOIL
        UNION
        SELECT 
            NAME AS CARD_NAME,
            SET_NAME AS CARD_SET,
            NULL AS CK_NM_PRICE,
            PRICE_USD AS SCRYFALL_PRICE_USD,
            PRICE_EUR AS SCRYFALL_PRICE_EUR,
            SCRAPE_DATE AS PRICE_DATE
        FROM 
            MTG_CARDS;
        """)
        conn.execute(create_view_sql)

def populate_search_count():
    # Fetch unique card_name and card_set combinations
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT CARD_NAME, CARD_SET 
            FROM VW_COMBINED_CARDS_NON_FOIL
        """))
        cards = result.fetchall()
    
        for card in cards:
            search_count = SearchCount(
            card_name=card[0],
            card_set=card[1],
            search_count=random.randint(1, 100)
        )
        session.add(search_count)
    session.commit()


# Truncate tables
def truncate_tables():
    meta = MetaData()
    meta.reflect(bind=engine)
    with engine.connect() as conn:
        for table in reversed(meta.sorted_tables):
            conn.execute(table.delete())
        # Drop the views if they exist
        conn.execute(text("DROP VIEW IF EXISTS VW_COMBINED_CARDS_NON_FOIL"))
        conn.execute(text("DROP VIEW IF EXISTS VW_COMBINED_CARD_PRICES_NON_FOIL"))
        
        # Drop the tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS search_count"))
        conn.execute(text("DROP TABLE IF EXISTS card_kingdom_non_foil"))
        conn.execute(text("DROP TABLE IF EXISTS card_kingdom_foil"))
        conn.execute(text("DROP TABLE IF EXISTS mtg_cards"))
    session.commit()

# Set folder path and run the migration
folder_path = './Test Migration'

# Truncate existing tables
truncate_tables()

# Read and migrate CK prices files
read_ck_prices_file(os.path.join(folder_path, 'CK_PRICES_20221113.txt'), is_foil=False)
read_ck_prices_file(os.path.join(folder_path, 'CK_FOIL_PRICES_20221022.txt'), is_foil=True)

# Read and migrate Oracle cards file
read_oracle_cards_file(os.path.join(folder_path, 'oracle-cards-20240719210240.json'))

# Create the views
create_card_view()
create_price_view()

# Call the function to populate the search count table
populate_search_count()

# Commit the session to save all the changes
session.commit()

print("Data migration completed successfully!")
