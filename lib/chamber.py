""" armor class """
from lib import data
from lib.npc import Npc
from lib.mob import Mob
from lib.equipment import Equipment


class Chamber:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, vnum):
        """ read in the config files """

        print(f"init {__name__}")

        for key in data.chambers[vnum]:
            setattr(self, key, data.chambers[vnum][key])
        setattr(self, "vnum", vnum)

        self._dark = ['dark']

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

    def is_illuminated(self, uid, pids_here, players, items):
        """ check to see if room is illuminated """
        print(players)
        print(pids_here)

        dark = bool(list(set(self.flags).intersection(set(self._dark))))

        if not dark:
            return True

        for pid, player in players.items():
            if pid in pids_here or pid == uid:
                for item in player.inventory:
                    if not isinstance(items[item], Equipment):
                        continue

                    if items[item].equip_sub_type == 'light':
                        print(items[item].type, items[item].is_activated)
                        if items[item].is_activated:
                            return True

                    if items[item].equip_sub_type == 'eternal light':
                        return True

        return False

