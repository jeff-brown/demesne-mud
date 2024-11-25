""" sustenance job """
import time

from enums.status import Status
from lib import data


class SlowStatus:
    """ slow class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for pid, player in self._game.players.items():
            if not player:
                return

            if not player.is_playing:
                return

            if player.status is Status.Hungry:
                self._game.handle_messages(pid, message_to_player=data.messages['YOUHNG'])
                self._game.handle_messages(pid, message_to_room=data.messages['OTHHNG'].format(player.name))
            elif player.status is Status.Thirsty:
                self._game.handle_messages(pid, message_to_player=data.messages['YOUTHR'])
                self._game.handle_messages(pid, message_to_room=data.messages['OTHTHR'].format(player.name))
            elif player.status is Status.Poisoned:
                self._game.handle_messages(pid, message_to_player=data.messages['POISON'])
                self._game.handle_messages(pid, message_to_room=data.messages['OTHPSN'].format(player.name))



