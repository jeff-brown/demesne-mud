""" armor class """
from lib import data


class Npc:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """
        print(vnum)

        for key in data.npcs[vnum]:
            setattr(self, key, data.npcs[vnum][key])
