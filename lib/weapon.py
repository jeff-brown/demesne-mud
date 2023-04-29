""" Weapon class """
from lib import data


class Weapon:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(f"init {__name__}")
        self._weapons = data.weapons

        for key in data.weapons[vnum]:
            setattr(self, key, data.weapons[vnum][key])

    def can_use(self, _player):
        """ check if a player can use an item """
        return bool(int(bin(_player.cid & self.classes), 2))

    def get_by_type(self, _type):
        """ ger armor vnum by type """
        for vnum, weapon in self._weapons:
            if weapon['type'] == _type.lower():
                return vnum


