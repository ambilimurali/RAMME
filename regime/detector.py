# File: regime/detector.py
import numpy as np
from regime.states import MarketRegime
from regime.entropy import EntropyCalculator

class RegimeDetector:
    """
    Detects market regimes using return statistics and entropy.
    """

    def __init__(self, window=100, entropy_threshold=0.5, trend_factor=2.0):
        self.returns = []
        self.window = window
        self.entropy_calc = EntropyCalculator(window=min(window, 20))
        self.entropy_threshold = entropy_threshold  # normalized entropy threshold
        self.trend_factor = trend_factor  # mean vs std ratio for trend

    def update(self, ret):
        """
        Append new return and keep sliding window
        """
        self.returns.append(ret)
        if len(self.returns) > self.window:
            self.returns.pop(0)

    def detect(self):
        """
        Returns one of MarketRegime enums: VOLATILE, TREND, MEAN_REVERT
        """
        if len(self.returns) < self.window:
            return MarketRegime.VOLATILE

        mean = np.mean(self.returns)
        var = np.var(self.returns)
        entropy = self.entropy_calc.normalized_entropy(self.returns)

        # TREND: strong directional movement + low entropy
        if abs(mean) > self.trend_factor * np.sqrt(var) and entropy < self.entropy_threshold:
            return MarketRegime.TREND

        # VOLATILE: high variance + high entropy
        if var > 5 * np.mean(np.abs(self.returns)) and entropy >= self.entropy_threshold:
            return MarketRegime.VOLATILE

        # Default: mean-reverting
        return MarketRegime.MEAN_REVERT
