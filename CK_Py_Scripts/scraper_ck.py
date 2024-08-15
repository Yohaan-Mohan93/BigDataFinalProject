from scraper import scraper
from datetime import date
from helper import *
from .ck_scraper_methods import *
from .ck_mtg_card import CkMtgCard
from .ck_url_scraper import get_ck_set_urls
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import concurrent.futures
import logging
import os
import time

# Database Models (as defined previously)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Integer

Base = declarative_base()

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

db_path = 'mtg_cards.db'
if not os.path.exists(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
else:
    engine = create_engine(f'sqlite:///{db_path}')

Session = sessionmaker(bind=engine)

class ck_scraper(scraper):

    def __init__(self):
        self.visited_urls = []
        self.card_list = []
        self.all_card_placements = []
        self.urls = []
        self.session = Session()  # Initialize the session

    def ck_scraping_task(self, urls):
        start_url = urls[1]
        set_name = urls[0]

        logging.info(f'Scraping cards for {set_name}')
        logging.info(f'and on page: {start_url}')

        ck_scrape(start_url, self.card_list, self.visited_urls, self.all_card_placements)
        time.sleep(10)

        logging.info(f'Final Number of Cards: {len(self.card_list)}' )
        logging.info(f'Final Number of Card Placements: {len(self.all_card_placements)}')

    def ck_scraping_foils_task(self, urls):
        start_url = urls[1] + '/foils'
        set_name = urls[0]

        logging.info(f'Scraping cards for {set_name}')
        logging.info(f'and on page: {start_url}')

        ck_foil_scrape(start_url, self.card_list, self.visited_urls, self.all_card_placements)
        time.sleep(10)

        logging.info(f'Final Number of Cards: {len(self.card_list)}' )
        logging.info(f'Final Number of Card Placements: {len(self.all_card_placements)}')

    def nf_scrape(self):
        date_today = date.today().strftime('%Y%m%d')
        start_time = time.time()
        self.urls = load_urls("CardKingdom")

        path_to_card_logs = 'Card_Kingdom/Logs/CardLogs'
        result = create_directory(path_to_card_logs)
        logs_filename = path_to_card_logs + '/Card_Kingdom_cards_' + date_today + '.log'
        
        logging.basicConfig(filename=logs_filename, level=logging.INFO,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

        if result:
            logging.info("Directory created")
        else:
            logging.info("Directory exists")

        logging.info("Starting Scraping")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self.ck_scraping_task, self.urls)

        # Save non-foil cards to the database
        for card in self.card_list:
            new_card = CardKingdomNonFoil(
                name=card.name,
                type=card.type,
                set=card.set,
                rarity=card.rarity,
                nm_price=card.nm_price,
                ex_price=card.ex_price,
                vg_price=card.vg_price,
                g_price=card.g_price,
                card_text=card.card_text
            )
            self.session.add(new_card)
        self.session.commit()

        logging.info("Scraping ended")

        end_time = time.time()
        time_taken_hrs = (end_time - start_time) / 60
        time_string = 'Total Execution Time: ' + str(time_taken_hrs) + ' minutes'
        logging.info(f'{time_string}')
    

    def f_scrape(self):
        date_today = date.today().strftime('%Y%m%d')
        start_time = time.time()
        urls = load_urls("CardKingdom")

        path_to_card_logs = 'Card_Kingdom/Logs/CardLogs'
        result = create_directory(path_to_card_logs)
        logs_filename = path_to_card_logs + '/Card_Kingdom_cards_' + date_today + '.log'
        
        logging.basicConfig(filename=logs_filename, level=logging.INFO,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

        if result:
            logging.info("Directory created")
        else:
            logging.info("Directory exists")

        logging.info("Starting Scraping")

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(self.ck_scraping_foils_task, urls)

        logging.info("Scraping ended")

        # Save foil cards to the database
        for card in self.card_list:
            new_card = CardKingdomFoil(
                name=card.name,
                type=card.type,
                set=card.set,
                rarity=card.rarity,
                nm_price=card.nm_price,
                ex_price=card.ex_price,
                vg_price=card.vg_price,
                g_price=card.g_price,
                card_text=card.card_text
            )
            self.session.add(new_card)
        self.session.commit()

        end_time = time.time()
        time_taken_hrs = (end_time - start_time) / 60
        time_string = 'Total Execution Time: ' + str(time_taken_hrs) + ' minutes'
        logging.info(f'{time_string}')
