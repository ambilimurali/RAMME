import numpy as np

class MicrostructureFeatures:
    def __init__(self):
        self.prev_mid_price = None

    def compute_mid_price(self, bid, ask):
        return (bid + ask) / 2.0

    def bid_ask_spread(self, bid, ask):
        return ask - bid

    def order_imbalance(self, bid_size, ask_size):
        denom = bid_size + ask_size
        if denom == 0:
            return 0.0
        return (bid_size - ask_size) / denom

    def price_return(self, mid_price):
        if self.prev_mid_price is None:
            self.prev_mid_price = mid_price
            return 0.0
        ret = mid_price - self.prev_mid_price
        self.prev_mid_price = mid_price
        return ret
