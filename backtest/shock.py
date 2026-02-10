import random

class ShockGenerator:
    def __init__(self, shock_prob=0.2, shock_size=3.0):
        self.shock_prob = shock_prob
        self.shock_size = shock_size

    def apply(self, price):
        if random.random() < self.shock_prob:
            direction = random.choice([-1, 1])
            return price + direction * self.shock_size
        return price
