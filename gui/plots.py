# File: gui/plots.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class EquityPlot(QWidget):
    """Widget to plot the equity curve."""

    def __init__(self, title="Equity Curve"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title)
        self.ax.set_xlabel("Tick")
        self.ax.set_ylabel("Equity")
        self.line = None  # store line object for live updates

    def update_plot(self, tick_data, title=None):
        """Update the equity curve with tick_data."""
        if not tick_data:
            return

        ticks = [d["tick"] for d in tick_data]
        equity = [d["equity"] for d in tick_data]

        if self.line is None:
            # First plot
            self.line, = self.ax.plot(ticks, equity, label="Equity", color="blue")
            self.ax.legend(loc="upper left")
        else:
            # Update existing line for live plotting
            self.line.set_data(ticks, equity)
            self.ax.relim()
            self.ax.autoscale_view()

        self.ax.set_title(title if title else "Equity Curve")
        self.ax.set_xlabel("Tick")
        self.ax.set_ylabel("Equity")
        self.canvas.draw()


class PnLPlot(QWidget):
    """Widget to plot PnL per regime."""

    def __init__(self, title="PnL by Regime"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title(title)
        self.ax.set_xlabel("Tick")
        self.ax.set_ylabel("PnL")
        self.lines = {}  # store lines per regime for live updates

        # Optional: fixed colors per regime
        self.colors = {"VOLATILE": "red", "TREND": "green", "MEAN_REVERT": "blue"}

    def update_plot(self, tick_data, title=None):
        """Update PnL per regime."""
        if not tick_data:
            self.ax.set_title("PnL by Regime (No Data)")
            self.canvas.draw()
            return

        regimes = sorted(set(d["regime"] for d in tick_data))
        for regime in regimes:
            regime_data = [d["equity"] for d in tick_data if d["regime"] == regime]
            ticks = [d["tick"] for d in tick_data if d["regime"] == regime]
            if not ticks:
                continue

            pnl = [regime_data[i] - regime_data[0] for i in range(len(regime_data))]

            if regime not in self.lines:
                # First plot for this regime
                self.lines[regime], = self.ax.plot(
                    ticks,
                    pnl,
                    label=regime,
                    color=self.colors.get(regime, "black")
                )
                self.ax.legend(loc="upper left")
            else:
                # Update existing line for live plotting
                self.lines[regime].set_data(ticks, pnl)

        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.set_title(title if title else "PnL by Regime")
        self.ax.set_xlabel("Tick")
        self.ax.set_ylabel("PnL")
        self.canvas.draw()
