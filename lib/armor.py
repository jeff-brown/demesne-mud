""" armor class """
from lib import data


class Armor:
    """
    @DynamicAttrs
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(f"init {__name__}")
        self._armor = data.armor

        for key in data.armor[vnum]:
            setattr(self, key, data.armor[vnum][key])

    def can_use(self, _player):
        """ check if a player can use an item """
        return bool(int(bin(_player.cid & self.classes), 2))

    def get_by_type(self, _type):
        """ ger armor vnum by type """
        for vnum, armor in self._armor:
            if armor['type'] == _type.lower():
                return vnum


