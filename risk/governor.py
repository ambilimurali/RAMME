class RiskGovernor:
    """
    Central risk control layer.
    Decides whether trading is allowed at a given time.
    """

    def __init__(self,
                 max_drawdown=0.05,
                 max_exposure=1.0,
                 regime_limits=None):
        """
        Parameters:
            max_drawdown  : max allowable drawdown (fraction)
            max_exposure  : absolute exposure limit
            regime_limits : optional dict {regime: exposure_cap}
        """
        self.equity_peak = 0.0
        self.max_drawdown = max_drawdown
        self.max_exposure = max_exposure
        self.regime_limits = regime_limits or {}

    def update(self, equity):
        """
        Update equity peak and evaluate drawdown stop.
        """
        self.equity_peak = max(self.equity_peak, equity)
        drawdown = (self.equity_peak - equity) / max(self.equity_peak, 1e-6)

        if drawdown > self.max_drawdown:
            return False  # HARD STOP

        return True

    def allow_trade(self, regime, exposure):
        """
        Decide whether a new trade is allowed.

        Parameters:
            regime   : current market regime
            exposure : current absolute exposure

        Returns:
            bool
        """
        # Global exposure cap
        if exposure > self.max_exposure:
            return False

        # Regime-specific caps
        if regime in self.regime_limits:
            if exposure > self.regime_limits[regime]:
                return False

        return True
