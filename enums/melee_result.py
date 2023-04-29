from enum import Enum


class MeleeResult(Enum):
    Miss = 0
    Hit = 1
    Crit = 2
    Dodge = 3
    Glance = 4
