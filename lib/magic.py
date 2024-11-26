""" magic class """
from lib import data
from lib.info import Info
from lib.spell import Spell
from enums.player_class import PlayerClass
from enums.spell_type import SpellType
from enums.spell_result import SpellResult as SpellResultEnum
from enums.entity_type import EntityType
from enums.target_type import TargetType

import random


class SpellResult:

    player_effect_time = 40

    def __init__(self):
        self.effect_time = SpellResult.player_effect_time * self.generate_number_variance()
        self.number_effect = 0
        self.spell_result = SpellResultEnum.Success

    @staticmethod
    def generate_number_variance():
        """
        generate a random number between .8 and 1.2
        """

        return round(random.uniform(.8, 1.2), 2)


class Magic:
    """
    This class contains everything to do with casting spells
    """

    def __init__(self, game):
        """
        init the magic class
        """
        self._room = None
        print(f"init {__name__}")
        self._game = game
        self._info = Info(game)
        self._pid = None
        self._entity = None
        self._target = None
        self._spell = None
        self._result = SpellResult()

    def _is_spell_success(self):
        """
        spells have a chance to fail
        """
        base_hit = self._entity.get_spell_hit_difficulty()
        spell_difficulty = self._entity.level - self._spell.get_level()
        to_hit = base_hit - spell_difficulty

        if to_hit < 1:
            to_hit = 2

        if random.randint(1, 20) < to_hit:
            return False

        return True

    def _find_target_including_self(self, maybe_target):
        """
        find target
        """
        target = None
        z, x, y = self._game.players[self._pid].room
        room = self._game.grid[z][x][y]
        pids_here = self._info.get_pids_here(
            self._pid, self._game.players[self._pid].room, self._game.players)

        for pid in pids_here:
            if maybe_target.lower() in self._game.players[pid].name:
                return self._game.players[pid]

        for mob in room.mobs:
            if maybe_target.lower() in self._game.mobs[mob].name:
                return self._game.mobs[mob]

        return target

    def _calculate_offensive_spell_result(self):
        """
        spell around, see what happens
        """

        level_difference = self._entity.level - self._target.level
        combat_skill_mod = (self._target.combat_skill - 70) / 10
        spell_defense = 1 - level_difference + combat_skill_mod

        if spell_defense < 1:
            spell_defense = 1

        if random.randint(1, 20) <= spell_defense:
            self._result.spell_result = SpellResultEnum.Negated
            return

        self._result.spell_result = SpellResultEnum.Success
        damage = random.randint(self._spell.min_spell_effect, self._spell.max_spell_effect)

        if self._spell.based_on_level:
            damage *= self._entity.level

        damage += damage * (self._entity.get_offensive_spell_potency() / 100)
        self._result.number_effect = damage

    def _handle_single_target_spell_attack(self):
        """

        """
        print("handle single target spell attack")

        self._calculate_offensive_spell_result()

        if self._result.spell_result == SpellResultEnum.Negated:
            self._handle_magic_negated()

        self._handle_attack_spell_success()
        self._do_spell_effects()
        # self._handle_victim_death()

    def _do_spell_effects(self):
        """
        do the spell effects
        """
        if not self._apply_damage():
            # TBD: deal with groups
            # TBD: if mob is in group, remove it
            self._apply_poison()
            self._apply_mana_drain()
            self._apply_morale()
            self._apply_wind()

        self._apply_life_steal()
        self._handle_specific_spell_functions()

    def _apply_poison(self):
        """
        apply poison
        """

    def _apply_mana_drain(self):
        """
        apply mana drain
        """

    def _apply_morale(self):
        """
        apply morale effects
        """

    def _apply_wind(self):
        """
        knock back effects
        """

    def _apply_damage(self):
        """
        apply the physical damage portion of a spell
        """
        if self._spell.type is SpellType.Attack:
            vit_before = self._target.vit
            self._target.take_damage(self._result)
            total_damage = vit_before - self._target.vit
            if total_damage < 0:
                total_damage = 0

            exp_gain = (
                int(total_damage * self._target.get_exp_per_point_of_damage(self._target.level)))

            if exp_gain < 0:
                exp_gain = 1

            self._entity.experience += exp_gain

        if self._target.vit < 1:
            return True

        return False

    def _handle_attack_spell_success(self):
        """
        docs
        """
        print("entity type", self._target.entity_type)
        if self._target.entity_type is EntityType.Mob:
            self._game.handle_messages(self._pid, data.messages['SPMDAM'].format(
                self._target.name, self._result.number_effect))
            self._game.handle_messages(self._pid, message_to_room=data.messages['USMOT1'].format(
                self._entity.name, self._spell.desc, self._target.name
            ))
        elif self._target.entity_type is EntityType.Player:
            self._game.handle_messages(self._pid, data.messages['SPLDAM'].format(
                self._target.name, self._result.number_effect
            ))
            self._game.handle_messages(self._pid, message_to_room=data.messages['USEOT1'].format(
                self._entity.name, self._spell.desc, self._target.name
            ))
            self._game.handle_messages(self._pid, message_to_target=data.messages['USEYU1'].format(
                self._entity.name, self._spell.desc, self._result.number_effect
            ))

        self._entity.man -= self._spell.mana
        self._info.handle_mental_rest_delay(self._entity, self._spell)

    def _handle_magic_negated(self):
        """
        TBD: all of these functions need to be made generic to handle mobs or players
        """

        print("entity_type", self._target.entity_type)
        if self._target.entity_type is EntityType.Player:
            self._game.handle_messages(self._pid, data.messages['SPLNEF'].format(self._target.name))
            self._game.handle_messages(self._pid, message_to_room=data.messages['NEFOTH'].format(
                self._entity.name, self._spell.name, self._target.name, self._target.name
            ))
            self._game.handle_messages(self._pid, message_to_target=data.messages['NEFYOU'].format(
                self._entity.name, self._spell.name)
            )
        else:
            self._game.handle_messages(self._pid, data.messages['SPMNEF'].format(self._target.name))
            self._game.handle_messages(self._pid, message_to_room=data.messages['SNMOTH'].format(
                self._entity.name, self._spell.name, self._target.name, self._target.name
            ))

        self._entity.man -= self._spell.mana
        self._info.handle_mental_rest_delay(self._entity, self._spell)

    def _find_single_target(self, maybe_target):
        """
        find single target
        """
        print("find single target")
        if not maybe_target:
            self._game.handle_messages(self._pid, data.messages['SNDTRG'])
            return

        self._target = self._find_target_including_self(maybe_target)
        print(self._target.name)

        if not self._target:
            self._game.handle_messages(self._pid, data.messages['ARNNHR'].format(maybe_target))
            return

        self._handle_single_target()

    def _handle_single_target(self):
        """
        handle single target
        """
        print("handle single target")
        if self._entity is self._target:
            self._handle_unsuccessful_spell()
            return

        if self._info.room_is_safe(self._entity):
            self._game.handle_messages(self._pid, data.messages['NOTHER'])
            return

        if not self._is_spell_success():
            self._handle_unsuccessful_spell()
            return

        self._handle_single_target_spell_attack()

        return

    def _handle_unsuccessful_spell(self):
        """
           protected void handleUnsuccessfulSpell() {
      _entity.print(TaMessageManager.SPLFLD.getMessage());

      String messageToRoom = MessageFormat.format(TaMessageManager.SFDYOU.getMessage(), getName());
      _room.print(_entity, messageToRoom, false);

      _entity.getMana().subtractCurMana(_spell.getMana());
      WorldManager.getGameMechanics().handleMentalRestDelay(_entity, _spell);
   }
        """

        self._game.handle_messages(self._pid, data.messages['SPLFLD'])
        self._game.handle_messages(self._pid, message_to_room=data.messages['SFDYOU'].format(self._entity.name))
        self._entity.man -= self._spell.mana
        self._entity.handle_mental_rest_delay()
    """
      
      
      handleSingleTargetSpellAttack(target);
   }
    """

    @staticmethod
    def _is_spell(maybe_spell):
        """
        check spell db to see if this is actually a spell
        """
        for spell in data.spells.values():
            if maybe_spell == spell['name']:
                return True
        return False

    @staticmethod
    def _get_spell_by_name(maybe_spell):
        """
        return spell index
        """
        for index, spell in data.spells.items():
            if maybe_spell == spell['name']:
                return index
        return -1

    def cast(self, entity, maybe_spell, maybe_target):
        """
        this is the big one
        """
        if entity.entity_type is EntityType.Player:
            self._pid = self._info.get_pid_by_name(self._game.players, entity.name)
        else:
            self._pid = self._info.get_pid_by_name(self._game.players, maybe_target.name)

        self._entity = entity

        if not self._is_spell(maybe_spell):
            self._game.handle_messages(self._pid, data.messages['NOSPEL'])
            return

        try:
            self._spell = Spell(self._get_spell_by_name(maybe_spell))
        except KeyError:
            self._game.handle_messages(self._pid, data.messages['NOSPEL'])
            return

        if self._entity.is_mentally_exhausted():
            self._game.handle_messages(self._pid, data.messages["SPLEXH"])
            return

        if not self._entity.has_spell(self._spell):
            self._game.handle_messages(self._pid, data.messages['NOSPEL'])
            return

        if self._entity.man < self._spell.mana:
            self._game.handle_messages(self._pid, data.messages['LOWSPL'])
            return

        self._room = self._entity.room
        self._spell.get_spell_target()

        print("target type", self._spell.target, TargetType.SingleTarget)
        if self._spell.target == TargetType.SingleTarget:
            print("this is the correct target type")
            self._find_single_target(maybe_target)

        """
          // Determine spell type -- mob area, player area, single target, etc
          if (spell.getSpellTarget().equals(SpellTarget.SPECIFIED)) {
             findSingleTarget(targetStr);
             return; entity, maybe_spell, 
          }
    
          if (spell.getSpellTarget().equals(SpellTarget.ROOM_MOB)
              || spell.getSpellTarget().equals(SpellTarget.ROOM_MOB2)) {
             ArrayList<Mob> roomTargets = _room.getMobs();
    
             // create a temporary list to modify.
             ArrayList<Entity> targets = new ArrayList<Entity>();
             for (Entity target : roomTargets) {
                targets.add(target);
             }
             findAreaTargets(targets, targetStr, false);
             return;
          }
    
          if (spell.getSpellTarget().equals(SpellTarget.ROOM_entity)
              || spell.getSpellTarget().equals(SpellTarget.ROOM_entity2)) {
             ArrayList<Player> roomTargets = _room.getPlayers();
    
             // create a temporary list to modify.
             ArrayList<Entity> targets = new ArrayList<Entity>();
             for (Entity target : roomTargets) {
                if (!target.equals(_entity)) {
                   targets.add(target);
                }
             }
             findAreaTargets(targets, targetStr, true);
             return;
          }
    
          if (spell.getSpellTarget().equals(SpellTarget.SUMMON)) {
             handleNoTargets(targetStr);
             return;
          }
        """











