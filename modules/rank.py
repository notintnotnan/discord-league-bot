from enum import Enum

from functools import total_ordering

class Tier(int, Enum):
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4
    EMERALD = 5
    DIAMOND = 6
    MASTER = 7
    GRANDMASTER = 8
    CHALLENGER = 9

@total_ordering
class Rank:
    def __init__(self, tier: Tier, division: int | None):
        if isinstance(tier, str):
            tier = Tier[tier.upper()]
        self.tier = tier
        self.division = int(division) if division is not None else None

    def _numeric_value(self):
        base = self.tier * 10

        if self.division is not None:
            return base - (self.division*0.1)
        
        return base
    
    def __lt__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self._numeric_value() < other._numeric_value()
    
    def __eq__(self, other):
        if not isinstance(other, Rank):
            return NotImplemented
        return self.tier == other.tier and self.division == other.division