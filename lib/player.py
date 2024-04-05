""" player class """
import random
from random import randint
import time

from lib import data

from enums.status import Status


class Player:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):
        """ read in the config files """
        self._species = data.species
        self._classes = data.classes
        self._stat_ranges = data.stat_ranges
        self._spell_casters = [8, 2, 3, 6]

        print(f"init {__name__}")

        # player info
        self.name = None
        self.species = None
        self.p_class = None
        self.is_playing = False
        self.resting = False

        # game settings
        self.room = [1, 4, 2]  # north plaza
        self.level = 1
        self.exp_base = 0
        self.experience = 100000000
        self.gold = 0
        self.combat_skill = 70  # 70, yep 70
        self.vault_balance = 0

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
        self.max_base_attacks = 0
        self.extra_attack_each_level = 0
        self.attacks = 0

        # things that happen to you
        self.inventory = None
        self.spellbook = None
        self.status = Status.Healthy
        self.fatigue = time.time()
        self.max_enc = 0
        self.enc = 0
        self.max_inv = 8
        self.max_spells = 8
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
        self.rest_ticker = 0
        self.combat_ticker = 0
        self.paralysis_ticker = 0.0
        self.stat_ticker_max = 30

        self._stat_increase_chance = 25

        self._attack_number_bonus = [
            0,                             # 0
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 1 - 10
            0, 0, 0, 0, 1, 1, 1, 1, 1, 1,  # 11 - 20
            1, 1, 1, 1, 1, 1, 1, 1, 1, 2,  # 21 - 30
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 31 - 40
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2   # 41 - 50
        ]

        self._max_encumbrance = [
            0,
            50, 100, 150, 200, 250, 300, 350, 400, 450, 500,
            550, 600, 650, 700, 750, 800, 850, 900, 950, 1000,
            1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500,
            1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000,
            2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450, 2500
        ]

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

        self._hp_bonus = [
            0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            1, 1, 1, 1, 2, 2, 2, 2, 2, 3,
            3, 3, 3, 3, 4, 4, 4, 4, 4, 5,
            5, 5, 5, 6, 6, 6, 6, 7, 7, 7,
            7, 8, 8, 8, 8, 9, 9, 9, 9, 10
        ]

    def get_attack_number_bonus(self):
        """ look up the proper bonus based on agi"""
        return self._attack_number_bonus[self.get_dex()]

    def get_max_enc(self, _str):
        """ return max encumbrance based on strength"""
        return self._max_encumbrance[_str]

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
                      self._stat_ranges['max_vit']) \
            + self._hp_bonus[self.con]
        self.man = self.man_max = p_class['max_mana_per_level'] * self.level

        self.gold = (randint(p_class['start_gold_min'],
                             p_class['start_gold_max'])) + 1000

        self.max_base_attacks = p_class['max_base_number_of_attacks']
        self.extra_attack_each_level = p_class['extra_attack_each_level']
        self.attacks = self.get_max_attacks()
        self.cid = p_class['id']
        self.max_enc = self.get_max_enc(self.get_str())
        self.inventory = []
        self.spellbook = []
        self.max_inv = 8
        self.max_spells = 8
        self.exp_base = p_class['base_exp']

        # timers
        self.regeneration_ticker = time.time()
        self.hunger_ticker = time.time()  # setHungerTicker(int
        self.thirst_ticker = time.time()  # setThirstTicker(int
        self.mental_exhaustion_ticker = time.time()  # setMentalExhaustionTicker(int
        self.paralysis_ticker = time.time()  # setParalysisTicker(int

        self.is_playing = True

        print(self.str, self.dex, self.con, self.int, self.wis, self.cha)
        print(self.vit, self.gold)

    def increase_int(self, amt=1):
        """ increase int by amt """
        self.int += amt
        self.int_max += amt

    def increase_wis(self, amt=1):
        """ increase int by amt """
        self.wis += amt
        self.wis_max += amt

    def increase_str(self, amt=1):
        """ increase int by amt """
        self.str += amt
        self.str_max += amt

    def increase_con(self, amt=1):
        """ increase int by amt """
        self.con += amt
        self.con_max += amt

    def increase_dex(self, amt=1):
        """ increase int by amt """
        self.dex += amt
        self.dex_max += amt

    def increase_cha(self, amt=1):
        """ increase int by amt """
        self.cha += amt
        self.cha_max += amt

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
        self.set_rest_ticker(15)
        self.reset_attacks()
        self.status = Status.Healthy
        self.room = [1, 4, 1]  # 1st town temple

        if soulstone is not None:
            items.pop(soulstone)
            self.inventory.remove(soulstone)
        else:
            for inv in self.inventory:
                items.pop(inv)
                self.inventory.remove(inv)
            print(self.experience, self.gold)
            self.experience = int(self.experience * 0.8)
            self.gold = 0
            print(self.experience, self.gold)

    def has_light(self, location, items):
        """
        does this player have light?
        """
        print("self.room", self.room)
        print("location", location)

    def is_resting(self):
        """
        is player resting
        """
        return self.resting

    def decrease_rest_ticker(self):
        """
        if resting, decrease ticker
        """
        if self.rest_ticker > 0:
            self.rest_ticker -= 1
            self.resting = True
        else:
            self.resting = False

    def decrease_attacks(self):
        """
        subtract one from max attacks
        """
        if self.attacks > 0:
            self.attacks -= 1

        if self.attacks <= 0:
            self.resting = True

    def get_max_attacks(self):
        """
        figure out max attacks
        """
        level_bonus = int(self.level / self.extra_attack_each_level)
        base_attack = 1 + level_bonus

        max_base_attacks = self.max_base_attacks
        if base_attack > max_base_attacks:
            base_attack = max_base_attacks

        return base_attack + self.get_attack_number_bonus()

    def reset_attacks(self):
        """
        reset attack counter back to max attacks
        """
        self.attacks = self.get_max_attacks()

    def decrease_combat_ticker(self):
        """
        if in combat, decrease combat ticker
        """
        if self.combat_ticker > 0:
            self.combat_ticker -= 1

    def set_rest_ticker(self, value):
        """
        set rest ticker
        """
        self.rest_ticker = value

    def set_combat_ticker(self, value):
        """
        set combat ticket
        """
        self.combat_ticker = value

    @staticmethod
    def get_exp_per_point_of_damage(player_level, mob_level):
        """
        Fuck if I know how exp is calculated.  It would be easier to just generate a random number!
        This is my best guess, which involves the players level and mobs level.
        """
        mob_variance = round(random.uniform(.8, 1.2), 2)
        level_difference = mob_level - player_level
        exp_gain_variance = 1.25

        if level_difference == -1:
            exp_base = 2.0
        elif level_difference == 0:
            exp_base = 3.5
        elif level_difference >= 2:
            exp_base = 9.5
        elif level_difference >= 1:
            exp_base = 6.5
        else:
            exp_base = 2.0

        return exp_base * mob_variance * exp_gain_variance * player_level

    def give_exp(self, target, vitality_before):
        """
        do it
        """
        # don't give exp for negative hp
        if target.vit < 0:
            target.vit = 0

        # determine damage delta
        total_damage = vitality_before - target.vit

        # don't allow negative damage
        if total_damage < 0:
            total_damage = 0

        # multiply damage done by unit of experience
        exp_gain = int(total_damage * self.get_exp_per_point_of_damage(self.level, target.level))

        # always give at least one xp
        if exp_gain <= 0:
            exp_gain = 1

        self.experience += exp_gain

    def increase_vitality(self):
        """
        increase vitality
        """
        species = self._species[self.species]
        p_class = self._classes[self.p_class]

        vitality = (species['vit']
                    + p_class['vit']
                    + randint(self._stat_ranges['min_vit'], self._stat_ranges['max_vit'])
                    + self._hp_bonus[self.con]
                    + self.vit_max
                    )

        self.vit = self.vit_max = vitality

    def handle_pleased_by_gods(self):
        """
        increase a random stat by one
        """
        roll = random.randint(0, 5)
        if roll == 0:
            self.increase_int()
        elif roll == 1:
            self.increase_wis()
        elif roll == 2:
            self.increase_str()
        elif roll == 3:
            self.increase_con()
        elif roll == 4:
            self.increase_dex()
        elif roll == 5:
            self.increase_cha()

    def increase_stat(self):
        """
        increase stat
        """
        roll = randint(1, 100)
        if roll <= self._stat_increase_chance:
            self.handle_pleased_by_gods()
