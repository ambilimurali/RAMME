import random


class LatencyModel:
    """
    Models execution latency and its impact on price.
    """

    def __init__(self, min_ms=1, max_ms=10, seed=42):
        self.min_ms = min_ms
        self.max_ms = max_ms
        random.seed(seed)

    def sample_latency(self, regime=None):
        """
        Sample latency in milliseconds.
        """
        latency = random.randint(self.min_ms, self.max_ms)

        if regime == "VOLATILE":
            latency *= 2

        return latency

    def apply_price_drift(self, price, latency_ms, volatility):
        """
        Apply adverse price movement during latency window.
        """
        drift = volatility * (latency_ms / 1000.0)
        return price * (1 + drift)
