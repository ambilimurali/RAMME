from regime.states import MarketRegime

class StrategyMorpher:
    def morph(self, regime):
        params = {}

        if regime == MarketRegime.TREND:
            params["position_size"] = 1.5
            params["stop_loss"] = 2.0

        elif regime == MarketRegime.MEAN_REVERT:
            params["position_size"] = 0.7
            params["stop_loss"] = 0.5

        elif regime == MarketRegime.SHOCK:
            params["position_size"] = 0.2
            params["stop_loss"] = 0.2

        else:
            params["position_size"] = 0.5
            params["stop_loss"] = 1.0

        return params
