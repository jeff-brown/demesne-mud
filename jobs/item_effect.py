""" item effect job """
import time

from lib.equipment import Equipment
from lib import data

from enums.status import Status


class ItemEffect:
    """ slow class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """ do sustenance """
        expired_items = []

        for pid, player in self._game.players.items():
            if not player:
                return

            if not player.is_playing:
                return

            if player.str_boo > 0:
                if int(time.time() - player.str_ticker) > player.stat_ticker_max:
                    player.str_boo = 0
                    self._game.handle_messages(pid, data.messages['STA1'])

            if player.dex_boo > 0:
                if int(time.time() - player.dex_ticker) > player.stat_ticker_max:
                    player.dex_boo = 0
                    self._game.handle_messages(pid, data.messages['STA1'])

            for item_num in player.inventory:
                if not isinstance(self._game.items[item_num], Equipment):
                    continue

                if self._game.items[item_num].is_activated:
                    if int(time.time() - self._game.items[item_num].effect_ticker) \
                            > self._game.items[item_num].effect_ticker_max:
                        expired_items.append(item_num)

                for expired_item in expired_items:
                    if self._game.items[expired_item].equip_sub_type == 'light':
                        self._game.handle_messages(pid, data.messages['BRNOUT'].format(self._game.items[expired_item].type))
                        self._game.handle_messages(
                            pid,
                            message_to_room=(
                                data.messages['OTHOUT'].format(player.name, self._game.items[expired_item].type)
                            )
                        )

                    self._game.items.pop(expired_item)
                    player.inventory.remove(expired_item)






