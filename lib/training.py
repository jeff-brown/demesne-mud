""" training class """
import random

from lib import data
from lib.info import Info


class Training:
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
