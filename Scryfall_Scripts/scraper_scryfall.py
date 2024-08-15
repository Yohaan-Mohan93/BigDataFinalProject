from scraper import scraper
from datetime import date, datetime
from helper import *
from sqlalchemy import Column, String, Float, Integer, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .scryfall_data import *
from .scryfall_scraper_methods import *
import logging
import sys
import time
import os

Base = declarative_base()

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
    scrape_date = Column(Date, nullable=False)

# Ensure the database exists and create it if it doesn't
db_path = 'mtg_cards.db'
if not os.path.exists(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
else:
    engine = create_engine(f'sqlite:///{db_path}')

Session = sessionmaker(bind=engine)

class scryfall_scraper(scraper):

    def __init__(self):
        self.scryfall_data = []
        self.urls = load_urls('Scryfall')

    def scryfall_scrape_task(self, urls):
        start_url = urls[1]
        task_name = urls[0]

        logging.info(f'Scraping cards for {task_name}')
        logging.info(f'and on page: {start_url}')

        scryfall_scrape(task_name, start_url, self.scryfall_data)
        logging.info(f'Final Number of {type(self.scryfall_data[0])}: {len(self.scryfall_data)}')

    def nf_scrape(self):
        """scrapes the website for the non-foil card data"""

    def f_scrape(self):
        """scrapes the website for the foil card data"""

    def get_urls(self):
        """scrapes the website the set urls"""

    def get_mtg_sets(self):
        date_today = date.today().strftime('%Y%m%d')
        path_to_file = 'Scryfall/Sets/' + date_today
        start_time = time.time()
        result = create_directory(path_to_file)
        path_to_card_logs = 'Scryfall/Logs/SetsLogs'
        result = create_directory(path_to_card_logs)
        logs_filename = path_to_card_logs + '/Scryfall_sets_' + date_today + '.log'

        logging.basicConfig(filename=logs_filename, level=logging.INFO, format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

        if result:
            logging.info("Directory created")
        else:
            logging.info("Directory exists")

        scry_sets_filename = path_to_file + '/MTG_SETS_' + date_today + '.txt'

        logging.info("Starting Scraping")

        self.scryfall_scrape_task(self.urls[0])

        logging.info("Scraping ended")

        end_time = time.time()
        time_taken_hrs = (end_time - start_time) / 60

        with open(scry_sets_filename, 'w') as file_handle:
            file_handle.write("Name|Code|ReleaseDate|CardCount|\n")
            for list_item in self.scryfall_data:
                file_handle.write('%s\n' % list_item.to_string())

        time_string = 'Total Execution Time: ' + str(time_taken_hrs) + ' minutes'
        logging.info(f'{time_string}')

    def get_all_mtg_cards(self):
        date_today = date.today().strftime('%Y%m%d')
        path_to_file = 'Scryfall/Cards/' + date_today
        start_time = time.time()
        result = create_directory(path_to_file)
        path_to_card_logs = 'Scryfall/Logs/CardLogs'
        result = create_directory(path_to_card_logs)
        logs_filename = path_to_card_logs + '/Scryfall_cards_' + date_today + '.log'

        logging.basicConfig(filename=logs_filename, level=logging.INFO, format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')

        if result:
            logging.info("Directory created")
        else:
            logging.info("Directory exists")

        scry_sets_filename = path_to_file + '/MTG_CARDS_' + date_today + '.txt'

        logging.info("Starting Scraping")

        self.scryfall_scrape_task(self.urls[1])

        logging.info("Scraping ended")

        end_time = time.time()
        time_taken_hrs = (end_time - start_time) / 60
        
        # Save to database
        session = Session()
        for i, card_data in enumerate(self.scryfall_data):
            try:
                combined_keywords = ','.join(card_data.keywords)
                scrape_date = card_data.scrape_date
                if isinstance(scrape_date, str):
                    scrape_date = datetime.strptime(scrape_date, "%d-%m-%Y").date()
                new_card = MTGCard(
                    name=card_data.name,
                    type=card_data.type,
                    set_name=card_data.set_name,
                    set_code=card_data.set_code,
                    rarity=card_data.rarity,
                    combined_keywords=combined_keywords,
                    card_faces=card_data.card_faces,
                    oracle_text=card_data.oracle_text,
                    price_usd=card_data.price_usd if card_data.price_usd is not None else 0.0,
                    price_eur=card_data.price_eur if card_data.price_eur is not None else 0.0,
                    scrape_date=scrape_date
                )
                session.add(new_card)
                logging.info(f"Added card {i}: {new_card.name}")
            except Exception as e:
                logging.error(f"Error processing card {i}: {card_data}")
                logging.exception(e)
        session.commit()

        logging.info("Data committed to the database")

        # Verify database content
        try:
            result = session.query(MTGCard).all()
            logging.info(f"Total records in the database: {len(result)}")
        except Exception as e:
            logging.error("Error querying the database")
            logging.exception(e)
        finally:
            session.close()

        time_string = 'Total Execution Time: ' + str(time_taken_hrs) + ' minutes'
        logging.info(f'{time_string}')
