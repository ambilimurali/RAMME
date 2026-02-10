class RegimePnLTracker:
    """
    Tracks PnL, drawdown, and activity by regime.
    """

    def __init__(self):
        self.last_equity = None
        self.pnl_by_regime = {}
        self.peak_by_regime = {}
        self.drawdown_by_regime = {}
        self.trades_by_regime = {}

    def update(self, regime, equity, traded=False):
        """
        Update PnL attribution for a regime.

        Parameters:
            regime  : current regime label
            equity  : current equity
            traded  : whether a trade occurred this step
        """
        if self.last_equity is None:
            self.last_equity = equity
            self.peak_by_regime.setdefault(regime, equity)
            self.drawdown_by_regime.setdefault(regime, 0.0)
            self.trades_by_regime.setdefault(regime, 0)
            return

        pnl = equity - self.last_equity

        # PnL
        self.pnl_by_regime.setdefault(regime, 0.0)
        self.pnl_by_regime[regime] += pnl

        # Trade count
        if traded:
            self.trades_by_regime[regime] = self.trades_by_regime.get(regime, 0) + 1

        # Drawdown
        peak = self.peak_by_regime.get(regime, equity)
        peak = max(peak, equity)
        self.peak_by_regime[regime] = peak

        dd = (peak - equity) / max(peak, 1e-6)
        self.drawdown_by_regime[regime] = max(
            self.drawdown_by_regime.get(regime, 0.0), dd
        )

        self.last_equity = equity

    def report(self):
        """
        Final attribution report.
        """
        return {
            "pnl": dict(self.pnl_by_regime),
            "max_drawdown": dict(self.drawdown_by_regime),
            "trades": dict(self.trades_by_regime),
        }

    def reset(self):
        """
        Reset tracker state.
        """
        self.__init__()
