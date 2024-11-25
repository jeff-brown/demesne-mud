""" regeneration job """
import time

from enums.status import Status
from lib import data


class Regenerate:
    """ reg class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """
        execute regeneration job
        """

        for pid, player in self._game.players.items():
            if not player:
                return

            if not player.is_playing:
                return

            if player.status is Status.Thirsty:
                if player.take_damage(1):
                    self._game.handle_messages(pid, data.messages['YOUDED3'])
                    self._game.handle_messages(
                        pid,
                        message_to_room=data.messages['OTHDED'].format(player.name))
                    player.handle_death(self._game.items)
            elif player.status is Status.Hungry:
                if player.take_damage(1):
                    self._game.handle_messages(pid, data.messages['YOUDED2'])
                    self._game.handle_messages(
                        pid,
                        message_to_room=data.messages['OTHDED'].format(player.name))
                    player.handle_death(self._game.items)
            else:
                print(player.status)
