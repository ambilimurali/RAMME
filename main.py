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


# -------------------------
# Initialization
# -------------------------
engine = RAMMEEngine()

signal_engine = DirectionalSignal()
position_mgr = PositionManager(max_position=1.0)

fill_model = PartialFillModel()
slippage_model = SlippageModel()
latency_model = LatencyModel()

sim = BacktestSimulator(initial_cash=100000)
risk = RiskGovernor(
    max_drawdown=0.05,
    max_exposure=1.0,
    regime_limits={"VOLATILE": 0.5}
)

pnl_tracker = RegimePnLTracker()
shock = ShockGenerator()

price = 100.0


# -------------------------
# Main simulation loop
# -------------------------
for tick in range(30):
    price = shock.apply(price)

    bid = price - 0.1
    ask = price + 0.1

    bids = [(bid - 0.1, 10), (bid - 0.2, 8), (bid - 0.3, 6)]
    asks = [(ask + 0.1, 9), (ask + 0.2, 7), (ask + 0.3, 5)]

    engine.orderbook.update(bids, asks)

    mid_price, regime, features = engine.on_tick(bid, ask, 10, 10)

    # -------------------------
    # Strategy
    # -------------------------
    ret = features.get("return", 0.0)
    volatility = features.get("volatility", 0.01)

    signal, strength = signal_engine.generate(ret, regime, volatility)

    target_pos = position_mgr.target_position(signal, strength)
    delta = position_mgr.delta(target_pos)

    traded = False

    # -------------------------
    # Risk checks
    # -------------------------
    if delta != 0 and risk.allow_trade(regime, position_mgr.exposure()):
        liquidity = features.get("liquidity", 0.5)

        fill_ratio = fill_model.fill_ratio(liquidity, abs(delta))

        latency_ms = latency_model.sample_latency(regime)
        drifted_price = latency_model.apply_price_drift(mid_price, latency_ms, volatility)

        executed_price = slippage_model.apply(
            drifted_price,
            abs(delta),
            liquidity,
            side=1 if delta > 0 else -1,
            regime=regime
        )

        equity = sim.step(
            target_delta=delta,
            mid_price=mid_price,
            fill_ratio=fill_ratio,
            executed_price=executed_price
        )

        position_mgr.update(delta * fill_ratio)
        traded = True
    else:
        equity = sim.mark_to_market(mid_price)

    pnl_tracker.update(regime, equity, traded=traded)

    print(f"Tick {tick:02d} | Regime: {regime} | Equity: {equity:.2f}")

    if not risk.update(equity):
        print("KILL SWITCH TRIGGERED")
        break


# -------------------------
# Final Report
# -------------------------
print("\nPnL Attribution by Regime:")
print(pnl_tracker.report())
