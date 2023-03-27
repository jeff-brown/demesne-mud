#!/usr/bin/python3

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

author: Mark Frimston - mfrimston@gmail.com
modified by: Jeff Brown - jeffbr@gmail.com
"""

from random import randrange
import signal
import sys
from threading import Condition
import time

from apscheduler.schedulers.background import BackgroundScheduler

# import library objects
from lib.area import Area
from lib.data import Data
from lib.info import Info
from lib.player import Player
from lib.armor import Armor
from lib.weapon import Weapon

# like it's a job
from jobs.sustenance import Sustenance

# import the MUD server class
from server.mud import Mud


class Game:
    """
    This class contains all the functions to allow the game to operate
    """

    def __init__(self, mud):
        # start the server
        self._area = Area()
        self._grid = self._area.grid
        self._mud = mud
        self._players = {}
        self._monsters = {}
        self._items = {}
        self._tick = 6  # 6 seconds
        self._info = Info()
        self._data = Data()
        self._species = self._data.species
        self._classes = self._data.classes
        self._weapons = self._data.weapons
        self._armor = self._data.armor
        self._equipment = self._data.equipment

        # counter for assigning each client a new id
        self._nextid = 0
        self._next_item = 0
        self._next_monster = 0

    def _handle_messages(
            self,
            uid,
            message_to_player=None,
            tid=None,
            message_to_target=None,
            message_to_room=None,
            global_message=None
    ):
        """
        properly format messages and send them to the correct folks
        """
        pids_here = self._info.get_pids_here(
            uid, self._players[uid].room, self._players)

        if message_to_player:
            print("message_to_player", uid, message_to_player)
            self._mud.send_message(uid, message_to_player)
            return

        if message_to_target and tid is not None:
            print("message_to_target", tid, message_to_target)
            self._mud.send_message(tid, message_to_target)
            return

        if message_to_room and tid is None:
            print("message_to_room", tid, message_to_room)
            for pid in pids_here:
                self._mud.send_message(pid, message_to_room)
            return

        if message_to_room and tid is not None:
            print("message_to_room_except_bil", tid, message_to_room)
            for pid in pids_here:
                if pid != tid:
                    self._mud.send_message(pid, message_to_room)
            return

        if global_message:
            print("global_message", uid, global_message)
            for pid, _ in self._players.items():
                if pid != uid:
                    self._mud.send_message(pid, global_message)
            return

    def _process_look_command(self, uid, command=None, params=None, location=None):
        """
        write out the room and any players or items in it
        """
        npc_here = None
        self._handle_messages(uid)

        if not location:
            location = self._players[uid].room

        exits = self._area.get_cur_exits(location)
        room = self._area.get_cur_room(location)

        print("cur_room", room.short)
        print("player", self._players[uid].name)

        players_here = self._info.get_players_here(uid, location, self._players)
        if room.npcs and params:
            for npc in room.npcs:
                if params.lower() in npc.type:
                    npc_here = npc
                    break
        print(npc_here)

        if command and not params:
            self._handle_messages(uid, room.long)
            self._handle_messages(uid, message_to_room="{} is looking at around.".format(
                self._players[uid].name))
            return

        if params:
            if self._area.is_exit(params):
                if params[0] in exits:
                    print(self._area.get_next_room(location, params[0]))
                    self._process_look_command(uid, location=self._area.get_next_room(location, params[0]))
                else:
                    self._handle_messages(uid, "You can't see anything in that direction!")
                return

            if self._players[uid].name.lower() == params.lower():
                self._handle_messages(uid, "You can't look at yourself!")
                return

            if [x for x in players_here if x.lower() == params.lower()]:
                pid = self._info.get_pid_by_name(self._players, params)
                msg = self._info.get_inspect_message(self._players[pid], self._items)
                self._handle_messages(uid, msg)
                self._handle_messages(uid, tid=pid, message_to_target="{} is looking at you!".format(
                            self._players[uid].name))
                self._handle_messages(uid, tid=pid, message_to_room="{} is looking at {}.".format(
                            self._players[uid].name, params.capitalize()))

            elif npc_here:
                self._handle_messages(uid, npc_here.description)
                self._handle_messages(uid, message_to_room="{} is looking at {}.".format(
                    self._players[uid].name, npc_here.long))

            else:
                self._handle_messages(uid, "You don't see {} nearby.".format(params.capitalize()))
            return

        # send player a message containing the list of players in the room
        self._handle_messages(uid, room.short)

        # list npcs if there are any
        if len(room.npcs) == 1:
            self._handle_messages(uid, "There is {} here.".format(room.npcs[0].long))
        elif len(room.npcs) == 2:
            self._handle_messages(uid, "There is {} and {} here.".format(room.npcs[0].long, room.npcs[1].long))
        elif len(room.npcs) > 2:
            self._handle_messages(
                uid,
                "There is {} and {} here.".format(
                    ", ".join([x.long for x in room.npcs[:-1]]), room.npcs[-1])
            )

        # list players if there are any
        if len(players_here) == 0 and not room.npcs:
            self._handle_messages(uid, "There is nobody here.")
        elif len(players_here) == 1:
            self._handle_messages(uid, "{} is here with you.".format(players_here[0]))
        elif len(players_here) == 2:
            self._handle_messages(uid, "{} and {} are here with you.".format(players_here[0], players_here[1]))
        elif len(players_here) > 2:
            self._handle_messages(uid, "{} and {} are here with you.".format(", ".join(players_here[:-1]), players_here[-1]))

        # list items that are on the floor
        items_on_floor = []
        for item in room.items:
            items_on_floor.append(self._items[item].long)

        if len(items_on_floor) == 0:
            self._handle_messages(uid, "There is nothing on the floor.")
        elif len(items_on_floor) == 1:
            self._handle_messages(uid, "There is {} on the floor.".format(items_on_floor[0]))
        elif len(items_on_floor) == 2:
            self._handle_messages(uid, "There is {} and {} on the floor.".format(items_on_floor[0], items_on_floor[1]))
        elif len(items_on_floor) > 2:
            self._handle_messages(
                uid,
                "There is {} and {} on the floor.".format(
                    ", ".join(items_on_floor[:-1]), items_on_floor[-1])
            )

    def _process_help_command(self, uid, command, params):
        """
        write out the room and any players or items in it
        """
        if params == "info":
            self._handle_messages(uid, """
