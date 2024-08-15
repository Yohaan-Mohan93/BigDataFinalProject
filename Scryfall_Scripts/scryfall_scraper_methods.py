from datetime import datetime
from .scryfall_data import *
from helper import remove_non_unicode_chars
import httpx
import json
import logging


def scryfall_scrape(task_name,url,scryfall_data):
    resp = httpx.get(url)
    data = resp.content
    date_today = date.today().strftime('%d-%m-%Y')

    if task_name == 'Scryfall Sets':
        scryfall_sets = json.loads(data)['data']
        logging.info(f'Number of sets: {len(scryfall_sets)}')

        for set in scryfall_sets :
            name = set['name']
            code = set['code']
            release_date = datetime.strptime(set['released_at'],'%Y-%m-%d').date()
            card_count = set['card_count']
            logging.info(f'Set: {name}')
            scryfall_data.append(mtg_set(name,code,release_date,card_count))

    elif task_name == 'Scryfall Cards':
        scryfall_card_url = json.loads(data)['data']
        scryfall_cards = []
    

        for url in scryfall_card_url:
            if url['name'] == 'Default Cards':
                card_data = httpx.get(url['download_uri'])
                scryfall_cards = json.loads(card_data.content)

        for card in scryfall_cards:
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

            if 'oracle_text' in card.keys():
                oracle_text = remove_non_unicode_chars(card['oracle_text']).replace('\n',' ')
            if 'keywords' in card.keys():
                keywords = card['keywords']
            if 'card_faces' in card.keys():
                card_faces_list = card['card_faces']
                for card_face in card_faces_list:
                    card_faces += ',' + card_face.get('name','')
            if 'type_list' in card.keys():
                type = ' '.join([str(types) for types in card['type_list']])
            if 'prices' in card.keys():
                price_usd = card['prices']['usd']
                price_eur = card['prices']['eur']

            logging.info(f'Card: {name}, {set_name}')

            scryfall_data.append(mtg_card(name,type,set_name,set_code,rarity,keywords,card_faces,oracle_text,price_usd,price_eur,date_today))