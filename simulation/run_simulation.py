"""
RAMME: Regime-Adaptive Market Microstructure Engine
User-Friendly Runner Script with Trades, CSV Export, and Corrected Logic
----------------------------------
This script demonstrates RAMME in a stochastic market.
Equity, trades, and PnL per regime are tracked and saved for visualization.
"""

from engine.engine import RAMMEEngine
from strategy.signal import DirectionalSignal
from strategy.position import PositionManager
from execution.fill import PartialFillModel
from execution.slippage import SlippageModel
from execution.latency import LatencyModel
from backtest.simulator import BacktestSimulator
from backtest.pnl_attribution import RegimePnLTracker
from backtest.shock import ShockGenerator
from risk.governor import RiskGovernor
import random
import pandas as pd

# -------------------------
# Introduction
# -------------------------
print("========================================")
print("Welcome to RAMME: Regime-Adaptive Market Microstructure Engine")
print("Stochastic simulation with adaptive trading logic.")
print("Equity, trades, and PnL are tracked per market regime (VOLATILE, TREND, MEAN_REVERT).")
print("Per-tick results are saved to CSV for visualization.")
print("========================================\n")

# -------------------------
# Initialization
# -------------------------
engine = RAMMEEngine()
signal_engine = DirectionalSignal()
position_mgr = PositionManager()
fill_model = PartialFillModel()
slippage_model = SlippageModel()
latency_model = LatencyModel()
sim = BacktestSimulator(initial_cash=100000)
risk = RiskGovernor(max_drawdown=0.05)
pnl_tracker = RegimePnLTracker()
shock = ShockGenerator()

# Synthetic price starting point
price = 100.0
vol_base = 0.01
vol_noise = 0.005

# -------------------------
# Store per-tick data
# -------------------------
tick_data = []

# -------------------------
# Simulation Loop
# -------------------------
for tick in range(30):
    # Apply stochastic shock to price
    stochastic_ret = random.gauss(0, vol_noise)
    price = shock.apply(price) * (1 + stochastic_ret)

    # Orderbook bid/ask
    bid = price - 0.1
    ask = price + 0.1
    bids = [(bid - 0.1, 10), (bid - 0.2, 8), (bid - 0.3, 6)]
    asks = [(ask + 0.1, 9), (ask + 0.2, 7), (ask + 0.3, 5)]
    engine.orderbook.update(bids, asks)

    # Engine observes market
    mid_price, regime, features = engine.on_tick(bid, ask, 10, 10)

    # --- Generate signal ---
    ret = features.get("return", 0.0)

    # Force trades in VOLATILE regime for demonstration
    if regime == "VOLATILE":
        signal = 1  # buy
        strength = 10
    else:
        signal, strength = signal_engine.generate(ret, regime)

    # --- Position Management ---
    target_pos = position_mgr.target_position(signal, strength)
    delta = position_mgr.delta(target_pos)

    traded = False
    if delta != 0 and risk.update(sim.equity):
        liquidity = features.get("liquidity", 0.5)
        fill_ratio = fill_model.fill_ratio(liquidity)
        latency_ms = latency_model.sample_latency()
        # Drifted & slippage-adjusted price
        drifted_price = mid_price * (1 + random.gauss(0, vol_base))
        executed_price = slippage_model.apply(drifted_price, abs(delta), liquidity)

        # Execute trade
        equity = sim.step(target_delta=delta, mid_price=mid_price, fill_ratio=fill_ratio, executed_price=executed_price)
        position_mgr.update(delta * fill_ratio)
        traded = True
    else:
        equity = sim.mark_to_market(mid_price)

    # Update PnL tracker
    pnl_tracker.update(regime, equity, traded=traded)

    # Store tick data
    tick_data.append({
        "tick": tick,
        "regime": regime,
        "equity": equity,
        "traded": traded,
        "return": ret
    })

    # Print tick summary
    print(f"Tick {tick:02d} | Regime: {regime} | Equity: {equity:,.2f} | Trades: {'Yes' if traded else 'No'}")

# -------------------------
# Final Summary
# -------------------------
print("\n========================================")
print("Simulation Complete: RAMME PnL Summary")
summary = pnl_tracker.report()
for key in summary["pnl"]:
    print(f"Regime: {key}")
    print(f"  Total PnL      : {summary['pnl'][key]:,.2f}")
    print(f"  Max Drawdown   : {summary['max_drawdown'][key]:.6f}")
    print(f"  Total Trades   : {summary['trades'][key]}")
print("========================================\n")

# -------------------------
# Export CSV for visualization
# -------------------------
df = pd.DataFrame(tick_data)
df.to_csv("RAMME/simulation_results.csv", index=False)
print("Per-tick simulation results saved to 'RAMME/simulation_results.csv'.")
print("Run 'visualize_simulation.py' to see plots of equity and PnL by regime.")

print("\nThank you for running RAMME! Demonstrates regime-adaptive microstructure trading in a stochastic environment.")
