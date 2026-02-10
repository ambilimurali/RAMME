class ToxicityEstimator:
    def __init__(self):
        self.recent_trades = []

    def update(self, price_move):
        self.recent_trades.append(price_move)
        if len(self.recent_trades) > 20:
            self.recent_trades.pop(0)

    def toxicity_score(self):
        if len(self.recent_trades) < 5:
            return 0.0

        same_dir = sum(
            1 for i in range(1, len(self.recent_trades))
            if self.recent_trades[i] * self.recent_trades[i-1] > 0
        )

        return same_dir / (len(self.recent_trades) - 1)
