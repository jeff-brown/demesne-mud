""" armor class """
from lib import data
from lib.npc import Npc


class Chamber:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """

        for key in data.chambers[vnum]:
            setattr(self, key, data.chambers[vnum][key])
        setattr(self, "vnum", vnum)

        self._init_npcs()

    def _init_npcs(self):
        """
        initialize npcs in rooms
        """
        if self.npcs:
            for index, npc in enumerate(self.npcs):
                self.npcs[index] = Npc(npc)

    def is_town(self):
        """
        is this room in a town
        """
        print(self.terrain)
        if self.terrain == 'town':
            print('is town')
            return True
        print('is not town')
        return False

