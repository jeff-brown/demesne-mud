""" bank class """
from lib import data
from lib.info import Info


class Bank:
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

        self._max_vault_transfer = 30000

    def _is_bank(self, uid, player):
        """
        not a bank
        """
        if not self._info.room_is_bank(player):
            self._game.handle_messages(uid, self._messages['CNTHRE'])
            print("room is not bank")
            return False
        return True

    def balance(self, uid):
        """
        ring the vaults
        """
        print(__name__)
        player = self._game.players[uid]
        if not self._is_bank(uid, player):
            return
        self._game.handle_messages(uid, self._messages['BNKBAL'].format(player.vault_balance))

    def deposit(self, uid, amount):
        """
        deposit gold
        """
        print(__name__)
        player = self._game.players[uid]
        if not self._is_bank(uid, player):
            return

        if not amount.isnumeric():
            print("not a number")
            self._game.handle_messages(uid, self._messages['BNKTMC'])
            return

        amount = int(amount)

        if amount < 1:
            print("too little")
            self._game.handle_messages(uid, self._messages['BNKTMC'])
            return

        if amount > player.gold:
            print("too poor")
            self._game.handle_messages(uid, self._messages['BNKNHA'])
            return

        player.gold -= amount
        player.vault_balance += amount

        self._game.handle_messages(uid, self._messages['BNKDEP'].format(amount))

    def withdraw(self, uid, amount):
        """
        withdraw gold
        """
        print(__name__)
        player = self._game.players[uid]
        if not self._is_bank(uid, player):
            return

        if not amount.isnumeric():
            print("not a number")
            self._game.handle_messages(uid, self._messages['BNKTMC'])
            return

        amount = int(amount)

        if amount < 1:
            print("too little")
            self._game.handle_messages(uid, self._messages['BNKTMC'])
            return

        if amount > player.vault_balance:
            print("save better")
            self._game.handle_messages(uid, self._messages['BNKNAC'])
            return

        if self._info.get_enc(player, self._game.items) + amount * 0.2 > player.max_enc:
            print("too heavy")
            self._game.handle_messages(uid, self._messages['BNKNCA'])
            return

        player.vault_balance -= amount
        player.gold += amount

        self._game.handle_messages(uid, self._messages['BNKWIT'].format(amount))





