from Scryfall_Scripts.scraper_scryfall import scryfall_scraper
from CK_Py_Scripts.scraper_ck import ck_scraper
from scraper import scraper

class ScraperFactory(object):

    def get_factory(self, website):        
        factories = {
            'scry': scryfall_scraper(),
            'ck' : ck_scraper()
        }

        if website in factories:
            return factories[website]