class PositionManager:
    """
    Manages target position and exposure based on signal and risk limits.
    """

    def __init__(self, max_position=1.0):
        self.position = 0.0
        self.max_position = max_position

    def target_position(self, signal, strength):
        """
        Compute target position using signal direction and confidence.

        Parameters:
            signal   : -1, 0, +1
            strength : [0.0 – 1.0]

        Returns:
            target position
        """
        raw_target = signal * strength * self.max_position
        return max(min(raw_target, self.max_position), -self.max_position)

    def delta(self, target):
        """
        Change required to reach target.
        """
        return target - self.position

    def update(self, delta):
        """
        Apply executed delta to position.
        """
        self.position += delta

    def exposure(self):
        """
        Current absolute exposure.
        """
        return abs(self.position)
