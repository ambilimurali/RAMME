# File: regime/entropy.py
import numpy as np

class EntropyCalculator:
    """
    Computes entropy metrics for time series of returns.
    Can be used as an advanced feature for regime detection.
    """

    def __init__(self, bins=10, window=20):
        """
        bins: number of histogram bins for Shannon entropy
        window: number of recent returns to compute rolling entropy
        """
        self.bins = bins
        self.window = window

    # -------------------------
    # Shannon Entropy
    # -------------------------
    def shannon_entropy(self, returns):
        """
        Compute Shannon entropy of a list of returns
        """
        if len(returns) < self.window:
            return 0.0
        window_returns = returns[-self.window:]
        hist, _ = np.histogram(window_returns, bins=self.bins, density=True)
        hist = hist[hist > 0]  # ignore zero probabilities
        return -np.sum(hist * np.log(hist))

    # -------------------------
    # Normalized Shannon Entropy
    # -------------------------
    def normalized_entropy(self, returns):
        """
        Normalized Shannon entropy (0 to 1)
        """
        se = self.shannon_entropy(returns)
        max_entropy = np.log(self.bins)
        return se / max_entropy if max_entropy > 0 else 0

    # -------------------------
    # Renyi Entropy (optional)
    # -------------------------
    def renyi_entropy(self, returns, alpha=2):
        """
        Renyi entropy of order alpha
        """
        if len(returns) < self.window:
            return 0.0
        window_returns = returns[-self.window:]
        hist, _ = np.histogram(window_returns, bins=self.bins, density=True)
        hist = hist[hist > 0]
        return 1/(1-alpha) * np.log(np.sum(hist ** alpha))

    # -------------------------
    # Rolling entropy for a series
    # -------------------------
    def rolling_entropy(self, returns):
        """
        Returns a list of normalized entropy values over time
        """
        entropies = []
        for i in range(len(returns)):
            entropies.append(self.normalized_entropy(returns[:i+1]))
        return entropies
