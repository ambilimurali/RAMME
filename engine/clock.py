from PyQt5.QtCore import QObject, pyqtSignal
import threading
import time

class SimulationClock(QObject):
    tick_signal = pyqtSignal(int)

    def __init__(self, tick_interval=0.5, max_ticks=100):
        super().__init__()
        self.tick_interval = tick_interval
        self.max_ticks = max_ticks
        self.running = False
        self._thread = None
        self._tick = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while self.running and self._tick < self.max_ticks:
            self.tick_signal.emit(self._tick)  # emits safely to GUI
            self._tick += 1
            time.sleep(self.tick_interval)

    def pause(self):
        self.running = False

    def resume(self):
        if not self.running:
            self.running = True
            self.start()  # start a new thread if stopped

    def stop(self):
        self.running = False
        self._tick = 0
