class DirectionalSignal:
    """
    Regime-aware directional signal generator.

    Output:
        signal: -1 (SHORT), 0 (FLAT), +1 (LONG)
        strength: [0.0 – 1.0] confidence used for sizing later
    """

    def generate(self, ret, regime, volatility=None):
        """
        Parameters:
            ret         : return or price delta
            regime      : market regime string
            volatility  : optional volatility metric

        Returns:
            (signal, strength)
        """

        # Default
        signal = 0
        strength = 0.0

        if regime == "TREND":
            signal = 1 if ret > 0 else -1
            strength = min(abs(ret) * 10, 1.0)

        elif regime == "MEAN_REVERT":
            signal = -1 if ret > 0 else 1
            strength = min(abs(ret) * 8, 1.0)

        elif regime == "VOLATILE":
            # Trade ONLY if move is strong enough
            if volatility is not None and abs(ret) > volatility:
                signal = 1 if ret > 0 else -1
                strength = min(abs(ret) / volatility, 1.0)
            else:
                signal = 0
                strength = 0.0

        elif regime == "QUIET":
            # Avoid trading low-entropy markets
            signal = 0
            strength = 0.0

        return signal, strength
