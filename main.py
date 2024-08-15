from datetime import date
from helper import *
from scraper_factory import ScraperFactory
import concurrent.futures
import logging
import sys
import threading
import time

if __name__ == "__main__":
    scraper_factory = ScraperFactory()
    scraper = scraper_factory.get_factory(sys.argv[1])
    if sys.argv[2] == 'cards':
        if sys.argv[3] == 'nonfoil':
            scraper.nf_scrape()
        if sys.argv[3] == 'foil':
            scraper.f_scrape()
    elif sys.argv[2] == 'urls':
        scraper.get_urls()
    elif sys.argv[2] == 'sets':
        scraper.get_mtg_sets()
    elif sys.argv[2] == 'allcards':
        scraper.get_all_mtg_cards()