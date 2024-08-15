from abc import ABC, abstractmethod

class scraper(ABC):
    
    @abstractmethod
    def nf_scrape(self):
        """ scrapes the website for the non-foil card data"""

    @abstractmethod
    def f_scrape(self):
        """scrapes the website for the non-foil card data """
    
    @abstractmethod
    def get_urls(self):
        """scrapes the website the set urls """