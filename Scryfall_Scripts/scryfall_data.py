from dataclasses import dataclass
from datetime import date

@dataclass
class mtg_set:
    name: str
    code: str
    release_date: date
    card_count: int

    def to_string(self):
        return ( self.name + '|' + self.code + '|' + str(self.release_date) + '|' + str(self.card_count) + '|')


@dataclass
class mtg_card:
    name: str
    type: str
    set_name: str
    set_code: str
    rarity: str
    keywords: list
    card_faces: str
    oracle_text: str
    price_usd: float
    price_eur: float
    scrape_date: date

    def to_string(self):
        combined_keywords = ','.join(self.keywords)

        return (self.name + '|' + self.type + '|' + self.set_name + '|' + self.set_code + '|' + self.rarity + '|' +
                combined_keywords + '|' + self.card_faces + '|' + self.oracle_text)
