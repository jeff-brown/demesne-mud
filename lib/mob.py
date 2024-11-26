""" armor class """
import random

from lib import data
from lib.entity import Entity
from lib.info import Info
from lib.combat import Combat
from lib.weapon import Weapon
from lib.armor import Armor
from enums.entity_type import EntityType


class Mob(Entity):
    """
    @DynamicAttrs
    This class contains all the basic informational commands
    """

    def __init__(self, vnum, game):
        """ read in the config files
        """
        super().__init__()
        print(vnum)

        print(f"init {__name__}")

        self._game = game
        self._info = Info(game)
        self._combat = Combat(game)
        self._data = data
        self.entity_type = EntityType.Mob

        for key in data.mobs[vnum]:
            setattr(self, key, data.mobs[vnum][key])

        _mob_variance = round(random.uniform(.8, 1.2), 2)
        num = (self.combat_skill * self.level) / 3
        self.vit = int(num * _mob_variance)
        self.vit_max = int(num * _mob_variance)
        self.resting = False
        self.room = []
        self.mid = -1

        self.regeneration_ticker = 0.0
        self.mental_exhaustion_ticker = 0.0
        self.activity_ticker = 0
        self.combat_ticker = 0
        self.paralysis_ticker = 0.0

        self._game.mob_items[self._game.next_mob_item] = Weapon(random.choice(self.weapon_types))
        self.weapon = self._game.next_mob_item
        self._game.next_mob_item += 1

        self._game.mob_items[self._game.next_mob_item] = Armor(random.choice(self.armor_types))
        self.armor = self._game.next_mob_item
        self._game.next_mob_item += 1

        self._melee_hit_bonus = [
            -1,
            -1, -1, -1, -1,  0,  0,  0,  0,  0, 1,
            1, 1, 1, 1, 2, 2, 2, 2, 2, 3,
            3, 3, 3, 3, 4, 4, 4, 4, 4, 5,
            5, 5, 5, 5, 5, 6, 6, 6, 6, 6,
            7, 7, 7, 7, 7, 8, 8, 8, 8, 8
        ]

        self._physical_damage_bonus = [
            0,
            0, 0, 0, 0, 0, 1, 1, 1, 1, 2,
            2, 2, 2, 2, 3, 3, 3, 3, 3, 3,
            4, 4, 4, 4, 5, 5, 5, 5, 5, 6,
            6, 6, 6, 7, 7, 7, 7, 8, 8, 8,
            8, 9, 9, 9, 9, 10, 10, 10, 10, 11
        ]

    def get_spell_hit_difficulty(self):
        """
        override this in the entity-type inherited class
        """
        hit_difficulty = self.MOB_SPELL_HIT_DIFFICULTY + (100 - self.spell_skill) / 10

        if hit_difficulty < 1:
            hit_difficulty = 1

        if hit_difficulty > 20:
            hit_difficulty = 20

        return hit_difficulty

    def set_mental_exhaustion_ticker(self, value: int):
        """ set mental exhaustion ticker """
        self.mental_exhaustion_ticker = value

    def get_look_description(self):
        """
        is it hurt how much
        MMSG1=\u0020The {0} is sorely wounded.
MMSG2=\u0020The {0} seems to be moderately wounded.
MMSG3=\u0020The {0} appears to be wounded.
MMSG5=\u0020The {0} seems to be in good physical health.
MMSG4=\u0020It looks as if the {0} is lightly wounded.
        """
        _vit_msg = [100, 75, 50, 25, 0]
        weapon = self._game.mob_items[self.weapon]
        msg = self.description
        if weapon.classes > 0:
            msg = f"{msg.format(weapon.long)}"

        vit_perc = int(self.vit / self.vit_max * 100)
        if _vit_msg[4] <= vit_perc < _vit_msg[3]:
            vit_msg = self._data.messages['MMSG1']
        elif _vit_msg[3] <= vit_perc < _vit_msg[2]:
            vit_msg = self._data.messages['MMSG2']
        elif _vit_msg[2] <= vit_perc < _vit_msg[1]:
            vit_msg = self._data.messages['MMSG3']
        elif _vit_msg[1] <= vit_perc < _vit_msg[0]:
            vit_msg = self._data.messages['MMSG4']
        else:
            vit_msg = self._data.messages['MMSG5']

        print(vit_msg)

        return f"{msg} {vit_msg.format(self.name)}"

    def _get_players_by_room(self):
        """
        get list of players in the same room as this mob
        """
        players_here = {}
        for pid, player in self._game.players.items():
            if not player:
                continue
            if player.room == self.room:
                players_here[pid] = player

        return players_here

    def get_melee_hit_bonus(self):
        """ return buy modifier based on current cha """
        return self._melee_hit_bonus[self.level]

    def get_physical_damage_bonus(self):
        return self._physical_damage_bonus[self.level]

    @staticmethod
    def get_class():
        """
        stub method for mob class
        """
        return None

    def decrease_activity_ticker(self):
        """

        """
        if self.activity_ticker > 0:
            self.activity_ticker -= 3

    def is_resting(self):
        """
        is the mob resting?
        """
        if self.activity_ticker > 0:
            return True
        return False

    def reset_activity_ticker(self):
        """
        reset it
        """
        self.activity_ticker = 12 + (random.randint(0, 2) - 1)

    def do_something(self):
        """
        take an action on a timer
        """
        players_here = self._get_players_by_room()
        if players_here:
            target = random.choice(list(players_here.values()))
            self._combat.mob_melee_attack(self, target, self._game.mob_items, self._game.items)

        self.reset_activity_ticker()

    def take_damage(self, damage):
        """
        take damage and determine if dead
        """
        self.vit -= damage
        if self.vit <= 0:
            return True
        return False
