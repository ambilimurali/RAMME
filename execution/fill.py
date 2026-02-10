import random


class PartialFillModel:
    """
    Models partial fills as a function of liquidity and order size.
    """

    def __init__(self, seed=42):
        random.seed(seed)

    def fill_ratio(self, liquidity_score, order_size=1.0):
        """
        Parameters:
            liquidity_score : [0.0 – 1.0]
            order_size      : relative size of order

        Returns:
            fill ratio in [0.0 – 1.0]
        """

        # Base fill probability from liquidity
        base = max(0.0, min(1.0, liquidity_score))

        # Larger orders fill worse
        size_penalty = max(0.1, 1.0 - order_size)

        # Microstructure noise
        noise = random.uniform(0.6, 1.0)

        fill = base * size_penalty * noise
        return max(0.0, min(1.0, fill))
