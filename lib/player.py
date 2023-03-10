""" player class """
from random import randrange
import time

from lib.info import Info


class Player:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):
        """ read in the config files """
        self.info = Info()
        self._species = self.info.get_species()
        self._classes = self.info.get_classes()
        self._stat_ranges = self.info.get_stat_ranges()

        self.name = None
        self.species = None
        self.p_class = None

        self.room = [1, 4, 2]  # north plaza
        self.level = 1
        self.experience = 0
        self.gold = 0

        self.str = 0
        self.dex = 0
        self.con = 0
        self.int = 0
        self.wis = 0
        self.cha = 0

        self.vit = 0
        self.att = 0
        self.ext = 0

        self.inventory = None
        self.spells = None
        self.status = None
        self.fatigue = time.time()

        self.weapon = None
        self.armor = None

    def set_base_stats(self):
        """ set base stats based on class/species """
        species = self._species[self.species]
        p_class = self._classes[self.p_class]

        self.str = species['str'] + p_class['str'] \
            + randrange(self._stat_ranges['min_str'],
                        self._stat_ranges['max_str'])
        self.dex = species['dex'] + p_class['dex'] \
            + randrange(self._stat_ranges['min_dex'],
                        self._stat_ranges['max_dex'])
        self.con = species['con'] + p_class['con'] \
            + randrange(self._stat_ranges['min_con'],
                        self._stat_ranges['max_con'])
        self.int = species['int'] + p_class['int'] \
            + randrange(self._stat_ranges['min_int'],
                        self._stat_ranges['max_int'])
        self.wis = species['wis'] + p_class['wis'] \
            + randrange(self._stat_ranges['min_wis'],
                        self._stat_ranges['max_wis'])
        self.cha = species['cha'] + p_class['cha'] \
            + randrange(self._stat_ranges['min_cha'],
                        self._stat_ranges['max_cha'])
        self.vit = species['vit'] + p_class['vit'] \
            + randrange(self._stat_ranges['min_vit'],
                        self._stat_ranges['max_vit'])

        self.gold = randrange(p_class['start_gold_min'],
                              p_class['start_gold_max'])

        self.att = p_class['max_base_number_of_attacks']
        self.ext = p_class['extra_attack_each_level']

        print(self.str, self.dex, self.con, self.int, self.wis, self.cha)
        print(self.vit, self.gold)

    def get_str(self):
        """ get current strength """
        return self.str

    def set_str(self, _str):
        """ set new strength """
        self.str = _str

    def get_dex(self):
        """ get current dexterity """
        return self.dex

    def set_dex(self, _dex):
        """ set new dexterity """
        self.dex = _dex

    def get_con(self):
        """ get current consitution """
        return self.con

    def set_con(self, _con):
        """ set new constitution """
        self.str = _con

    def get_int(self):
        """ get current intelligence """
        return self.int

    def set_int(self, _int):
        """ set new intelligence """
        self.dex = _int

    def get_wis(self):
        """ get current intelligence """
        return self.wis

    def set_wis(self, _wis):
        """ set new intelligence """
        self.dex = _wis

    def get_cha(self):
        """ get current intelligence """
        return self.cha

    def set_cha(self, _cha):
        """ set new intelligence """
        self.dex = _cha

    def get_vit(self):
        """ get current intelligence """
        return self.vit

    def set_vit(self, _vit):
        """ set new intelligence """
        self.dex = _vit

    def get_class(self):
        """ return name of current class """
        return self._classes[self.p_class]['type']

    def get_species(self):
        """ return name of current species """
        return self._species[self.species]['type']


