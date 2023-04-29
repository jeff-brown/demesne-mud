""" player class """
from enum import Enum
from random import randint
import time

from lib.info import Info
from lib.data import Data

from enums.status import Status


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

        print(f"init {__name__}")

        # player info
        self.name = None
        self.species = None
        self.p_class = None
        self.is_playing = False

        # game settings
        self.room = [1, 4, 2]  # north plaza
        self.level = 2
        self.experience = 0
        self.gold = 0

        # stats
        self.str = 0
        self.str_max = 0
        self.str_boo = 0
        self.str_ticker = time.time()

        self.dex = 0
        self.dex_max = 0
        self.dex_boo = 0
        self.dex_ticker = time.time()

        self.con = 0
        self.con_max = 0
        self.con_boo = 0
        self.con_ticker = time.time()

        self.int = 0
        self.int_max = 0
        self.int_boo = 0
        self.int_ticker = time.time()

        self.wis = 0
        self.wis_max = 0
        self.wis_boo = 0
        self.wis_ticker = time.time()

        self.cha = 0
        self.cha_max = 0
        self.cha_boo = 0
        self.cha_ticker = time.time()

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
        self.status = Status.Healthy
        self.fatigue = time.time()
        self.max_enc = 0
        self.enc = 0
        self.max_inv = 8
        self.max_hunger = 6000
        self.max_thirst = 3000
        self.max_stat = 30
        self.min_stat = 5

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
        self.stat_ticker_max = 30

        # stat modifiers
        self._buy_modifier = [
            50,
            50, 50, 50, 50, 50, 50, 50, 40, 40, 40,
            30, 30, 30, 30, 20, 20, 20, 10, 10, 10,
            10, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        # sustenance modifier
        self._sustenance_modifier = [
            10,
            9, 9, 9, 8, 8, 8, 7, 7, 7, 6,
            6, 6, 5, 5, 5, 4, 4, 4, 3, 3,
            3, 2, 2, 2, 1, 1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]

        self._melee_hit_bonus = [
            -1,
            -1, -1, -1, -1,  0,  0,  0,  0,  0, 1,
            1, 1, 1, 1, 2, 2, 2, 2, 2, 3,
            3, 3, 3, 3, 4, 4, 4, 4, 4, 5,
            5, 5, 5, 5, 5, 6, 6, 6, 6, 6,
            7, 7, 7, 7, 7, 8, 8, 8, 8, 8
        ]

        self._rogue_skill_bonus = [
            1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
            5, 5, 5, 5, 5, 6, 6, 6, 6, 6,
            7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
            8, 8, 8, 8, 8, 8, 8, 8, 8, 8
        ]

        self._physical_damage_bonus = [
            0,
            0, 0, 0, 0, 0, 1, 1, 1, 1, 2,
            2, 2, 2, 2, 3, 3, 3, 3, 3, 3,
            4, 4, 4, 4, 5, 5, 5, 5, 5, 6,
            6, 6, 6, 7, 7, 7, 7, 8, 8, 8,
            8, 9, 9, 9, 9, 10, 10, 10, 10, 11
        ]

    def set_base_stats(self):
        """ set base stats based on class/species """
        species = self._species[self.species]
        p_class = self._classes[self.p_class]

        self.str = self.str_max = species['str'] + p_class['str'] \
            + randint(self._stat_ranges['min_str'],
                        self._stat_ranges['max_str'])
        self.dex = self.dex_max = species['dex'] + p_class['dex'] \
            + randint(self._stat_ranges['min_dex'],
                        self._stat_ranges['max_dex'])
        self.con = self.con_max = species['con'] + p_class['con'] \
            + randint(self._stat_ranges['min_con'],
                        self._stat_ranges['max_con'])
        self.int = self.int_max = species['int'] + p_class['int'] \
            + randint(self._stat_ranges['min_int'],
                        self._stat_ranges['max_int'])
        self.wis = self.wis_max = species['wis'] + p_class['wis'] \
            + randint(self._stat_ranges['min_wis'],
                        self._stat_ranges['max_wis'])
        self.cha = self.cha_max = species['cha'] + p_class['cha'] \
            + randint(self._stat_ranges['min_cha'],
                        self._stat_ranges['max_cha'])
        self.vit = self.vit_max = species['vit'] + p_class['vit'] \
            + randint(self._stat_ranges['min_vit'],
                        self._stat_ranges['max_vit'])
        self.man = self.man_max = p_class['max_mana_per_level'] * self.level

        self.gold = randint(p_class['start_gold_min'],
                              p_class['start_gold_max'])

        self.att = p_class['max_base_number_of_attacks']
        self.ext = p_class['extra_attack_each_level']
        self.cid = p_class['id']
        self.max_enc = self.info.get_max_enc(self.get_str())
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

        self.is_playing = True

        print(self.str, self.dex, self.con, self.int, self.wis, self.cha)
        print(self.vit, self.gold)

    def get_buy_modifier(self):
        """ return buy modifier based on current cha """
        return self._buy_modifier[self.get_cha()]

    def get_melee_hit_bonus(self):
        """ return buy modifier based on current cha """
        return self._melee_hit_bonus[self.get_int()]

    def get_rogue_skill_bonus(self):
        """ rogues hit stuff more better """
        return self._rogue_skill_bonus[self.get_int()]

    def get_physical_damage_bonus(self):
        """ rogues hit stuff more better """
        return self._physical_damage_bonus[self.get_str()]

    def get_class(self):
        """ return name of current class """
        return self._classes[self.p_class]['type']

    def get_species(self):
        """ return name of current species """
        return self._species[self.species]['type']

    def get_str(self):
        return self.str + self.str_boo

    def get_dex(self):
        return self.dex + self.dex_boo

    def get_int(self):
        return self.int + self.int_boo

    def get_cha(self):
        return self.cha + self.cha_boo

    def take_damage(self, damage):
        """
        take damage and determine if dead
        """
        self.vit -= damage
        if self.vit <= 0:
            return True
        return False

    def handle_death(self, items):
        """
        handle player death
        """
        soulstone = None
        for inv in self.inventory:
            if items[inv].type == "soulstone":
                soulstone = inv
                break

        self.hunger_ticker = time.time()
        self.thirst_ticker = time.time()
        self.vit = self.vit_max
        self.rest_ticker = time.time()
        self.status = Status.Healthy
        self.room = [1, 4, 1]  # 1st town temple

        if soulstone is not None:
            items.pop(soulstone)
            self.inventory.remove(soulstone)
        else:
            for inv in self.inventory:
                items.remove(inv)
                self.inventory.pop(inv)

            self.experience = int(self.experience * 0.8)
            self.gold = 0

    def has_light(self, location, items):
        """
        does this player have light?
        """
        print("self.room", self.room)
        print("location", location)






