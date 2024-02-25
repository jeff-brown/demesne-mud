""" rest job """
import time

from enums.status import Status


class Rest:
    """ sus class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for pid, player in self._game.players.items():
            if not player.is_playing:
                return

            print(f"player {player.name} is resting {player.resting} and has {player.attacks} attacks.")

            player.decrease_rest_ticker()
            player.decrease_combat_ticker()
            if player.attacks == 0 and not player.resting:
                player.reset_attacks()
