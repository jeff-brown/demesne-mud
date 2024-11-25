""" gong class """
import random

from lib import data
from lib.info import Info
from lib.mob import Mob


class Gong:
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

    def ring(self, uid):
        """
        ring the bells
        """
        print("ring bells")
        player = self._game.players[uid]
        room = self._game._area.get_cur_room(player.room)
        z, x, y = player.room

        print(dir(room))

        if player.resting:
            self._game.handle_messages(uid, self._messages['CNTMOV'])
            print("can't ring, resting")
            return

        if not self._info.room_is_arena(player):
            self._game.handle_messages(uid, self._messages['CNTHRE'])
            print("room is not arena")
            return

        arena_mobs = []
        for mob_type in room.mob_types:
            arena_mobs = self._info.get_mob_by_terrain(mob_type)

        if len(room.mobs) >= 8:
            self._game.handle_messages(uid, self._messages['NTHHPS'])
            print("too many mobs")
            return

        self._game.handle_messages(uid, self._messages['RNGGNG'].format("You"))
        self._game.handle_messages(uid, message_to_room=self._messages['RNGGNG'].format(player.name))
        self._game.mobs[self._game.next_mob] = Mob(random.choice(arena_mobs), self._game)
        self._game.mobs[self._game.next_mob].room = player.room
        self._game.grid[z][x][y].mobs.append(self._game.next_mob)
        self._game.handle_messages(uid, self._messages['MONENT'].format(self._game.mobs[self._game.next_mob].name))
        self._game.handle_messages(uid, message_to_room=self._messages['MONENT'].format(self._game.mobs[self._game.next_mob].name))
        self._game.next_mob += 1
        player.set_rest_ticker(6)
        player.set_combat_ticker(6)

        print(room.mobs)




