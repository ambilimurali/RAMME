RAMME: Market Microstructure Engine

RAMME is a Python-based market microstructure simulation engine with a GUI that enables real-time simulation of price, liquidity, and PnL per regime. It supports regime-based tick simulation, live plotting, and basic trade execution with risk and slippage modeling.

Features
Market State Engine (RAMMEEngine)
- Computes mid-price, bid-ask spread, microstructure features, liquidity, and toxicity.
- Detects market regimes: TREND, MEAN_REVERT, VOLATILE, SHOCK, ILLIQUID.
- Regime-based tick simulation with drift, mean-reversion, volatility, shocks, and liquidity effects.

Simulation Controls
- Start, Pause, Resume, Reset.
- Adjustable parameters: Initial equity, Number of ticks, Volatility, Maximum drawdown.

Live Plotting
- Equity curve updates in real-time.
- PnL per regime with consistent color coding.
- Legends automatically updated.

Trade Execution
- Signal-based position management.
- Partial fills, slippage, latency, and risk governance.
- Shock events incorporated into price dynamics.

Data Export
- Save simulation ticks to CSV for post-analysis.

Dependencies
- Python 3.10+
- PyQt5
- matplotlib
- pandas
- numpy
- Usage

Launch the GUI:
python main_window.py


Adjust parameters on the control panel:
- Initial equity
- Number of ticks
- Volatility magnitude
- Maximum drawdown

Use Simulation Controls:
Start – begin simulation
Pause – pause simulation
Resume – resume simulation
Reset – reset simulation and plots

Observe live plots:
Top panel: Equity curve
Bottom panel: PnL per regime

Save simulation data to CSV using the Save CSV button.

Project Structure
RAMME/
│
├── engine/              # Market state engine and clock
│   ├── engine.py        # RAMMEEngine core logic
│   └── clock.py         # Simulation clock
│
├── strategy/            # Signal and position management
│   ├── signal.py
│   └── position.py
│
├── execution/           # Fill, slippage, and latency models
│   ├── fill.py
│   ├── slippage.py
│   └── latency.py
│
├── backtest/            # Simulation and PnL tracking
│   ├── simulator.py
│   ├── pnl_attribution.py
│   └── shock.py
│
├── risk/                # Risk management
│   └── governor.py
│
├── gui/                 # GUI widgets and plots
│   ├── plots.py
│   └── widgets.py
│
└── main_window.py       # Main GUI application

Features in Depth
- Regime-Based Tick Simulation
- TREND → persistent drift
- MEAN_REVERT → pull to moving average
- VOLATILE → high variance
- SHOCK → rare extreme moves
- ILLIQUID → thin order book, slippage spikes

Microstructure Metrics
- Mid-price, spread, returns, liquidity, and toxicity scores updated each tick.
- Sanity checks: price > 0, spread ≥ 0, liquidity ≥ 0.

GUI Widgets
- Custom sliders and panels for inputs and statistics.
- Tick table to view per-tick details.
- Plots update live with legends and color-coded regimes.

Future Enhancements
- Integrate order flow simulation for multi-asset markets.
- Advanced risk and portfolio management.
- Hardware-in-the-loop validation for real-time testing.
- Machine learning models for regime prediction.

