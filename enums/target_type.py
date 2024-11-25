from enum import IntEnum


class TargetType(IntEnum):
    PvpAreaEffect = 1
    RoomAreaEffect = 2
    RoomPlayer = 3
    SingleTarget = 4
    Summon = 5
