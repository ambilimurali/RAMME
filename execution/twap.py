from execution.slippage import SlippageModel
from execution.latency import LatencyModel
from execution.fill import PartialFillModel

class TWAPExecutor:
    def __init__(self, slices=5):
        self.slices = slices
        self.slippage = SlippageModel()
        self.latency = LatencyModel()
        self.filler = PartialFillModel()

    def generate_orders(self, total_qty, mid_price, liquidity_score, spread):
        adj_slices = max(1, int(self.slices * liquidity_score))
        slice_qty = total_qty / adj_slices

        orders = []
        for _ in range(adj_slices):
            latency_ms = self.latency.sample_latency()

            fill_price = mid_price + spread / 2
            fill_price = self.slippage.apply(
                fill_price, slice_qty, liquidity_score
            )

            fill_ratio = self.filler.fill_ratio(liquidity_score)
            filled_qty = slice_qty * fill_ratio

            orders.append({
                "qty": filled_qty,
                "price": fill_price,
                "latency_ms": latency_ms
            })
        return orders
