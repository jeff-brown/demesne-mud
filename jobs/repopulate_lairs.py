""" rest job """
import time
import random

from enums.status import Status
from lib.mob import Mob


class RepopulateLairs:
    """ sus class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for z, level in enumerate(self._game.grid):
            for x, row in enumerate(level):
                for y, cnum in enumerate(row):
                    if self._game.grid[z][x][y].lair:
                        for index, mob in enumerate(self._game.grid[z][x][y].mob_types):
                            if not self._game.grid[z][x][y].mobs:
                                if random.randint(1, 100) > 10:
                                    continue
                                self._game.mobs[self._game.next_mob] = Mob(mob, self._game)
                                self._game.mobs[self._game.next_mob].room = [z, x, y]
                                self._game.mobs[self._game.next_mob].mid = self._game.next_mob
                                self._game.grid[z][x][y].mobs.append(self._game.next_mob)
                                self._game.next_mob += 1
                        print(f"({z}, {x}, {y})", self._game.grid[z][x][y].mobs)

        print([y.name for x, y in self._game.mobs.items()])
