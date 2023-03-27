""" player class """
from random import randrange
import time

from lib.info import Info
from lib.data import Data


class Player:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):
        """ read in the config files """
        self.info = Info()
        self._species = Data().species
        self._classes = Data().classes
        self._stat_ranges = Data().stat_ranges

        # player info
        self.name = None
        self.species = None
        self.p_class = None

        # game settings
        self.room = [1, 4, 2]  # north plaza
        self.level = 1
        self.experience = 0
        self.gold = 0

        # stats
        self.str = 0
        self.str_max = 0
        self.dex = 0
        self.dex_max = 0
        self.con = 0
        self.con_max = 0
        self.int = 0
        self.int_max = 0
        self.wis = 0
        self.wis_max = 0
        self.cha = 0
        self.cha_max =0

        # hp and mana
        self.vit = 0
        self.vit_max = 0
        self.man = 0
        self.man_max = 0

        # attacks
        self.att = 0
        self.ext = 0

        # things that happen to you
        self.inventory = None
        self.spells = None
        self.status = None
        self.fatigue = time.time()
        self.max_enc = 0
        self.enc = 0
        self.max_inv = 0

        # equipped items
        self.weapon = None
        self.armor = None
        self.cid = 0

        # timers
        self.regeneration_ticker = 0.0
        self.hunger_ticker = 0.0
        self.thirst_ticker = 0.0
        self.mental_exhaustion_ticker = 0.0
        self.rest_ticker = 0.0
        self.combat_ticker = 0.0
        self.paralysis_ticker = 0.0

        # stat modifiers
        self._buy_modifier = [
            50,
            50, 50, 50, 50, 50, 50, 50, 40, 40, 40,
            30, 30, 30, 30, 20, 20, 20, 10, 10, 10,
            10, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        self._sustenanceModifier = [
            10,
            9, 9, 9, 8, 8, 8, 7, 7, 7, 6,
            6, 6, 5, 5, 5, 4, 4, 4, 3, 3,
            3, 2, 2, 2, 1, 1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

    def set_base_stats(self):
        """ set base stats based on class/species """
        species = self._species[self.species]
        p_class = self._classes[self.p_class]

        self.str = self.str_max = species['str'] + p_class['str'] \
            + randrange(self._stat_ranges['min_str'],
                        self._stat_ranges['max_str'])
        self.dex = self.dex_max = species['dex'] + p_class['dex'] \
            + randrange(self._stat_ranges['min_dex'],
                        self._stat_ranges['max_dex'])
        self.con = self.con_max = species['con'] + p_class['con'] \
            + randrange(self._stat_ranges['min_con'],
                        self._stat_ranges['max_con'])
        self.int = self.int_max = species['int'] + p_class['int'] \
            + randrange(self._stat_ranges['min_int'],
                        self._stat_ranges['max_int'])
        self.wis = self.wis_max = species['wis'] + p_class['wis'] \
            + randrange(self._stat_ranges['min_wis'],
                        self._stat_ranges['max_wis'])
        self.cha = self.cha_max = species['cha'] + p_class['cha'] \
            + randrange(self._stat_ranges['min_cha'],
                        self._stat_ranges['max_cha'])
        self.vit = self.vit_max = species['vit'] + p_class['vit'] \
            + randrange(self._stat_ranges['min_vit'],
                        self._stat_ranges['max_vit'])
        self.man = self.man_max = p_class['max_mana_per_level'] * self.level

        self.gold = randrange(p_class['start_gold_min'],
                              p_class['start_gold_max'])

        self.att = p_class['max_base_number_of_attacks']
        self.ext = p_class['extra_attack_each_level']
        self.cid = p_class['id']
        self.max_enc = self.info.get_max_enc(self.str)
        self.inventory = []
        self.max_inv = 8

        # timers
        self.regeneration_ticker = time.time()
        self.hunger_ticker = time.time()  # setHungerTicker(int
        self.thirst_ticker = time.time()  # setThirstTicker(int
        self.mental_exhaustion_ticker = time.time()  # setMentalExhaustionTicker(int
        self.rest_ticker = time.time()  # setRestTicker(int
        self.combat_ticker = time.time()  # setCombatTicker(int
        self.paralysis_ticker = time.time()  # setParalysisTicker(int

        print(self.str, self.dex, self.con, self.int, self.wis, self.cha)
        print(self.vit, self.gold)

    def get_buy_modifier(self):
        """ return buy modifier based on current cha """
        return self._buy_modifier[self.cha_max]

    def get_class(self):
        """ return name of current class """
        return self._classes[self.p_class]['type']

    def get_species(self):
        """ return name of current species """
        return self._species[self.species]['type']


