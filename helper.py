import os
import csv
import re
import pandas as pd
from sqlalchemy import create_engine

def euro_num_format_to_normal(price):
    price = price[:len(price) - 2]
    price = price.replace('.', '')
    price = price.replace(',', '.')

    return price

def prepare_set_name(set_name):
    set_name = remove_non_unicode_chars(set_name)
    set_name = set_name.replace(' ', '-')
    set_name = set_name.replace("'", '')
    set_name = set_name.replace(':', '')
    if 'Secret-Lair-Drop-Series-' in set_name:
        set_name = set_name.replace('Secret-Lair-Drop-Series-', '')
    set_name = set_name.replace(',', '')
    set_name = set_name.replace('.', '')

    return set_name

def has_number(input_string):
    return bool(re.search(r'\d', input_string))

def create_directory(path_to_file):
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)

    return os.path.exists(path_to_file)

def create_dataset(columns):
    return pd.DataFrame(columns=columns)

def create_conn_string():
    mysql_user = os.getenv('MYSQL_USER')
    mysql_pwd = os.getenv('MYSQL_PASSWORD')
    return 'mysql+pymysql://' + mysql_user + ':' + mysql_pwd + 'localhost/mtgcards'

def write_dataset_to_db(dataset,table,save_mode):
    conn_string = create_conn_string()
    engine = create_engine(conn_string)
    if save_mode == 'Overwrite':
        dataset.to_sql(name=table,con=engine,if_fails='replace')
    elif save_mode == 'Append':
        dataset.to_sql(name=table,con=engine,if_fails='append')
    else:
        dataset.to_sql(name=table,con=engine,if_fails='fail')
   

def read_from_db(query):
    conn_string = create_conn_string()
    engine = create_engine(conn_string)
    return pd.read_sql(query,engine)


def load_urls(website):
    urls = []
    if website == 'CardKingdom':
        with open('./Card_Kingdom/URLs/ck_urls.txt', 'r') as f:
            url_reader = csv.reader(f, delimiter='|')
            next(url_reader)
            urls = list(url_reader)
    elif website == 'SCG':
        with open('./Star_City_Games/URLs/scg_urls.txt', 'r') as f:
            url_reader = csv.reader(f, delimiter='|')
            next(url_reader)
            urls = list(url_reader)
    elif website == 'Scryfall':
        with open('./Scryfall/URLs/scry_urls.txt', 'r') as f:
            url_reader = csv.reader(f, delimiter='|')
            next(url_reader)
            urls = list(url_reader)
            
    return urls

def remove_non_unicode_chars(string):
    return re.sub(r'[^\x00-\x7F]+','', string)