+=========================================================================+
| The following commands deal with information.                           |
+=========================================================================+
|  COMMAND          |  DESCRIPTION                          |  SHORTHAND  |
|-------------------+---------------------------------------+-------------|
| PLAYERS           | List the players currently in game    | PL          |
| LOOK              | Examine your current surroundings     | L           |
| LOOK <WHO>        | Look at this denizen                  | L <W>       |
| LOOK <DIR>        | Look in this direction                | L <D>       |
| EXITS             | Display available exits               | EX          |
| INVENTORY         | List items in your inventory          | I           |
| STATUS            | Display your status                   | ST          |
| HEALTH            | Display brief status                  | HE          |
| EXPERIENCE        | Display experience                    | EP          |
| SPELLS            | List spells in your spellbook         | SP          |
| HELP              | Display general help message          | ?           |
+=========================================================================+    
            """)
        elif params == "shops":
            self._handle_messages(uid, """
+=========================================================================+
| The following commands work only in Shops.                              |
+=========================================================================+
|  COMMAND          |  DESCRIPTION                          |  SHORTHAND  |
|-------------------+---------------------------------------+-------------|
| LIST ITEMS        | List items available from the shop    | LS I        |
| BUY <ITEM>        | Buy an item from the shop             | B <I>       |
| SELL <ITEM>       | Sell an item from your inventory      | S <I>       |
+=========================================================================+
            """)
        elif params == "items":
            self._handle_messages(uid, """
