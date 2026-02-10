# File: engine/engine.py
import numpy as np
from microstructure.features import MicrostructureFeatures
from microstructure.liquidity import LiquidityEstimator
from regime.detector import RegimeDetector
from microstructure.orderbook import OrderBook
from microstructure.toxicity import ToxicityEstimator


class RAMMEEngine:
    """
    Market state engine with regime-based autonomous tick simulation.
    Computes microstructure features, liquidity, toxicity, and regime.
    """

    def __init__(self, initial_price=100.0, volatility=0.01):
        self.features = MicrostructureFeatures()
        self.liquidity = LiquidityEstimator()
        self.regime_detector = RegimeDetector()
        self.orderbook = OrderBook()
        self.toxicity = ToxicityEstimator()

        # Simulation state
        self.last_price = initial_price
        self.volatility = volatility

    def _simulate_tick(self, regime):
        """
        Simulate a single price tick based on market regime.
        Returns bid, ask prices and sizes.
        """
        mid_price = self.last_price
        drift = 0.0
        sigma = self.volatility

        # Determine regime-based drift/volatility
        if regime == "TREND":
            drift = 0.05
        elif regime == "MEAN_REVERT":
            mean_price = 100.0
            drift = 0.1 * (mean_price - mid_price)
        elif regime == "VOLATILE":
            sigma = 0.05
        elif regime == "SHOCK":
            shock_prob = 0.05
            shock = np.random.choice([0, 5, -5], p=[1 - shock_prob, shock_prob / 2, shock_prob / 2])
            drift += shock
        elif regime == "ILLIQUID":
            sigma = 0.1  # thin order book, spikes
        # Generate price return
        ret = drift + np.random.normal(0, sigma)
        mid_price = max(mid_price * (1 + ret), 0.01)  # price > 0

        # Generate bid/ask around mid price
        spread = max(np.random.uniform(0.01, 0.05), 0.0)  # spread ≥ 0
        bid = mid_price - spread / 2
        ask = mid_price + spread / 2

        # Random liquidity
        bid_size = max(np.random.poisson(10), 0)
        ask_size = max(np.random.poisson(10), 0)

        self.last_price = mid_price
        return bid, ask, bid_size, ask_size

    def on_tick(self, bid, ask, bid_size, ask_size):
        """
        Process a new tick using given bid/ask and sizes.
        Returns:
            mid: float, mid price
            regime: str, detected market regime
            features: dict, microstructure features
        """
        # --- Price & microstructure features ---
        mid = self.features.compute_mid_price(bid, ask)
        spread = self.features.bid_ask_spread(bid, ask)
        ret = self.features.price_return(mid)

        # Sanity checks
        mid = max(mid, 0.01)
        spread = max(spread, 0.0)

        # --- Update estimators ---
        self.liquidity.update(spread, bid_size, ask_size)
        self.regime_detector.update(ret)
        self.toxicity.update(ret)

        # --- Detect current regime ---
        regime = self.regime_detector.detect().name

        # --- Collect features ---
        features = {
            "return": ret,
            "spread": spread,
            "liquidity": max(0.0, self.liquidity.liquidity_score()),
            "toxicity": self.toxicity.toxicity_score(),
        }

        return mid, regime, features
