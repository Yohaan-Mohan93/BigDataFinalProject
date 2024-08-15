import logging
import time
import re
import undetected_chromedriver as uc
from urllib.error import HTTPError, URLError
from .ck_mtg_card import *
from helper import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def ck_scrape(start_url, card_list, urls, all_cards_placements):
    try:
        url = 'https://webcache.googleusercontent.com/search?q=cache:' + start_url
        browser = uc.Chrome()
        browser.get(url)
        wait = WebDriverWait(browser, 20)

        pages =  wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.page-item a')))
        total_pages = int(pages[len(pages) - 2 ].text)
        page_number = 1

        while(page_number <= (total_pages)):
            urls.append(url)
            set_count = 0
            price_count = 0
            card_names = browser.find_elements(By.CLASS_NAME, 'productDetailTitle')
            card_types = browser.find_elements(By.CLASS_NAME, 'productDetailType')
            card_sets = browser.find_elements(By.CLASS_NAME, 'productDetailSet')
            card_prices = browser.find_elements(By.CSS_SELECTOR,'input[name~="price"')
            card_texts = browser.find_elements(By.CLASS_NAME, 'detailFlavortext')

            for names in card_names:
                this_name = names.text.strip()
                card_type = card_types[set_count].text[0:len(card_types[set_count].text.strip())]
                this_type = ''
                if has_number(card_type):
                    types = re.split('(\d+)', card_type)
                    this_type = types[len(types) - 1].strip()
                else:
                    this_type = card_type.strip()
                this_set_rarity = card_sets[set_count].text.strip().split('(')
                this_nm = 0.0
                this_ex = 0.0
                this_vg = 0.0
                this_g = 0.0
                this_text = card_texts[set_count].text.strip().replace('\n', ' ')
                set_count += 1

                for j in range(4):
                    string = card_prices[price_count].get_attribute("value").strip()
                    if j == 0:
                        this_nm = float(string)
                    elif j == 1:
                        this_ex = float(string)
                    elif j == 2:
                        this_vg = float(string)
                    elif j == 3:
                        this_g = float(string)
                    price_count += 1

                this_set = this_set_rarity[0]
                this_rarity = this_set_rarity[1][0]

                card_list.append(CkMtgCard(0, this_name, this_type, this_set,
                                           this_rarity, this_nm, this_ex, this_vg, this_g,this_text))
                all_cards_placements.append(CkCardPlacement(this_name, this_set, set_count, page_number))


            pages = browser.find_elements(By.CSS_SELECTOR,'.page-item a')
            logging.info(f'Number of Cards: {len(card_list)}' )
            logging.info(f'Number of Card Placements: {len(all_cards_placements)}' )
            time.sleep(5)
            if page_number != total_pages:
                logging.info(f'Page Number: {page_number}')
                pages[len(pages) - 1].click()
            page_number += 1
        browser.close()

    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print(url, ' is wrong')
    except TimeoutException as e:
        return
    except Exception as e:
        logging.info(f'{e}')
        return
    finally:
        uc.Chrome().close()

def ck_foil_scrape(start_url, card_list, urls, all_cards_placements):
    try:
        url = start_url
        browser = uc.Chrome()
        browser.get(url)
        wait = WebDriverWait(browser, 20)

        pages =  wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.page-item a')))

        total_pages = int(pages[len(pages) - 2 ].text)
        page_number = 1

        while(page_number <= (total_pages)):
            urls.append(url)
            set_count = 0
            price_count = 0
            card_names = browser.find_elements(By.CLASS_NAME, 'productDetailTitle')
            card_types = browser.find_elements(By.CLASS_NAME, 'productDetailType')
            card_sets = browser.find_elements(By.CLASS_NAME, 'productDetailSet')
            card_prices = browser.find_elements(By.CSS_SELECTOR,'input[name~="price"')
            card_texts = browser.find_elements(By.CLASS_NAME, 'detailFlavortext')

            for names in card_names:
                this_name = names.text.strip()
                card_type = card_types[set_count].text[0:len(card_types[set_count].text.strip())]
                this_type = ''
                if has_number(card_type):
                    types = re.split('(\d+)', card_type)
                    this_type = types[len(types) - 1].strip()
                else:
                    this_type = card_type.strip()
                this_set_rarity = card_sets[set_count].text.strip().split('(')
                this_nm = 0.0
                this_ex = 0.0
                this_vg = 0.0
                this_g = 0.0
                this_text = card_texts[set_count].text.strip().replace('\n', ' ')
                set_count += 1

                for j in range(4):
                    string = card_prices[price_count].get_attribute("value").strip()
                    if j == 0:
                        this_nm = float(string)
                    elif j == 1:
                        this_ex = float(string)
                    elif j == 2:
                        this_vg = float(string)
                    elif j == 3:
                        this_g = float(string)
                    price_count += 1

                this_set = this_set_rarity[0]
                this_rarity = this_set_rarity[1][0]

                card_list.append(CkMtgCard(0, this_name, this_type, this_set,
                                           this_rarity, this_nm, this_ex, this_vg, this_g,this_text))
                all_cards_placements.append(CkCardPlacement(this_name, this_set, set_count, page_number))


            pages = browser.find_elements(By.CSS_SELECTOR,'.page-item a')
            logging.info(f'Number of Cards: {len(card_list)}' )
            logging.info(f'Number of Card Placements: {len(all_cards_placements)}' )
            time.sleep(5)
            if page_number != total_pages:
                logging.info(f'Page Number: {page_number}')
                pages[len(pages) - 1].click()
            page_number += 1
        browser.close()

    except HTTPError as e:
        print(e)
    except URLError as e:
        print(e)
        print(url, ' is wrong')
    except TimeoutException as e:
        logging.error(f'TimeoutException {e}')
        return
    except Exception as e:
        logging.error(f'{e}')
        return
    finally:
        uc.Chrome().close()