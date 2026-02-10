import os
import matplotlib.pyplot as plt
import pandas as pd

# -------------------------
# Load simulation data
# -------------------------
df = pd.read_csv("simulation_results.csv")

# Ensure folder exists
os.makedirs("RAMME", exist_ok=True)

# Compute per-tick PnL
df["pnl"] = df["equity"].diff().fillna(0)
df["traded"] = df["traded"].astype(bool)

# -------------------------
# Plot Equity over Time
# -------------------------
plt.figure(figsize=(12, 6))
plt.plot(df["tick"], df["equity"], label="Equity", color="blue")
plt.scatter(df["tick"][df["traded"]], df["equity"][df["traded"]], color="green", label="Trades Executed", marker="o")
plt.title("RAMME: Equity Over Time with Trades")
plt.xlabel("Tick")
plt.ylabel("Equity")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("RAMME/equity_plot.png")
plt.show()

# -------------------------
# Plot PnL by Regime
# -------------------------
regimes = df["regime"].unique()
plt.figure(figsize=(12, 6))
for r in regimes:
    regime_df = df[df["regime"] == r]
    pnl_cumsum = regime_df["pnl"].cumsum()
    plt.plot(regime_df["tick"], pnl_cumsum, label=f"PnL - {r}")

plt.title("RAMME: Cumulative PnL by Regime")
plt.xlabel("Tick")
plt.ylabel("Cumulative PnL")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("RAMME/pnl_by_regime.png")
plt.show()

# -------------------------
# Export to CSV
# -------------------------
df.to_csv("RAMME/simulation_results_export.csv", index=False)
print("Plots saved as PNG and results exported to 'simulation_results_export.csv'.")
