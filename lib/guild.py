""" training class """
import random

from lib import data
from lib.info import Info
from lib.spell import Spell


class Guild:
    """
    @DynamicAttrs
    This class contains all the basic training commands
    """

    def __init__(self, game):
        """ read in the config files """
        print(f"init {__name__}")
        self._game = game
        self._info = Info(game)
        self._messages = data.messages
        self.training_cost_modifier = 5
        self.stat_increase_chance = 25
        self._spell_casters = [8, 2, 3, 6]

    @staticmethod
    def _get_spell_vnum_by_name(name):
        """
        lookup spell vnum by name
        """
        for vnum, spell in data.spells.items():
            if spell["name"] == name:
                return vnum

        return None

    def handle_training(self, player):
        """
        ring the bells
        """
        print(__name__)
        pid = self._info.get_pid_by_name(self._game.players, player.name)
        training_cost = int((player.level + 1) * self.training_cost_modifier)
        if training_cost > player.gold:
            self._game.handle_messages(pid, self._messages['CNTAFD'].format('to buy training.'))
            print("you broke")
            return

        exp_req = self._info.get_exp_gain(player)
        if player.experience < exp_req:
            self._game.handle_messages(pid, self._messages['NOTRDY'])
            print("you stupid")
            return

        player.gold -= training_cost
        player.level += 1
        player.increase_vitality()
        player.increase_stat()
        # player.increase_mana()

        self._game.handle_messages(pid, self._messages['GNDLEV'])
        self._game.handle_messages(pid, message_to_room=self._messages['GOTTRN'].format(player.name))

        return

    def handle_buy(self, player, spell_name):
        """
        buy spells
        """
        vnum = self._get_spell_vnum_by_name(spell_name)
        pid = self._info.get_pid_by_name(self._game.players, player.name)

        if player.p_class not in self._spell_casters:
            self._game.handle_messages(pid, self._messages['WARNSP'])
            return

        if vnum is None:
            self._game.handle_messages(pid, self._messages['NOSSPL'])
            return

        spell = Spell(vnum)
        if spell.p_class != player.p_class:
            self._game.handle_messages(pid, self._messages['OUTRLM'])
            return


