# File: gui/widgets.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSlider, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt

# ---------- Custom Slider with Label ----------
class LabeledSlider(QWidget):
    def __init__(self, label, min_val, max_val, default_val):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel(f"{label}: {default_val}")
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default_val)
        self.slider.valueChanged.connect(lambda v: self.label.setText(f"{label}: {v}"))
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def get_value(self):
        return self.slider.value()


# ---------- Tick Table ----------
class TickTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tick", "Regime", "Equity", "Traded", "Return"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_tick(self, tick, regime, equity, traded, ret):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(tick)))
        self.table.setItem(row, 1, QTableWidgetItem(regime))
        self.table.setItem(row, 2, QTableWidgetItem(f"{equity:,.2f}"))
        self.table.setItem(row, 3, QTableWidgetItem("Yes" if traded else "No"))
        self.table.setItem(row, 4, QTableWidgetItem(f"{ret:.5f}"))
        self.table.scrollToBottom()


# ---------- Summary Stats Panel ----------
class SummaryStatsPanel(QWidget):
    """Display PnL, trades, max drawdown per regime."""
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
        self.labels = {}
        metrics = ["PnL", "Trades", "Max Drawdown"]
        regimes = ["VOLATILE", "TREND", "MEAN_REVERT"]

        for i, regime in enumerate(regimes):
            group = QGroupBox(regime)
            group_layout = QVBoxLayout()
            self.labels[regime] = {}
            for metric in metrics:
                lbl = QLabel(f"{metric}: 0")
                self.labels[regime][metric] = lbl
                group_layout.addWidget(lbl)
            group.setLayout(group_layout)
            layout.addWidget(group, 0, i)

        self.setLayout(layout)

    def update_stats(self, stats_dict):
        """
        stats_dict: {regime: {"PnL": val, "Trades": val, "Max Drawdown": val}}
        """
        for regime, metrics in stats_dict.items():
            if regime in self.labels:
                for metric, val in metrics.items():
                    if metric in self.labels[regime]:
                        self.labels[regime][metric].setText(f"{metric}: {val}")


# ---------- Pause/Resume Buttons ----------
class SimulationControls(QWidget):
    """Start, pause, resume, reset simulation buttons."""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.reset_btn = QPushButton("Reset")

        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.resume_btn)
        layout.addWidget(self.reset_btn)
        self.setLayout(layout)
