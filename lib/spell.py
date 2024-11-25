""" spell class """
from lib import data


class Spell:
    """
    @DynamicAttrs
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(f"init {__name__}")
        self._spells = data.spells

        for key in data.spells[vnum]:
            setattr(self, key, data.spells[vnum][key])

    def get_level(self):
        """
        spell level is based on mana
        """
        return (self.mana * 2) - 1
