""" bank class """
import random

from lib import data
from lib.info import Info


class Temple:
    """
    @DynamicAttrs
    This class contains all the basic informational commands
    """

    def __init__(self, game):
        """ read in the config files """
        print(f"init {__name__}")
        self._game = game
        self._info = Info(game)
        self._messages = data.messages

    @staticmethod
    def _pleased_gods(amount):
        """
        check if you've pleased the gods
        """
        if amount < 10:
            return False

        chance = random.randint(1, 600)
        if chance < 10:
            return True

        return False

    def _is_temple(self, uid, player):
        """
        not a temple
        """
        if not self._info.room_is_temple(player):
            self._game.handle_messages(uid, self._messages['CNTHRE'])
            print("room is not temple")
            return False
        return True

    def donate(self, uid, amount):
        """
        ring the vaults
        """
        print(__name__)
        player = self._game.players[uid]
        if not self._is_temple(uid, player):
            return

        if not amount.isnumeric():
            print("not a number")
            self._game.handle_messages(uid, self._messages['DPLGDS'])
            return

        amount = int(amount)

        if amount < 1:
            print("too little")
            self._game.handle_messages(uid, self._messages['DPLGDS'])
            return

        if amount > player.gold:
            print("too poor")
            self._game.handle_messages(uid, self._messages['DNTHVG'])
            return

        amount = int(amount)
        player.gold -= amount
        self._game.handle_messages(uid, self._messages['YOUDON'])
        self._game.handle_messages(uid, message_to_room=self._messages['JSTDON'].format(player.name))

        if self._pleased_gods(amount):
            self._game.handle_messages(uid, self._messages['PLSGDS'])
            player.handle_pleased_by_gods()
