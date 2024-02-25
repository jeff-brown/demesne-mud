""" armor class """
from lib import data


class Npc:
    """
    @DynamicAttrs
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(vnum)

        print(f"init {__name__}")

        for key in data.npcs[vnum]:
            setattr(self, key, data.npcs[vnum][key])
