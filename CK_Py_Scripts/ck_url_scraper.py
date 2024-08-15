from datetime import date,datetime
from helper import create_directory,create_dataset
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pandas as pd
import logging

def get_ck_set_urls():
    
    path_to_url_logs='Card_Kingdom/Logs/URLLogs'
    result = create_directory(path_to_url_logs)
    date_today = date.today().strftime('%d%m%Y')
    datetime_today = datetime.today().strftime()
    logs_filename=path_to_url_logs+'/Card_Kingdom_urls_'+date_today+'.log' 

    logging.basicConfig(filename=logs_filename, level=logging.INFO,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    url = 'https://webcache.googleusercontent.com/search?q=cache:https://www.cardkingdom.com/catalog/magic_the_gathering/by_az'
    logging.info(url)
    browser = uc.Chrome()
    wait = WebDriverWait(browser, 30)
    browser.get(url)
    urls = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.col-sm-6 a[href]')))
    logging.info(len(urls))

    columns = ['Date','Set_Name','Set_URL']
    url_df = create_dataset(columns=columns)
    for i in range(len(urls)):
        new_row = {'Date':datetime_today,'Set_Name':urls[i].text,'Set_URL':urls[i].get_attribute('href')}
        url_df = url_df.append(new_row,ignore_index=True)
    
    
    # path_to_file = 'Card_Kingdom/URLs'
    # result = create_directory(path_to_file)
    

    # with open('./Card_Kingdom/URLs/ck_urls.txt', 'w') as f:
    #     f.write('Set_Name|Set_URL\n')
    #     for i in range(len(urls)):
    #         logging.info('Set Name: ' + urls[i].text + ';Url: ' + urls[i].get_attribute('href'))
    #         f.write('%s|%s\n' %(urls[i].text,urls[i].get_attribute('href')))
    #     f.close()
