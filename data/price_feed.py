# data/price_feed.py

import random

class PriceFeed:
    def __init__(self, start_price=100.0):
        self.price = start_price

    def next_price(self):
        # random walk (volatile market)
        self.price += random.uniform(-1.5, 1.5)
        return round(self.price, 2)
