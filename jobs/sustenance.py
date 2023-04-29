""" sustenance job """
import time

from enums.status import Status


class Sustenance:
    """ sus class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for pid, player in self._game.players.items():
            if not player.is_playing:
                return

            print("delta", int(time.time() - player.hunger_ticker))
            if int(time.time() - player.hunger_ticker) > player.max_hunger:
                player.status = Status.Hungry
                print("toggle to hunger")

            if int(time.time() - player.thirst_ticker) > player.max_thirst:
                player.status = Status.Thirsty
                print("toggle to thirst")

