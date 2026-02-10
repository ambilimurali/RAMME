class SlippageModel:
    """
    Models execution price impact based on order size and liquidity.
    """

    def __init__(self, base_slippage=0.0001):
        self.base_slippage = base_slippage

    def apply(self, price, qty, liquidity_score, side=1, regime=None):
        """
        Parameters:
            price           : mid price
            qty             : absolute order quantity
            liquidity_score : [0.0 – 1.0]
            side            : +1 buy, -1 sell
            regime          : optional regime label

        Returns:
            executed price
        """

        liquidity = max(liquidity_score, 1e-6)

        # Base impact
        impact = self.base_slippage * qty / liquidity

        # Regime amplification
        if regime == "VOLATILE":
            impact *= 2.0
        elif regime == "QUIET":
            impact *= 0.5

        # Buy pays more, sell receives less
        executed_price = price * (1 + side * impact)
        return executed_price
