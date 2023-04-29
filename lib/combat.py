""" combat class """
import random

from enums.melee_result import MeleeResult


class Combat:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):

        print(f"init {__name__}")
        self._melee_damage = 0
        self._melee_result = MeleeResult.Miss
        self._melee_player_hit_difficulty = 10  # TODO: add to config file

    @staticmethod
    def _is_critical_hit(player, target):
        is_rogue = False
        if player.get_class() == 'rogue':
            is_rogue = True

        mob_level = target.level
        player_level = player.level
        diff = player_level - mob_level * 2

        roll = random.randint(1, 20)

        # critical failure
        if roll == 1:
            return False

        # critical success
        if roll == 20:
            return True

        if is_rogue:
            crit_chance = diff + player.get_rogue_skill_bonus()
            if roll <= crit_chance:
                return True

        return False

    def _determine_player_melee_hit(self, player, target):
        base = self._melee_player_hit_difficulty
        mob_level = target.level
        player_level = player.level
        diff = (mob_level - player_level) * 2
        print(diff)
        int_bonus = player.get_melee_hit_bonus()
        print(int_bonus)
        combat_skill_mod = (target.combat_skill - 70) / 10
        print(combat_skill_mod)

        to_hit = base + diff + combat_skill_mod - int_bonus
        roll = random.randint(0, 100)
        print("dodge: ", roll, to_hit)
        if roll < to_hit:
            print("roll {} less than {} so you dodge.".format(roll, to_hit))
            self._melee_result = MeleeResult.Dodge
            return

        roll = random.randint(1, 20)
        print("miss: ", roll, to_hit)

        # critical hit
        if roll == 20:
            self._melee_result = MeleeResult.Hit
            return

        # critical miss
        if roll == 1:
            self._melee_result = MeleeResult.Miss
            return

        if roll >= to_hit:
            print("roll {} great than or equal to {} so you hit.".format(roll, to_hit))
            self._melee_result = MeleeResult.Hit
            return
        else:
            print("roll {} less than {} so you miss.".format(roll, to_hit))
            self._melee_result = MeleeResult.Miss
            return

    def _determine_player_melee_damage(self, player, target, items):
        self._melee_damage = 0
        player_weapon = items[player.weapon]

        if self._melee_result == MeleeResult.Hit:
            base_damage = random.randint(player_weapon.min_damage, player_weapon.max_damage)
            final_damage = base_damage + player.get_physical_damage_bonus() - target.armor

            if final_damage <= 0:
                final_damage = 0
                self._melee_result = MeleeResult.Glance
            elif self._is_critical_hit(player, target):
                self._melee_result = MeleeResult.Crit
                final_damage *= 2

            self._melee_damage = final_damage

    def player_melee_attack(self, player, target, items):
        """ check to see if an attack hits and """
        self._determine_player_melee_hit(player, target)
        self._determine_player_melee_damage(player, target, items)
        print(self._melee_result)
        print(self._melee_damage)