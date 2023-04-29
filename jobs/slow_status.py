""" sustenance job """
import time

from enums.status import Status


class SlowStatus:
    """ slow class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for pid, player in self._game.players.items():
            if not player.is_playing:
                return

            if player.status is Status.Hungry:
                self._game.handle_messages(pid, message_to_player="You're hungry.")
                self._game.handle_messages(pid, message_to_room=f"You hear {player.name}'s stomach growling.")
            elif player.status is Status.Thirsty:
                self._game.handle_messages(pid, message_to_player="You're thirsty.")
                self._game.handle_messages(pid, message_to_room=f"{player.name} is looking rather parched.")
            elif player.status is Status.Poisoned:
                self._game.handle_messages(pid, message_to_player="You're poisoned.")
                self._game.handle_messages(pid, message_to_room=f"{player.name} is looking a little under the weather.")



