""" sustenance job """
import time


class Sustenance:
    """ sus class """

    def __init__(self, game):

        self._game = game

    def get_sustenace(self):
        """ do sustenance """
        for pid, player in self._game._players.items():
            print(int(time.time() - player.hunger_ticker))