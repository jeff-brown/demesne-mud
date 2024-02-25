""" combat class """
import random

from enums.melee_result import MeleeResult
from lib import data
from lib.info import Info


class Combat:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, game):

        print(f"init {__name__}")
        self._melee_damage = 0
        self._melee_result = MeleeResult.Miss
        self._melee_player_hit_difficulty = 10  # TODO: add to config file
        self._messages = data.messages
        self._game = game
        self._info = Info(game)

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

    def _determine_melee_hit(self, attacker, target):
        base = self._melee_player_hit_difficulty
        mob_level = target.level
        player_level = attacker.level
        diff = (mob_level - player_level) * 2
        print(diff)
        int_bonus = attacker.get_melee_hit_bonus()
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

    def _determine_melee_damage(self, attacker, target, items):
        self._melee_damage = 0
        attacker_weapon = items[attacker.weapon]
        target_armor = items[target.armor]

        if self._melee_result == MeleeResult.Hit:
            base_damage = random.randint(attacker_weapon.min_damage, attacker_weapon.max_damage)
            print(base_damage, attacker.get_physical_damage_bonus(), target_armor.ac)
            final_damage = base_damage + attacker.get_physical_damage_bonus() - target_armor.ac

            if final_damage <= 0:
                final_damage = 0
                self._melee_result = MeleeResult.Glance
            elif self._is_critical_hit(attacker, target):
                self._melee_result = MeleeResult.Crit
                final_damage *= 2

            self._melee_damage = final_damage

    def _calculate_melee_result(self, attacker, target, items):
        """
        compile melee result message
        """
        message_to_player = None
        message_to_room = None
        message_to_victim = None
        weapon = items[attacker.weapon]

        if self._melee_result == MeleeResult.Miss:
            message_to_player = self._messages['ATTFUM']
            message_to_room = self._messages['FMMOTH'].format(attacker.name, target.name)
        elif self._melee_result == MeleeResult.Hit:
            message_to_player = self._messages['ATTHTM'].format(target.name, self._melee_damage)
            message_to_room = self._messages['HTMOTH'].format(attacker.name, target.name, weapon.long)
        elif self._melee_result == MeleeResult.Crit:
            message_to_player = self._messages['ATTCRM'].format(target.name, self._melee_damage)
            message_to_room = self._messages['HTMOTH'].format(attacker.name, target.name, weapon.long)
        elif self._melee_result == MeleeResult.Dodge:
            message_to_player = self._messages['MATDOG'].format(target.name)
            message_to_room = self._messages['DGMOTH'].format(target.name, attacker.name, weapon.type)
        elif self._melee_result == MeleeResult.Glance:
            message_to_player = self._messages['ATTGNM'].format(target.name)
            message_to_room = self._messages['GNMOTH'].format(attacker.name, weapon.long, target.long)
        else:
            print(f"Got unhandled melee result of {self._melee_result}.")

        return message_to_player, message_to_room, message_to_victim

    def _calculate_mob_melee_result(self, attacker, target, items):
        """
        compile melee result message
        """
        message_to_player = None
        message_to_room = None
        weapon = items[attacker.weapon]

        if self._melee_result == MeleeResult.Miss:
            message_to_player = self._messages['MFMYOU'].format(attacker.name)
            message_to_room = self._messages['MFMOTH'].format(attacker.name, target.name)
        elif self._melee_result == MeleeResult.Hit:
            message_to_player = self._messages['MATYOU'].format(attacker.name, weapon.long, self._melee_damage)
            message_to_room = self._messages['MATOTH'].format(attacker.name, target.name, weapon.long)
        elif self._melee_result == MeleeResult.Crit:
            message_to_player = self._messages['MDGCRM'].format(attacker.name, weapon.long, self._melee_damage)
            message_to_room = self._messages['MATOTH'].format(attacker.name, target.name, weapon.long)
        elif self._melee_result == MeleeResult.Dodge:
            message_to_player = self._messages['MDGYOU'].format(attacker.name)
            message_to_room = self._messages['MDGOTH'].format(target.name, attacker.name, weapon.type)
        elif self._melee_result == MeleeResult.Glance:
            message_to_player = self._messages['MGNYOU'].format(target.name, weapon.long)
            message_to_room = self._messages['MGNOTH'].format(attacker.name, target.name, weapon.long, target.name)
        else:
            print(f"Got unhandled melee result of {self._melee_result}.")
        uid = self._info.get_pid_by_name(self._game.players, target.name)
        self._game.handle_messages(uid, message_to_player=message_to_player)
        self._game.handle_messages(uid, message_to_room=message_to_room)

    def player_melee_attack(self, player, target, items):
        """ check to see if an attack hits and

            // Reset combat ticker only if the room contains mob.
            if (!player.getRoom().getHostileMobs().isEmpty()) {
                player.setCombatTicker(ATTACK_COMBAT_WAIT_TIME);
            }

            int vitalityBefore = target.getVitality().getCurVitality();
            MeleeResult result = calculateMeleeResult(player, target, weapon);
            displayMessage(player, target, result, exitDirectionEnum, weapon);
            target.takeDamage(result.getDamage());

            GameUtil.giveExperience(player, target, vitalityBefore);

            // Adjust number of attacks appropriately
            player.getAttacks().attack();
            if (player.getAttacks().getAttacksLeft() == 0) {
                player.setRestTicker(GameUtil.randomizeRestWaitTime());
            }

        """
        vitality_before = target.vit
        self._determine_melee_hit(player, target)
        self._determine_melee_damage(player, target, items)
        target.take_damage(self._melee_damage)
        player.give_exp(target, vitality_before)
        print(f"{player.name} has {player.attacks}")
        player.decrease_attacks()
        if player.attacks == 0:
            player.set_rest_ticker(12 + (random.randint(0, 2) - 1))
            player.resting = True

        return self._calculate_melee_result(player, target, items)

    def mob_melee_attack(self, mob, target, items):
        """ check to see if an attack hits and

            // Reset combat ticker only if the room contains mob.
            if (!player.getRoom().getHostileMobs().isEmpty()) {
                player.setCombatTicker(ATTACK_COMBAT_WAIT_TIME);
            }

            int vitalityBefore = target.getVitality().getCurVitality();
            MeleeResult result = calculateMeleeResult(player, target, weapon);
            displayMessage(player, target, result, exitDirectionEnum, weapon);
            target.takeDamage(result.getDamage());

            GameUtil.giveExperience(player, target, vitalityBefore);

            // Adjust number of attacks appropriately
            player.getAttacks().attack();
            if (player.getAttacks().getAttacksLeft() == 0) {
                player.setRestTicker(GameUtil.randomizeRestWaitTime());
            }

        """
        for x in range(0, mob.num_attacks):
            self._determine_melee_hit(mob, target)
            self._determine_melee_damage(mob, target, items)
            print(self._melee_result, self._melee_damage)
            self._calculate_mob_melee_result(mob, target, items)
            if target.take_damage(self._melee_damage):
                pid = self._info.get_pid_by_name(self._game.players, target.name)
                message_to_player = self._messages['YOUDED4']
                message_to_room = self._messages['OTHDED'].format(target.name)
                self._game.handle_messages(pid, message_to_player=message_to_player)
                self._game.handle_messages(pid, message_to_room=message_to_room)
                target.handle_death(self._game.items)
        print("mob attacks")
