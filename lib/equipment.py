""" armor class """
from lib import data
from lib.container import ConfigSection


class Equipment:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(f"init {__name__}")

        self._equipment = data.equipment

        for key in data.equipment[vnum]:
            setattr(self, key, data.equipment[vnum][key])

    def can_use(self, _player):
        """ check if a player can use an item """
        return bool(int(bin(_player.cid & self.classes), 2))



