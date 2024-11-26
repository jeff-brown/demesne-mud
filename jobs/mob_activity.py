""" rest job """
import time

from enums.status import Status


class MobActivity:
    """ sus class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        for mid, mob in self._game.mobs.items():
            mob.decrease_activity_ticker()
            mob.decrease_mental_ticker()
            print(f"{mob.name} is resting {mob.is_resting()} for {mob.activity_ticker}.")
            if not mob.is_resting():
                mob.do_something()