+=========================================================================+
| The following commands deal with items.                                 |
+=========================================================================+
|  COMMAND            |  DESCRIPTION                     |  SHORTHAND     |
|---------------------+----------------------------------+----------------|
| INVENTORY           | List items in your inventory     | I              |
| GIVE <WHO> <ITEM>   | Give an item to this denizen     | GI <W> <I>     |
| GIVE <WHO> <#> GOLD | Give this denizen some gold      | GI <W> <#> GOLD|
| GET <ITEM>          | Get an item from room            | G <I>          |
| DROP <ITEM>         | Drop an item from your inventory | D <I>          |
| GET ALL             | Get all items in room            | G ALL          |
| DROP ALL            | Drop everything you're carrying  | D ALL          |
| EQUIP <ITEM>        | Equip an item from your inventory| EQ <I>         |
| UNEQUIP <ITEM>      | Unequip an equipped item         | UN <I>         |
| USE <ITEM>          | Use an item                      | U <I>          |
| USE <ITEM> <WHO>    | Use an item on this denizen      | U <I> <W>      |
| EAT <ITEM>          | Eat a ration of food             | E <I>          |
| DRINK <ITEM>        | Drink from a waterskin or potion | DR <I>         |
| LIGHT TORCH         | Light a torch                    | LI TORCH       |
+=========================================================================+
            """)
        else:
            self._handle_messages(uid, "Sorry, that is not a valid topic.")

    def _process_new_player(self, uid):
        """
        add a new players name to the dictionary and stick them in a room
        """
        self._players[uid].set_base_stats()

        # add default armor
        self._items[self._next_item] = Armor(0)
        self._players[uid].armor = self._next_item
        self._next_item += 1

        # add default armor
        self._items[self._next_item] = Weapon(0)
        self._players[uid].weapon = self._next_item
        self._next_item += 1

        print(self._items)
        print(vars(self._players[uid]))

        # go through all the players in the game
        self._handle_messages(uid, global_message="{} entered the game".format(self._players[uid].name))

        # send the new player a welcome message
        self._handle_messages(uid, "Welcome to the game, {}. ".format(
            self._players[uid].name))

        # send the new player the description of their current room
        self._process_look_command(uid)

    def _process_say_command(self, uid, command, params):
        """
        say stuff to other folks
        """
        if self._info.get_players_here(uid, self._players[uid].room, self._players):
            self._handle_messages(uid, message_to_room=(
                    "{} says: {}".format(self._players[uid].name, " ".join([command, params]))
                )
            )
            self._handle_messages(uid, "--- Message Sent ---")
            return

        self._handle_messages(uid, "Sorry, that is not an appropriate command.")

    def _process_stats_command(self, uid):
        """
        show players stats
        """
        self._handle_messages(uid, "")
        self._handle_messages(uid, f"{'Name:':15}{self._players[uid].name}")
        self._handle_messages(uid, f"{'Species:':15}{self._players[uid].get_species().capitalize()}")
        self._handle_messages(uid, f"{'Class:':15}{self._players[uid].get_class().capitalize()}")
        self._handle_messages(uid, f"{'Level:':15}{self._players[uid].level}")
        self._handle_messages(uid, f"{'Experience:':15}{self._players[uid].experience}")
        self._handle_messages(uid, f"{'Rune':15}{'None'}")
        self._handle_messages(uid, "")
        self._handle_messages(uid, f"{'Intellect:':15}{self._players[uid].int}")
        self._handle_messages(uid, f"{'Wisdom:':15}{self._players[uid].wis}")
        self._handle_messages(uid, f"{'Strength:':15}{self._players[uid].str}")
        self._handle_messages(uid, f"{'Constitution:':15}{self._players[uid].con}")
        self._handle_messages(uid, f"{'Dexterity:':15}{self._players[uid].dex}")
        self._handle_messages(uid, f"{'Charisma:':15}{self._players[uid].cha}")
        self._handle_messages(uid, "")
        self._handle_messages(uid, f"{'Hit Points:':15}{self._players[uid].vit} / {self._players[uid].vit_max}")
        self._handle_messages(uid, f"{'Mana:':15}{self._players[uid].man} / {self._players[uid].man_max}")
        self._handle_messages(uid, f"{'Status:':15}{'Healthy'}")
        self._handle_messages(uid, f"{'Armor Class:':15}{self._items[self._players[uid].armor].ac}")
        self._handle_messages(uid, "")
        self._handle_messages(uid, f"{'Weapon:':15}{self._items[self._players[uid].weapon].type.capitalize()}")
        self._handle_messages(uid, f"{'Armor:':15}{self._items[self._players[uid].armor].type.capitalize()}")
        self._handle_messages(uid, f"{'Encumbrance:':15}{self._info.get_enc(self._players[uid], self._items)} / {self._players[uid].max_enc}")
        return

    def _process_exits_command(self, uid):
        """
        list players currently in the game
        """
        exits = [self._area.exits[x] for x in self._area.get_cur_exits(self._players[uid].room)]
        if len(exits) == 0:
            self._handle_messages(uid, "There are no exits.")
        elif len(exits) == 1:
            self._handle_messages(uid, "There is an exit to the {}.".format(exits[0]))
        elif len(exits) == 2:
            self._handle_messages(uid, "There are exits to the {} and {}.".format(exits[0], exits[1]))
        else:
            self._handle_messages(uid, "There are exits to the {} and {}.".format(", ".join(exits[:-1]),
                                                                              exits[-1]))
        return

    def _process_reroll_command(self, uid):
        """
        get new stats
        """
        self._players[uid].set_base_stats()
        self._process_stats_command(uid)

    def _process_buy_command(self, uid, command, params):
        """
        buy something
        """
        room_is_shop = self._info.room_is_shop(self._players[uid])

        if not room_is_shop:
            self._process_say_command(uid, command, params)
            return

        items = self._info.get_item_list(room_is_shop[0])
        avail_items = []
        for item in items:
            if params.lower() in item.type:
                avail_items.append(item)

        if not avail_items:
            self._handle_messages(uid, "The shopkeeper doesn't seem to have that.")
            return

        if len(avail_items) > 1:
            self._handle_messages(uid, "Sorry, you'll need to be more specific.")
            return

        # found it
        avail_item = avail_items[0]

        if not avail_item.can_use(self._players[uid]):
            self._handle_messages(uid, "Sorry, you can't use that.")
            return

        if self._players[uid].level < avail_item.level:
            self._handle_messages(uid, "You're not a high enough level to use that!")
            return

        variance = randrange(0, 20) - 10
        percent_markup = (self._players[uid].get_buy_modifier() + variance) / 100
        mod_cost = int((avail_item.value * percent_markup) + avail_item.value)
        print(mod_cost)

        if mod_cost < avail_item.value:
            mod_cost = avail_item.value

        if mod_cost < 1:
            mod_cost = 1

        if mod_cost > self._players[uid].gold:
            self._handle_messages(uid, "Sorry, you don't have enough gold purchase {}.".format(avail_item.long))
            return

        if len(self._players[uid].inventory) + 1 > self._players[uid].max_inv:
            self._handle_messages(uid, "Sorry, you don't have enough room in your inventory for {}.".format(avail_item.long))
            return

        if self._info.get_enc(self._players[uid], self._items) + avail_item.weight > self._players[uid].max_enc:
            self._handle_messages(uid, "Sorry, you're not strong enough to carry {}'.".format(avail_item.long))
            return

        # add it to inventory!
        self._players[uid].gold -= avail_item.value
        self._items[self._next_item] = avail_item
        self._players[uid].inventory.append(self._next_item)
        self._next_item += 1

        # go through all the players in the game
        self._handle_messages(uid, message_to_room="{} purchased {}.".format(
            self._players[uid].name, avail_item.long))

        self._handle_messages(uid, "You purchased {} for {} gold.".format(
            avail_item.long, mod_cost))

        print(self._players[uid].inventory)
        print(self._items)

        return

    def _process_get_command(self, uid, params):
        """
        pick something up
        """
        room = self._area.get_cur_room(self._players[uid].room)

        item_to_get = None
        index_of_item = None
        for index, item in enumerate(room.items):
            if params in self._items[item].type:
                item_to_get = self._items[item]
                index_of_item = item
                break

        if not item_to_get:
            self._handle_messages(uid, "Sorry, but you don't see that nearby.")
            return

        if len(self._players[uid].inventory) >= 8:
            self._handle_messages(uid, "Sorry, but there is no more room in your inventory.")
            return

        self._players[uid].inventory.append(index_of_item)
        room.items.remove(index_of_item)

        # go through all the players in the game
        self._handle_messages(uid, message_to_room="{} just picked up {}.".format(
            self._players[uid].name, item_to_get.long))

        self._handle_messages(uid, "You picked up {}.".format(
            item_to_get.long))

    def _handle_give_gold(self, uid, player_to, amt_from):
        """
        give an item to another player
        """
        pid = self._info.get_pid_by_name(self._players, player_to)
        print(pid)

        if pid == uid:
            self._handle_messages(uid, "Sorry, you can't give gold to yourself.")
            return

        players_here = self._info.get_players_here(uid, self._players[uid].room, self._players)
        if not [x for x in players_here if x.lower() == player_to.lower()]:
            self._handle_messages(uid, "Sorry, you don't see them nearby.")
            return

        if pid is None:
            self._handle_messages(uid, "You don't see {} nearby.".format(player_to.capitalize()))
            return

        if amt_from <= 0:
            self._handle_messages(uid, "You need to give at least 1 gold.")
            return

        if amt_from > self._players[uid].gold:
            self._handle_messages(uid, "You don't seem to have enough.")
            return

        if self._players[pid].enc + int(amt_from * 0.2) > self._players[pid].max_enc:
            self._handle_messages(
                uid, "Sorry, {} can''t carry that much more gold.".format(self._players[pid].name))
            return

        self._players[uid].gold -= amt_from
        self._players[pid].gold += amt_from

        self._handle_messages(uid, "You gave {} gold coins to {}.".format(amt_from, self._players[pid].name))
        self._handle_messages(
            uid, tid=pid, message_to_target="{} gave you {} gold coins.".format(self._players[uid].name, amt_from))
        self._handle_messages(
            uid, tid=pid, message_to_room="{} gave some gold coins to {}.".format(self._players[uid].name, self._players[pid].name))

    def _handle_give_item(self, uid, player_to, item_from):
        """
        give an item to another player
        """
        item_to_give = None
        index_of_item = None
        for index, item in enumerate(self._players[uid].inventory):
            if item_from in self._items[item].type:
                item_to_give = self._items[item]
                index_of_item = item
                break

        if not item_to_give:
            self._handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        pid = self._info.get_pid_by_name(self._players, player_to)
        print(pid)

        if pid == uid:
            self._handle_messages(uid, "Sorry, you can't give items to yourself.")
            return

        players_here = self._info.get_players_here(uid, self._players[uid].room, self._players)

        if not [x for x in players_here if x.lower() == player_to.lower()]:
            self._handle_messages(uid, "Sorry, you don't see them nearby.")
            return

        if len(self._players[pid].inventory) >= 8:
            self._handle_messages(uid, "Sorry, {} can't carry anything else.".format(player_to.capitalize()))
            return

        if self._players[pid].enc + item_to_give.weight >= self._players[pid].max_enc:
            self._handle_messages(uid, "Sorry, {} can't carry any more weight.".format(player_to.capitalize()))
            return

        self._players[pid].inventory.append(index_of_item)
        self._players[uid].inventory.remove(index_of_item)

        print(uid, self._players[uid].name)
        print(pid, self._players[pid].name)

        print(uid, pid)

        message_to_room = "{} gave {} to {}.".format(self._players[uid].name, item_to_give.long, player_to.capitalize())
        self._handle_messages(uid, tid=pid, message_to_room=message_to_room)

        message_to_target = "{} just gave you {}".format(self._players[uid].name, item_to_give.long)
        self._handle_messages(uid, tid=pid, message_to_target=message_to_target)

        message_to_player = "You just gave {} to {}.".format(item_to_give.long, player_to.capitalize())
        self._handle_messages(uid, message_to_player=message_to_player)

    def _process_give_command(self, uid, command, params):
        """
        give something

        give <player> <item>
        give <player> <amt> gold

        """

        if len(params.split()) == 1:
            self._handle_messages(uid, "What do you want to give to {}.".format(params))
            return
        elif len(params.split()) == 2:
            player_to, item_from = params.split()
            self._handle_give_item(uid, player_to, item_from)
        elif len(params.split()) == 3:
            player_to, amt_from, gold = params.split()
            if gold == 'gold' and amt_from.isnumeric():
                self._handle_give_gold(uid, player_to, int(amt_from))
                return
            self._handle_messages(uid, "Sorry, but you don't seem to have one.")
            return
        else:
            self._process_say_command(uid, command, params)

        return

    def _process_drop_command(self, uid, params):
        """
        drop something
        """
        room = self._area.get_cur_room(self._players[uid].room)

        item_to_drop = None
        index_of_item = None
        for index, item in enumerate(self._players[uid].inventory):
            if params in self._items[item].type:
                item_to_drop = self._items[item]
                index_of_item = item
                break

        if not item_to_drop:
            self._handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        if room.is_town():
            self._handle_messages(uid, "Sorry, littering is not permitted here.")
            return

        if len(room.items) >= 8:
            self._handle_messages(uid, "Sorry, but there is no more room here to drop items.")
            return

        room.items.append(index_of_item)
        self._players[uid].inventory.remove(index_of_item)
        z, x, y = self._players[uid].room
        print(self._area.grid[z][x][y].items)

        # go through all the players in the game
        self._handle_messages(uid, message_to_room="{} just dropped {}.".format(
            self._players[uid].name, item_to_drop.long))

        self._handle_messages(uid, "You dropped your {}.".format(
            item_to_drop.type))

    def _process_sell_command(self, uid, command, params):
        """
        sell something
        """
        room_is_shop = self._info.room_is_shop(self._players[uid])

        if not room_is_shop:
            self._process_say_command(uid, command, params)
            return

        items_in_shop = self._info.get_item_list(room_is_shop[0])
        item_for_sale = None
        index_of_item = None
        for index, item in enumerate(self._players[uid].inventory):
            if params in self._items[item].type:
                item_for_sale = self._items[item]
                index_of_item = item

        if not item_for_sale:
            self._handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        shop_is_interested = False
        for item_in_shop in items_in_shop:
            if item_for_sale.type == item_in_shop.type:
                shop_is_interested = True
                break

        if not shop_is_interested:
            self._handle_messages(uid, "Sorry, the shopkeeper doesn't want that.")
            return

        proceeds = -(-item_for_sale.value // 2)   # round up!

        # go through all the players in the game
        self._handle_messages(uid, "{} sold {}.".format(
            self._players[uid].name, item_for_sale.long))

        self._handle_messages(uid, "You sold {} for {} gold.".format(
            item_for_sale.long, proceeds))

        print(self._players[uid].inventory)
        print(index_of_item)

        # give player money and remove item from game
        self._players[uid].gold += proceeds
        self._players[uid].inventory.remove(index_of_item)
        self._items.pop(index_of_item)

        print(self._items)
        print(self._players[uid].inventory)

    def _process_health_command(self, uid):
        """
        get new stats
        """
        self._handle_messages(uid, f"{'Hit Points:':15}{self._players[uid].vit} / {self._players[uid].vit_max}")
        self._handle_messages(uid, f"{'Mana:':15}{self._players[uid].man} / {self._players[uid].man_max}")
        self._handle_messages(uid, f"{'Status:':15}{'Healthy'}")

    def _process_equip_command(self, uid, params):
        """
        get new stats
        """
        item_to_equip = None
        index_of_item = 0
        equipped = False

        for index, item in enumerate(self._players[uid].inventory):
            if params in self._items[item].type:
                item_to_equip = self._items[item]
                index_of_item = item

        if not item_to_equip:
            self._handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        if not item_to_equip.can_use(self._players[uid]):
            self._handle_messages(uid, "Sorry, you can't equip that.")
            return

        if self._players[uid].level < item_to_equip.level:
            self._handle_messages(uid, "You're not a high enough level to equip that.")
            return

        print(type(item_to_equip))

        if isinstance(item_to_equip, Armor):
            print("armor", item_to_equip.type)
            print(self._players[uid].armor)

            # unequip first
            self._players[uid].inventory.append(self._players[uid].armor)
            old_item = self._players[uid].armor

            # equip new weapon
            self._players[uid].inventory.remove(index_of_item)
            self._items[self._next_item] = item_to_equip
            self._players[uid].armor = self._next_item
            self._next_item += 1
            equipped = True

        elif isinstance(item_to_equip, Weapon):
            print("weapon", item_to_equip.type)
            print(self._players[uid].weapon)

            # unequip first
            self._players[uid].inventory.append(self._players[uid].weapon)
            old_item = self._players[uid].weapon

            # equip new weapon
            self._players[uid].inventory.remove(index_of_item)
            self._items[self._next_item] = item_to_equip
            self._players[uid].weapon = self._next_item
            self._next_item += 1
            equipped = True

        if not equipped:
            return

        # go through all the players in the game
        self._handle_messages(uid, message_to_room="{} just equipped {}.".format(
            self._players[uid].name, item_to_equip.long))

        self._handle_messages(uid, "You just equipped {} and removed {}.".format(
            item_to_equip.long, self._items[old_item].long))

    def _process_experience_command(self, uid):
        """
        get new stats
        """
        self._handle_messages(uid, f"{'Level:':15}{self._players[uid].level}")
        self._handle_messages(uid, f"{'Experience:':15}{self._players[uid].experience}")
        self._handle_messages(uid, f"{'Rune':15}{'None'}")

    def _process_inventory_command(self, uid):
        """
        get new stats
        """
        inventory = []
        for item in self._players[uid].inventory:
            inventory.append(self._items[item].long)

        if not inventory:
            self._handle_messages(uid, f"You are carrying {self._players[uid].gold} gold coins.")
            return

        msg = f"You are carrying {self._players[uid].gold} gold coins "

        if len(inventory) == 1:
            msg += "and {}.".format(inventory[0])
        elif len(inventory) == 2:
            msg += "{} and {}.".format(inventory[0], inventory[1])
        else:
            msg += "{} and {}.".format(", ".join(inventory[:-1]), inventory[-1])

        self._handle_messages(uid, msg)

    def _process_list_items_command(self, uid):
        """
        list items in shops you can buy
        """
        room_is_shop = self._info.room_is_shop(self._players[uid])

        if not room_is_shop:
            return

        items = self._info.get_item_list(room_is_shop[0])

        self._handle_messages(uid, "")
        self._handle_messages(uid, "+======================+======+==+")
        self._handle_messages(uid, "| Item                 |   Price |")
        self._handle_messages(uid, "+----------------------+---------+")

        for item in sorted(items, key=lambda x: x.value):
            self._handle_messages(
                uid, (
                    f"| {item.type:21}"
                    f"| {item.value:7} |"
                )
            )

        self._handle_messages(uid, "+======================+=========+")

        self._handle_messages(uid, message_to_room="{} is browsing the wares.".format(
            self._players[uid].name))

    def _process_players_command(self, uid):
        """
        list players currently in the game
        """

        players = self._info.get_current_players(self._players)

        if not players:
            return

        if len(players) == 1:
            self._handle_messages(uid, "{} is playing.".format(players[0]))
        elif len(players) == 2:
            self._handle_messages(uid, "{} and {} are playing.".format(players[0], players[1]))
        else:
            self._handle_messages(uid, "{} and {} are playing.".format(", ".join(players[:-1]), players[-1]))

    def _process_quit_command(self, uid):
        """
        exit on your own terms
        """
        self._handle_messages(uid, "Goodbye, {}.".format(
            self._players[uid].name))
        self._mud.get_disconnect(uid)

    def _process_go_command(self, uid, command):
        """ move around """

        command = command[:1].lower()

        # get current room and list of exits
        cur_exits = self._area.get_cur_exits(self._players[uid].room)

        if command not in cur_exits:
            self._handle_messages(uid, "You can't go that way!")
            return

        cur_player_room = self._players[uid].room
        next_player_room = self._area.get_next_room(cur_player_room, command)

        # tell people you're leaving
        self._handle_messages(uid, message_to_room="{} just left to the {}.".format(
            self._players[uid].name, self._area.exits[command]))

        # move player to next room
        self._players[uid].room = next_player_room

        # tell people you've arrived
        self._handle_messages(uid, message_to_room="{} just arrived from the {}.".format(
            self._players[uid].name, self._area.exits[command]))

        # send the player a message telling them where they are now
        self._process_look_command(uid)

    def check_for_new_players(self):
        """
        check to see if any new connections arrived since last update
        """
        # go through any newly connected players
        for pid in self._mud.get_new_players():

            # add the new player to the dictionary, noting that they've not
            # named yet.
            # The dictionary key is the player's id number. We set their room
            # None initially until they have entered a name
            # Try adding more player stats - level, gold, inventory, etc
            self._players[pid] = Player()

            # send the new player a prompt for their name
            self._handle_messages(pid, "What is your name?")

    def check_for_disconnected_players(self):
        """
        check to see if anyone disconnected since last update
        """
        for uid in self._mud.get_disconnected_players():

            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self._players:
                continue

            # go through all the players in the game
            self._handle_messages(uid, global_message="{} quit the game".format(
                self._players[uid].name))

            # remove the player's entry in the player dictionary
            del self._players[uid]

    def check_for_new_commands(self):
        """
        check to see if any new commands are on the queue
        """
        for uid, command, params in self._mud.get_commands():

            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self._players:
                continue

            # if the player hasn't given their name yet, use this first command
            # their name and move them to the starting room.
            if self._players[uid].name is None:

                self._players[uid].name = command.capitalize()

                self._handle_messages(uid, "")
                self._handle_messages(uid, "+==========+============+")
                self._handle_messages(uid, "| Num      | Species    |")
                self._handle_messages(uid, "+----------+------------+")
                for num, species in self._species.items():
                    self._handle_messages(
                        uid, (
                            f"| {num:<9}"
                            f"| {species['type']:11}|"
                        )
                    )
                self._handle_messages(uid, "+==========+============+")
                self._handle_messages(uid, "")
                self._handle_messages(uid, "What species are you?")

            elif self._players[uid].species is None:

                self._players[uid].species = int(command)

                self._handle_messages(uid, "")
                self._handle_messages(uid, "+==========+============+")
                self._handle_messages(uid, "| Num      | Class      |")
                self._handle_messages(uid, "+----------+------------+")
                for num, classes in self._classes.items():
                    self._handle_messages(
                        uid, (
                            f"| {num:<9}"
                            f"| {classes['type']:11}|"
                        )
                    )
                self._handle_messages(uid, "+==========+============+")
                self._handle_messages(uid, "")
                self._handle_messages(uid, "What class are you?")

            elif self._players[uid].p_class is None:

                self._players[uid].p_class = int(command)
                self._process_new_player(uid)

            # 'help' command
            elif command == "help":
                self._process_help_command(uid, command, params)

            # 'look' command
            elif command in [""]:
                self._process_look_command(uid)

            # 'go' command
            elif command in [
                "east", "e",
                "west", "w",
                "north", "n",
                "south",
                "up", "u",
                "down"
            ]:
                self._process_go_command(uid, command)

            # 'look' command
            elif command == "look" or command == "l":
                self._process_look_command(uid, command, params)

            # 'reroll' command
            elif command == "reroll" or command == "re":
                self._process_reroll_command(uid)

            # 'players' command
            elif command == "players" or command == "pl":
                self._process_players_command(uid)

            # 'exits' command
            elif command == "exits" or command == "ex":
                self._process_exits_command(uid)

            # 'inventory' command
            elif command == "inventory" or command == "i":
                self._process_inventory_command(uid)

            # 'status' command
            elif command == "status" or command == "st":
                self._process_stats_command(uid)

            # 'health' command
            elif command == "health" or command == "he":
                self._process_health_command(uid)

            # 'experience' command
            elif command == "experience" or command == "ep":
                self._process_experience_command(uid)

            # 'list' command
            elif command == "list" or command == "ls":
                if not params:
                    self._process_say_command(uid, command, params)
                elif params == "items" or params == "i":
                    self._process_list_items_command(uid)
                else:
                    self._process_say_command(uid, command, params)

            # 'spells' command
            elif command == "spells" or command == "sp":
                self._process_spells_command(uid, command, params)

            # 'buy' command
            elif command == "buy" or command == "b":
                self._process_buy_command(uid, command, params)

            # 'equip' command
            elif command == "equip" or command == "eq":

                if params:
                    self._process_equip_command(uid, params)
                else:
                    self._process_say_command(uid, command, params)

            # 'sell' command
            elif command == "sell":
                self._process_sell_command(uid, command, params)

            # 'drop' command
            elif command == "drop":
                if params:
                    self._process_drop_command(uid, params)
                else:
                    self._process_say_command(uid, command, params)

            # 'get' command
            elif command == "get" or command == "g":
                if params:
                    self._process_get_command(uid, params)
                else:
                    self._process_say_command(uid, command, params)

            # 'give' command
            elif command == "give":
                if params:
                    self._process_give_command(uid, command, params)
                else:
                    self._process_say_command(uid, command, params)

            # 'sell' if params otherwise 'go'
            elif command == "s":
                if not params:
                    self._process_go_command(uid, command)
                else:
                    self._process_sell_command(uid, params)

                # 'sell' if params otherwise 'go'
            elif command == "d":
                if not params:
                    self._process_go_command(uid, command)
                else:
                    self._process_drop_command(uid, params)

            # 'quit' command
            elif command == "quit":
                self._process_quit_command(uid)

            # everything else assume player is talking
            else:
                self._process_say_command(uid, command, params)


def _stop(stop_signal, frame):  # pylint: disable=unused-argument
    """
    Raise KeyboardInterrupt to cleanly exit.

    Args:
        stop_signal (int): System signal.
        frame (frame): Stack frame.
    """
    print("Stop signal received")
    raise SystemExit(stop_signal)


def _game_loop(mud, game):
    # main game loop. We loop forever (i.e. until the program is terminated)
    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()

    game.check_for_new_players()

    game.check_for_disconnected_players()

    game.check_for_new_commands()


def _initialize_jobs(mud):
    """ run some background tasks """
    job_defaults = {
        'coalesce': True
    }
    scheduler = BackgroundScheduler()
    scheduler.configure(job_defaults=job_defaults, timezone='UTC')

    # create an instance of the game
    game = Game(mud)
    scheduler.add_job(
        _game_loop,
        'interval',
        args=[
            mud,
            game
        ],
        seconds=0.2,
        id='game_loop',
    )

    # sustenance job
    sustenance = Sustenance(game)
    scheduler.add_job(
        sustenance.get_sustenace,
        'interval',
        seconds=10,
        id='sustenance_job',
    )

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGQUIT, _stop)

    stopping = False

    def time_to_stop():
        return stopping

    stop_condition = Condition()
    try:
        scheduler.start()
        with stop_condition:
            stop_condition.wait_for(time_to_stop)
    except (KeyboardInterrupt, SystemExit) as e:
        if isinstance(e, KeyboardInterrupt):
            print("Keyboard interrupt, shutting down.")
        elif e.args:
            print("Stopping on signal %d", e.args[0])
        else:
            print("Unknown signal received, stopping.")

        scheduler.shutdown()

        with stop_condition:
            stopping = True
            stop_condition.notify()

        return False


def main():
    """
    function main
    args: none
    returns: none
    """

    # start the server
    mud = Mud()

    # schedule the game jobs
    _initialize_jobs(mud)


if __name__ == '__main__':
    sys.exit(main())
