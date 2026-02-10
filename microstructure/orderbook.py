class OrderBook:
    def __init__(self, levels=3):
        self.levels = levels
        self.bids = []
        self.asks = []

    def update(self, bids, asks):
        """
        bids / asks: list of (price, size)
        """
        self.bids = bids[:self.levels]
        self.asks = asks[:self.levels]

    def imbalance(self):
        bid_vol = sum(size for _, size in self.bids)
        ask_vol = sum(size for _, size in self.asks)
        total = bid_vol + ask_vol
        if total == 0:
            return 0.0
        return (bid_vol - ask_vol) / total
