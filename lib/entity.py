"""
Entity base class - players, mobs and npcs all inherit this
"""
import random
from lib import data


class Entity:
    """
    base class
    """
    MOB_SPELL_HIT_DIFFICULTY = 0
    PLAYER_SPELL_HIT_DIFFICULTY = 5
    OFFENSIVE_SPELL_POTENCY = [
        0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
        55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
        105, 110, 115, 120, 125, 130, 135, 140, 145, 150,
        155, 160, 165, 170, 175, 180, 185, 190, 195, 200
    ]

    def __init__(self):
        """
        initialize an Entity
        """
        self.level = 0
        self.mental_exhaustion_ticker = 0
        self.combat_ticker = 0
        self.rest_ticker = 0
        self.resting = False
        self.spellbook = None

        offensive_spell_potency = [
            0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
            55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
            105, 110, 115, 120, 125, 130, 135, 140, 145, 150,
            155, 160, 165, 170, 175, 180, 185, 190, 195, 200
        ]

    def set_mental_exhaustion_ticker(self, value: int):
        """ set mental exhaustion ticker """
        self.mental_exhaustion_ticker = value

    def is_resting(self):
        """
        is player resting
        """
        return self.resting

    def is_mentally_exhausted(self):
        """
        can the player spellcast?
        """
        print("mentally exhausted", self.mental_exhaustion_ticker)
        if self.mental_exhaustion_ticker > 0:
            return True
        else:
            return False

    def decrease_rest_ticker(self):
        """
        if resting, decrease ticker
        """
        if self.rest_ticker > 0:
            self.rest_ticker -= 1
            self.resting = True
        else:
            self.resting = False

    def decrease_combat_ticker(self):
        """
        if in combat, decrease combat ticker
        """
        if self.combat_ticker > 0:
            self.combat_ticker -= 1

    def decrease_mental_ticker(self):
        """
        decrease mental ticker
        """
        if self.mental_exhaustion_ticker > 0:
            self.mental_exhaustion_ticker -= 1

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

    def handle_mental_rest_delay(self, spell):
        """
        handle mental rest delay
        """
        if spell.get_level() == 1:
            base_wait = 15
        else:
            base_wait = 27 + spell.get_level()

        base_wait -= self.level

        if base_wait < 5:
            base_wait = 5

        variance = (base_wait / 10) * 2
        rand = random.randint(1, int(variance))
        if random.randint(0, 1) == 0:
            rand = -rand

        base_wait += rand

        self.mental_exhaustion_ticker = int(base_wait)

    def has_spell(self, maybe_spell):
        """
        i can haz spell pls
        """
        for spell in self.spellbook:
            if spell.name == maybe_spell.name:
                return True

        return False

    def get_spell_hit_difficulty(self):
        """
        override this in the entity-type inherited class
        """
        pass

    def get_offensive_spell_potency(self):
        return self.OFFENSIVE_SPELL_POTENCY[self.level]
