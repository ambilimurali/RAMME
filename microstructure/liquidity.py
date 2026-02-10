import numpy as np

class LiquidityEstimator:
    def __init__(self, window=50):
        self.history = []  # store tuples of (spread, bid_size, ask_size)
        self.window = window

    def update(self, spread, bid_size=None, ask_size=None):
        self.history.append((spread, bid_size, ask_size))
        if len(self.history) > self.window:
            self.history.pop(0)

    def liquidity_score(self):
        if not self.history:
            return 0.0
        avg_spread = np.mean([h[0] for h in self.history])
        # optionally include sizes in a more complex score
        return 1.0 / (avg_spread + 1e-6)
