# File: main_window.py

import sys
import random
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QPushButton

# --- Import your RAMME engine components ---
from engine.engine import RAMMEEngine
from engine.clock import SimulationClock
from strategy.signal import DirectionalSignal
from strategy.position import PositionManager
from execution.fill import PartialFillModel
from execution.slippage import SlippageModel
from execution.latency import LatencyModel
from backtest.simulator import BacktestSimulator
from backtest.pnl_attribution import RegimePnLTracker
from backtest.shock import ShockGenerator
from risk.governor import RiskGovernor

# --- Import reusable GUI widgets ---
from gui.plots import EquityPlot, PnLPlot
from gui.widgets import LabeledSlider, TickTable, SummaryStatsPanel, SimulationControls

DARK_STYLE = """
QMainWindow { background-color: #1b1b2f; color: #fff; }
QLabel { color: #fff; font-size: 12pt; }
QPushButton { background-color: #2e2e4d; color: #fff; border-radius: 5px; padding: 5px; }
QPushButton:hover { background-color: #4b4b7d; }
QLineEdit, QSpinBox { background-color: #2e2e4d; color: #fff; border-radius: 3px; padding: 3px; }
QSlider::handle { background: #4b4b7d; border-radius: 6px; }
QTableWidget { background-color: #ffffff; gridline-color: #444444; selection-background-color: #3e3e5d; selection-color: #ffffff; }
QHeaderView::section { background-color: #2e2e4d; color: #ffffff; }
QProgressBar { background-color: #2e2e4d; color: #fff; border-radius: 5px; }
QProgressBar::chunk { background-color: #4b4b7d; }
"""

class RAMMEWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAMME: Market Microstructure Engine")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet(DARK_STYLE)

        # -----------------------
        # Main Layouts
        # -----------------------
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QHBoxLayout()
        main_widget.setLayout(self.main_layout)

        # -----------------------
        # Control Panel (Left)
        # -----------------------
        self.control_panel = QVBoxLayout()
        self.main_layout.addLayout(self.control_panel, 1)

        self.equity_input = LabeledSlider("Initial Equity", 10000, 1000000, 100000)
        self.tick_input = LabeledSlider("Number of Ticks", 10, 1000, 30)
        self.vol_slider = LabeledSlider("Volatility Magnitude", 1, 100, 10)
        self.dd_slider = LabeledSlider("Max Drawdown (%)", 1, 20, 5)
        self.control_panel.addWidget(self.equity_input)
        self.control_panel.addWidget(self.tick_input)
        self.control_panel.addWidget(self.vol_slider)
        self.control_panel.addWidget(self.dd_slider)

        self.sim_controls = SimulationControls()  # create the widget
        self.control_panel.addWidget(self.sim_controls)

        self.stats_panel = SummaryStatsPanel()
        self.control_panel.addWidget(self.stats_panel)

        self.tick_table = TickTable()
        self.control_panel.addWidget(self.tick_table)


        self.save_btn = QPushButton("Save CSV")
        self.control_panel.addWidget(self.save_btn)
        self.save_btn.clicked.connect(self.save_csv)

        # -----------------------
        # Plot Panel (Right)
        # -----------------------
        self.plot_panel = QVBoxLayout()
        self.main_layout.addLayout(self.plot_panel, 3)

        self.equity_plot = EquityPlot()
        self.pnl_plot = PnLPlot()
        

        self.plot_panel.addWidget(self.equity_plot)
        self.plot_panel.addWidget(self.pnl_plot)
        

        # -----------------------
        # Simulation Variables
        # -----------------------
        self.tick_data = []
        self.clock = None  # will hold SimulationClock

        # -----------------------
        # Connect Buttons
        # -----------------------
         
        self.sim_controls.start_btn.clicked.connect(self.start_simulation)
        self.sim_controls.pause_btn.clicked.connect(self.pause_simulation)
        self.sim_controls.resume_btn.clicked.connect(self.resume_simulation)
        self.sim_controls.reset_btn.clicked.connect(self.reset_simulation)

    # -----------------------
    # Simulation Control Methods
    # -----------------------
    def start_simulation(self):
        self.init_simulation()
        # Setup clock with tick_interval and max_ticks
        self.clock = SimulationClock(tick_interval=0.5, max_ticks=self.max_ticks)
        self.clock.tick_signal.connect(self.simulation_step)
        self.clock.start()

    def pause_simulation(self):
        if self.clock:
            self.clock.pause()

    def resume_simulation(self):
        if self.clock:
            self.clock.resume()

    def reset_simulation(self):
        if self.clock:
            self.clock.stop()
        self.tick_data = []
        self.equity_plot.update_plot([])
        self.pnl_plot.update_plot([])
        self.tick_table.table.setRowCount(0)
        self.stats_panel.update_stats({
            "VOLATILE": {"PnL": 0, "Trades": 0, "Max Drawdown": 0},
            "TREND": {"PnL": 0, "Trades": 0, "Max Drawdown": 0},
            "MEAN_REVERT": {"PnL": 0, "Trades": 0, "Max Drawdown": 0}
        })

    # -----------------------
    # Initialize Simulation
    # -----------------------
    def init_simulation(self):
        self.tick = 0
        self.tick_data = []
        self.max_ticks = self.tick_input.get_value()
        initial_cash = self.equity_input.get_value()
        self.vol_base = self.vol_slider.get_value() / 1000
        self.vol_noise = self.vol_base / 2
        max_dd = self.dd_slider.get_value() / 100

        self.engine = RAMMEEngine()
        self.signal_engine = DirectionalSignal()
        self.position_mgr = PositionManager()
        self.fill_model = PartialFillModel()
        self.slippage_model = SlippageModel()
        self.latency_model = LatencyModel()
        self.sim = BacktestSimulator(initial_cash=initial_cash)
        self.risk = RiskGovernor(max_drawdown=max_dd)
        self.pnl_tracker = RegimePnLTracker()
        self.shock = ShockGenerator()
        self.price = 100.0

    # -----------------------
    # Simulation Step (called by clock)
    # -----------------------
    def simulation_step(self, tick_num=None):
        # tick_num is optional, clock passes it
        self.tick = tick_num if tick_num is not None else self.tick
        if self.tick >= self.max_ticks:
            self.pause_simulation()
            return

        # --- Price shock ---
        stochastic_ret = random.gauss(0, self.vol_noise)
        self.price = self.shock.apply(self.price) * (1 + stochastic_ret)
        bid = self.price - 0.1
        ask = self.price + 0.1
        bids = [(bid - 0.1, 10), (bid - 0.2, 8), (bid - 0.3, 6)]
        asks = [(ask + 0.1, 9), (ask + 0.2, 7), (ask + 0.3, 5)]
        self.engine.orderbook.update(bids, asks)

        mid_price, regime, features = self.engine.on_tick(bid, ask, 10, 10)
        ret = features.get("return", 0.0)

        # --- Signal & Trade ---
        if regime == "VOLATILE":
            signal, strength = 1, 10
        else:
            signal, strength = self.signal_engine.generate(ret, regime)

        target_pos = self.position_mgr.target_position(signal, strength)
        delta = self.position_mgr.delta(target_pos)
        traded = False

        if delta != 0 and self.risk.update(self.sim.equity):
            liquidity = features.get("liquidity", 0.5)
            fill_ratio = self.fill_model.fill_ratio(liquidity)
            drifted_price = mid_price * (1 + random.gauss(0, self.vol_base))
            executed_price = self.slippage_model.apply(drifted_price, abs(delta), liquidity)
            equity = self.sim.step(target_delta=delta, mid_price=mid_price,
                                   fill_ratio=fill_ratio, executed_price=executed_price)
            self.position_mgr.update(delta * fill_ratio)
            traded = True
        else:
            equity = self.sim.mark_to_market(mid_price)

        self.pnl_tracker.update(regime, equity, traded=traded)

        # --- Save tick data ---
        self.tick_data.append({
            "tick": self.tick,
            "regime": regime,
            "equity": equity,
            "traded": traded,
            "return": ret
        })

        # --- Update GUI ---
        self.equity_plot.update_plot(self.tick_data)
        self.pnl_plot.update_plot(self.tick_data)
        self.tick_table.add_tick(self.tick, regime, equity, traded, ret)

        # --- Update summary stats ---
        stats = {}
        for r in ["VOLATILE", "TREND", "MEAN_REVERT"]:
            pnl = sum(d["equity"] - self.tick_data[0]["equity"] if d["regime"] == r else 0 for d in self.tick_data)
            trades = sum(1 for d in self.tick_data if d["regime"] == r and d["traded"])
            max_dd = min([d["equity"] for d in self.tick_data if d["regime"] == r] + [equity]) - self.tick_data[0]["equity"]
            stats[r] = {"PnL": round(pnl,2), "Trades": trades, "Max Drawdown": round(abs(max_dd),2)}
        self.stats_panel.update_stats(stats)

        self.tick += 1

    # -----------------------
    # Save CSV
    # -----------------------
    def save_csv(self):
        if not self.tick_data:
            return
        df = pd.DataFrame(self.tick_data)
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            df.to_csv(path, index=False)


# --------------------------
# Run Application
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAMMEWindow()
    window.show()
    sys.exit(app.exec_())
