# File: simulation.py
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from engine.engine import RAMMEEngine
from clock import SimulationClock

# --- Initialize engine and clock ---
engine = RAMMEEngine()
tick_interval = 0.1  # seconds per tick
max_ticks = 100
clock = SimulationClock(tick_interval=tick_interval, max_ticks=max_ticks)

# --- Regimes for simulation ---
regimes = ["TREND", "MEAN_REVERT", "VOLATILE", "SHOCK", "ILLIQUID"]

# --- History storage ---
price_history = []
regime_history = []
liquidity_history = []
toxicity_history = []

# --- Matplotlib setup ---
plt.ion()
fig, ax = plt.subplots(2, 1, figsize=(10, 6))

price_line, = ax[0].plot([], [], label="Price", color='blue')
ax[0].set_ylabel("Price")
ax[0].legend()
ax[0].grid(True)

liquidity_line, = ax[1].plot([], [], label="Liquidity", color='green')
toxicity_line, = ax[1].plot([], [], label="Toxicity", color='red')
ax[1].set_ylabel("Score")
ax[1].legend()
ax[1].grid(True)

ax[1].set_xlabel("Tick")

# --- Tick handler ---
def handle_tick(tick):
    # Pick a regime randomly
    regime = np.random.choice(regimes)
    
    # Generate simulated price tick
    prices = engine.simulate_tick(regime, n_ticks=1)
    mid_price = prices[-1]

    # Simulate bid/ask around mid
    spread = 0.01 * mid_price
    bid = mid_price - spread/2
    ask = mid_price + spread/2
    bid_size = np.random.randint(50, 150)
    ask_size = np.random.randint(50, 150)

    # Update engine
    mid, detected_regime, features = engine.on_tick(bid, ask, bid_size, ask_size)

    # Save history
    price_history.append(mid)
    regime_history.append(detected_regime)
    liquidity_history.append(features["liquidity"])
    toxicity_history.append(features["toxicity"])

    # Update plots
    ticks = list(range(len(price_history)))
    price_line.set_data(ticks, price_history)
    liquidity_line.set_data(ticks, liquidity_history)
    toxicity_line.set_data(ticks, toxicity_history)

    ax[0].relim()
    ax[0].autoscale_view()
    ax[1].relim()
    ax[1].autoscale_view()

    plt.pause(0.001)

# --- Connect signal ---
clock.tick_signal.connect(handle_tick)

# --- Run simulation ---
app = QApplication(sys.argv)
clock.start()
sys.exit(app.exec_())
