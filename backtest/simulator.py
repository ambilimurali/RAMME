class BacktestSimulator:
    """
    End-to-end backtest simulator:
    signal → position → execution → PnL
    """

    def __init__(self, initial_cash=100000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0.0
        self.equity = initial_cash
        self.history = []

    def execute_trade(self, qty, price):
        """
        Execute filled quantity at executed price.
        """
        cost = qty * price
        self.cash -= cost
        self.position += qty

    def mark_to_market(self, mid_price):
        """
        Update equity based on mid price.
        """
        self.equity = self.cash + self.position * mid_price
        return self.equity

    def step(self,
             target_delta,
             mid_price,
             fill_ratio,
             executed_price):
        """
        One simulation step.

        Parameters:
            target_delta   : desired position change
            mid_price      : current mid price
            fill_ratio     : fraction filled [0–1]
            executed_price : price after slippage/latency
        """

        filled_qty = target_delta * fill_ratio
        self.execute_trade(filled_qty, executed_price)

        equity = self.mark_to_market(mid_price)

        self.history.append({
            "cash": self.cash,
            "position": self.position,
            "equity": equity
        })

        return equity
