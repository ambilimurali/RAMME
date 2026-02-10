from enum import Enum

class MarketRegime(Enum):
    TREND = 1
    MEAN_REVERT = 2
    VOLATILE = 3
    ILLIQUID = 4
    SHOCK = 5
