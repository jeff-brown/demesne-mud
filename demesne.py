#!/usr/bin/python3

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

author: Mark Frimston - mfrimston@gmail.com
modified by: Jeff Brown - jeffbr@gmail.com
"""

from random import randint
import pickle
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
from lib.equipment import Equipment
from lib.mob import Mob
from lib.combat import Combat
from lib.gong import Gong
from lib.training import Training

# like it's a job
from jobs.sustenance import Sustenance
from jobs.regenerate import Regenerate
from jobs.slow_status import SlowStatus
from jobs.item_effect import ItemEffect
from jobs.rest import Rest
from jobs.mob_activity import MobActivity
from jobs.repopulate_lairs import RepopulateLairs

# enums
from enums.status import Status

# import the MUD server class
from server.mud import Mud


class Game:
    """
    This class contains all the functions to allow the game to operate
    """

    def __init__(self, mud, players, items):
        # public members
        self.players = {}
        self.state = players
        self.mobs = {}
        self.next_mob = 0
        self.mob_items = {}
        self.next_mob_item = 0
        self.items = items
        if items:
            self._next_item = max([x for x in items.keys()]) + 1
        else:
            self._next_item = 0

        # private members
        self._area = Area()
        self._info = Info(self)
        self._data = Data()
        self._combat = Combat(self)
        self._gong = Gong(self)
        self._training = Training(self)

        self.grid = self._area.grid
        self._mud = mud
        self._tick = 6  # 6 seconds
        self._species = self._data.species
        self._classes = self._data.classes
        self._weapons = self._data.weapons
        self._armor = self._data.armor
        self._equipment = self._data.equipment
        self._messages = self._data.messages

        # counter for assigning each client a new id
        self._nextid = 0
        self._next_monster = 0

    def handle_messages(
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
            uid, self.players[uid].room, self.players)

        if message_to_player is not None:
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

        if global_message is not None:
            print("global_message", uid, global_message)
            for pid, _ in self.players.items():
                if pid != uid:
                    self._mud.send_message(pid, global_message)
            return

    def _process_look_command(self, uid, command=None, params=None, location=None):
        """
        write out the room and any players or items in it
        """

        npc_here = None
        mob_here = None
        self.handle_messages(uid)

        if not location:
            location = self.players[uid].room

        exits = self._area.get_cur_exits(location)
        room = self._area.get_cur_room(location)

        print("cur_room", room.short)
        print("player", self.players[uid].name)

        players_here = self._info.get_players_here(uid, location, self.players)
        pids_here = self._info.get_pids_here(uid, location, self.players)
        if not room.is_illuminated(uid, pids_here, self.players, self.items):
            self.handle_messages(uid, self._data.messages['TOODRK'])
            return

        if room.npcs and params:
            for npc in room.npcs:
                if params.lower() in npc.type:
                    npc_here = npc
                    break
        print(npc_here)

        if room.mobs and params:
            for mob in room.mobs:
                if params.lower() in self.mobs[mob].name:
                    mob_here = self.mobs[mob]
                    break
        print(mob_here)
        print(self.mobs)

        if command and not params:
            self.handle_messages(uid, room.long)
            self.handle_messages(uid, message_to_room=self._data.messages['LOKOTH'].format(
                self.players[uid].name))
            return

        if params:
            if self._area.is_exit(params):
                if params[0] in exits:
                    print(self._area.get_next_room(location, params[0]))
                    self._process_look_command(uid, location=self._area.get_next_room(location, params[0]))
                else:
                    self.handle_messages(uid, self._data.messages['NOEXIT'])
                return

            if self.players[uid].name.lower() == params.lower():
                self.handle_messages(uid, self._data.messages['NOLSLF'])
                return

            if [x for x in players_here if x.lower() == params.lower()]:
                pid = self._info.get_pid_by_name(self.players, params)
                msg = self._info.get_inspect_message(self.players[pid], self.items)
                self.handle_messages(uid, msg)
                self.handle_messages(uid, tid=pid, message_to_target=self._data.messages['INSPCT'].format(
                            self.players[uid].name))
                self.handle_messages(uid, tid=pid, message_to_room=self._data.messages['INSOTH1'].format(
                            self.players[uid].name, params.capitalize()))

            elif npc_here:
                self.handle_messages(uid, npc_here.description)
                self.handle_messages(uid, message_to_room=self._data.messages['INSOTH1'].format(
                    self.players[uid].name, npc_here.long))

            elif mob_here:
                self.handle_messages(uid, mob_here.get_look_description())
                self.handle_messages(uid, message_to_room=self._data.messages['INMOTH'].format(
                    self.players[uid].name, mob_here.name))

            else:
                self.handle_messages(uid, self._data.messages['ARNNHR'].format(params.capitalize()))
            return

        # send player a message containing the list of players in the room
        msg = self._data.messages['YELLO'] + room.short + self._data.messages['WHITE']
        self.handle_messages(uid, msg)

        # list npcs if there are any
        if len(room.npcs) == 1:
            self.handle_messages(uid, self._data.messages['SOMTNG'].format(room.npcs[0].long))
        elif len(room.npcs) == 2:
            self.handle_messages(uid, self._data.messages['SOMTN2'].format(room.npcs[0].long, room.npcs[1].long))
        elif len(room.npcs) > 2:
            self.handle_messages(
                uid,
                self._data.messages['SOMTN2'].format(
                    ", ".join([x.long for x in room.npcs[:-1]]), room.npcs[-1])
            )

        # list mobs if there are any
        print("look at mobs")
        print(len(room.mobs))
        print(room.mobs)
        mobs_in_room = []
        print(self.mobs)
        for mob in room.mobs:
            mobs_in_room.append(self.mobs[mob].name)

        if len(mobs_in_room) == 1:
            self.handle_messages(uid, self._data.messages['SOMMNG'].format(mobs_in_room[0]))
        elif len(mobs_in_room) == 2:
            self.handle_messages(
                uid, self._data.messages['SOMMN2'].format(
                    mobs_in_room[0], mobs_in_room[1]))
        elif len(room.mobs) > 2:
            self.handle_messages(
                uid,
                self._data.messages['SOMMN2'].format(
                    ", ".join([x for x in mobs_in_room[:-1]]), mobs_in_room[-1])
            )

        # list players if there are any
        if len(players_here) == 0 and not room.npcs and not room.mobs:
            self.handle_messages(uid, self._data.messages['BYSELF'])
        elif len(players_here) == 1:
            self.handle_messages(uid, self._data.messages['ONEOTH'].format(players_here[0]))
        elif len(players_here) == 2:
            self.handle_messages(uid, self._data.messages['SOMMN3'].format(players_here[0], players_here[1]))
        elif len(players_here) > 2:
            self.handle_messages(uid, self._data.messages['SOMMN3'].format(", ".join(players_here[:-1]), players_here[-1]))

        # list items that are on the floor
        items_on_floor = []
        for item in room.items:
            items_on_floor.append(self.items[item].long)

        if len(items_on_floor) == 0:
            self.handle_messages(uid, self._data.messages['NOTING'])
        elif len(items_on_floor) == 1:
            msg = f"{self._data.messages['SOMTN3']} {items_on_floor[0]} {self._data.messages['ONFLOR']}"
            self.handle_messages(uid, msg)
        elif len(items_on_floor) == 2:
            msg = (
                f"{self._data.messages['SOMTN3']} {items_on_floor[0]} and {items_on_floor[1]} "
                f"{self._data.messages['ONFLOR']}"
            )
            self.handle_messages(uid, msg)
        elif len(items_on_floor) > 2:
            msg = (
                f"{self._data.messages['SOMTN3']} {', '.join(items_on_floor[:-1])} and {items_on_floor[-1]} "
                f"{self._data.messages['ONFLOR']}"
            )
            self.handle_messages(uid, msg)

    def _process_help_command(self, uid, command, params):
        """
        write out the room and any players or items in it
        """
        if params == "info":
            self.handle_messages(uid, """
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
            self.handle_messages(uid, """
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
            self.handle_messages(uid, """
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
            self.handle_messages(uid, "Sorry, that is not a valid topic.")

    def _process_new_player(self, uid):
        """
        add a new players name to the dictionary and stick them in a room
        """
        self.players[uid].set_base_stats()

        # add default armor
        self.items[self._next_item] = Armor(0)
        self.players[uid].armor = self._next_item
        self._next_item += 1

        # add default armor
        self.items[self._next_item] = Weapon(0)
        self.players[uid].weapon = self._next_item
        self._next_item += 1

        print(self.items)
        print(vars(self.players[uid]))

        # go through all the players in the game
        self.handle_messages(uid, global_message=self._data.messages['XARENT'].format(self.players[uid].name))

        # send the new player a welcome message
        self.handle_messages(uid, self._data.messages['WELCO1'].format(self.players[uid].name))

        # send the new player the description of their current room
        self._process_look_command(uid)

    def _process_say_command(self, uid, command, params):
        """
        say stuff to other folks
        """
        if self._info.get_players_here(uid, self.players[uid].room, self.players):
            self.handle_messages(uid, message_to_room=(
                    self._data.messages['MSGFRM'].format(self.players[uid].name, " ".join([command, params]))
                )
            )
            self.handle_messages(uid, self._data.messages['MSGSNT'])
            return

        self.handle_messages(uid, self._data.messages['BYSELF2'])

    def _process_stats_command(self, uid):
        """
        show players stats
        """
        self.handle_messages(uid, "")
        self.handle_messages(uid, f"{'Name:':15}{self.players[uid].name}")
        self.handle_messages(uid, f"{'Species:':15}{self.players[uid].get_species().capitalize()}")
        self.handle_messages(uid, f"{'Class:':15}{self.players[uid].get_class().capitalize()}")
        self.handle_messages(uid, f"{'Level:':15}{self.players[uid].level}")
        self.handle_messages(uid, f"{'Experience:':15}{self.players[uid].experience}")
        self.handle_messages(uid, f"{'Rune':15}{'None'}")
        self.handle_messages(uid, "")
        self.handle_messages(uid, f"{'Intellect:':15}{self.players[uid].int}")
        self.handle_messages(uid, f"{'Wisdom:':15}{self.players[uid].wis}")
        self.handle_messages(uid, f"{'Strength:':15}{self.players[uid].get_str()}")
        self.handle_messages(uid, f"{'Constitution:':15}{self.players[uid].con}")
        self.handle_messages(uid, f"{'Dexterity:':15}{self.players[uid].get_dex()}")
        self.handle_messages(uid, f"{'Charisma:':15}{self.players[uid].cha}")
        self.handle_messages(uid, "")
        self.handle_messages(uid, f"{'Hit Points:':15}{self.players[uid].vit} / {self.players[uid].vit_max}")
        self.handle_messages(uid, f"{'Mana:':15}{self.players[uid].man} / {self.players[uid].man_max}")
        self.handle_messages(uid, f"{'Status:':15}{self.players[uid].status.name}")
        self.handle_messages(uid, f"{'Armor Class:':15}{self.items[self.players[uid].armor].ac}")
        self.handle_messages(uid, "")
        self.handle_messages(uid, f"{'Weapon:':15}{self.items[self.players[uid].weapon].type.capitalize()}")
        self.handle_messages(uid, f"{'Armor:':15}{self.items[self.players[uid].armor].type.capitalize()}")
        self.handle_messages(uid, f"{'Encumbrance:':15}{self._info.get_enc(self.players[uid], self.items)} / {self.players[uid].max_enc}")
        return

    def _process_exits_command(self, uid):
        """
        list players currently in the game
        """
        exits = [self._area.exits[x] for x in self._area.get_cur_exits(self.players[uid].room)]
        if len(exits) == 0:
            self.handle_messages(uid, self._data.messages['NOEXT1'])
        elif len(exits) == 1:
            self.handle_messages(uid, self._data.messages['ONEEXT'].format(exits[0]))
        elif len(exits) == 2:
            self.handle_messages(uid, self._data.messages['SOMEXT'].format(exits[0], exits[1]))
        else:
            self.handle_messages(uid, self._data.messages['SOMEXT'].format(", ".join(exits[:-1]), exits[-1]))
        return

    def _process_reroll_command(self, uid):
        """
        get new stats
        """
        self.players[uid].set_base_stats()
        self._process_stats_command(uid)

    def _handle_tavern(self, uid, params):
        """
        let a player buy a mean or drink in a tavern
        """
        meal_cost = 2
        drink_cost = 1

        if not [x for x in ['meal', 'drink'] if x == params]:
            self.handle_messages(uid, self._data.messages['NOSITM'])
            return

        if params == "meal":
            if meal_cost > self.players[uid].gold:
                self.handle_messages(uid, self._data.messages['CNTAFD'].format(params))
                return

            self.handle_messages(uid, self._data.messages['YOUGTM'].format(meal_cost))
            self.handle_messages(uid, message_to_room=self._data.messages['OTHGTM'].format(self.players[uid].name))
            self.players[uid].hunger_ticker = time.time()
            self.players[uid].status = Status.Healthy
            self.players[uid].gold -= meal_cost

            return

        if params == "drink":
            if drink_cost > self.players[uid].gold:
                self.handle_messages(uid, self._data.messages['CNTAFD'].format(params))
                return

            self.handle_messages(uid, self._data.messages['YOUGTD'].format(meal_cost))
            self.handle_messages(uid, message_to_room=self._data.messages['OTHGTD'].format(self.players[uid].name))
            self.players[uid].thirst_ticker = time.time()
            self.players[uid].status = Status.Healthy
            self.players[uid].gold -= meal_cost

            return

    def _handle_temple(self, uid, params):
        """
        do the temple stuff
        """
        if not [x for x in ['healing'] if x == params]:
            self.handle_messages(uid, self._data.messages['DNTOFF'])
            return

        if params == "healing":
            damage_to_heal = self.players[uid].vit_max - self.players[uid].vit
            cost_to_heal = int((damage_to_heal / 10) + 1)

            if cost_to_heal > self.players[uid].gold:
                self.handle_messages(uid, self._data.messages['CNTAFD'].format(params))
                return

            self.handle_messages(uid, self._data.messages['YOUGTH'].format(cost_to_heal))
            self.handle_messages(
                uid,
                message_to_room=self._data.messages['OTHGTH'].format(self.players[uid].name, self.players[uid].name))
            self.players[uid].gold -= cost_to_heal
            self.players[uid].vit = self.players[uid].vit_max

    def _process_buy_command(self, uid, command, params):
        """
        buy something
        """
        if self._info.room_is_guild(self.players[uid]):
            if "training" in params:
                print(f"exp_gain: {self._info.get_exp_gain(self.players[uid])}")
                self._training.handle_training(self.players[uid])
            return

        if self._info.room_is_tavern(self.players[uid]):
            self._handle_tavern(uid, params)
            return

        if self._info.room_is_temple(self.players[uid]):
            self._handle_temple(uid, params)
            return

        room_is_shop = self._info.room_is_shop(self.players[uid])

        if not room_is_shop:
            self._process_say_command(uid, command, params)
            return

        items = self._info.get_item_list(room_is_shop)
        avail_items = []
        for item in items:
            if params.lower() in item.type:
                avail_items.append(item)

        if not avail_items:
            self.handle_messages(uid, self._data.messages['NSOHER'])
            return

        if len(avail_items) > 1:
            self.handle_messages(uid, self._data.messages['BMRSPC'])
            return

        # found it
        avail_item = avail_items[0]

        if not avail_item.can_use(self.players[uid]):
            self.handle_messages(uid, self._data.messages['CNTUSE'].format(avail_item.long))
            return

        if self.players[uid].level < avail_item.level:
            self.handle_messages(uid,  self._data.messages['TOOINX'])
            return

        variance = randint(0, 21) - 10
        percent_markup = (self.players[uid].get_buy_modifier() + variance) / 100
        mod_cost = int((avail_item.value * percent_markup) + avail_item.value)
        print(mod_cost)

        if mod_cost < avail_item.value:
            mod_cost = avail_item.value

        if mod_cost < 1:
            mod_cost = 1

        if mod_cost > self.players[uid].gold:
            self.handle_messages(uid, self._data.messages['CNTAFD'].format(avail_item.long))
            return

        if len(self.players[uid].inventory) + 1 > self.players[uid].max_inv:
            self.handle_messages(uid, self._data.messages['INVFUL'])
            return

        if self._info.get_enc(self.players[uid], self.items) + avail_item.weight > self.players[uid].max_enc:
            self.handle_messages(uid, self._data.messages['TOOHVY'])
            return

        # add it to inventory!
        self.players[uid].gold -= avail_item.value
        self.items[self._next_item] = avail_item
        self.players[uid].inventory.append(self._next_item)
        self._next_item += 1

        # go through all the players in the game
        self.handle_messages(uid, message_to_room=self._data.messages['BUYOTH'].format(
            self.players[uid].name, avail_item.long))

        self.handle_messages(uid, self._data.messages['YOUGOT'].format(avail_item.long, mod_cost))

        print(self.players[uid].inventory)
        print(self.items)

        return

    def _process_get_command(self, uid, params):
        """
        pick something up
        """
        room = self._area.get_cur_room(self.players[uid].room)

        item_to_get = None
        index_of_item = None
        for index, item in enumerate(room.items):
            if params in self.items[item].type:
                item_to_get = self.items[item]
                index_of_item = item
                break

        if not item_to_get:
            self.handle_messages(uid, self._data.messages['NSIHER'])
            return

        if len(self.players[uid].inventory) >= 8:
            self.handle_messages(uid, self._data.messages['INVFUL'])
            return

        if self._info.get_enc(self.players[uid], self.items) + item_to_get.weight > self.players[uid].max_enc:
            self.handle_messages(uid, self._data.messages['TOOHVY'])
            return

        self.players[uid].inventory.append(index_of_item)
        room.items.remove(index_of_item)

        # go through all the players in the game
        self.handle_messages(uid, message_to_room=self._data.messages['GETOTH'].format(
            self.players[uid].name, item_to_get.long))

        self.handle_messages(uid, self._data.messages['YOUTAK'].format(item_to_get.long))

    def _handle_give_gold(self, uid, player_to, amt_from):
        """
        give an item to another player
        """
        pid = self._info.get_pid_by_name(self.players, player_to)
        print(pid)

        if pid == uid:
            self.handle_messages(uid, self._data.messages['NOGSLF'])
            return

        players_here = self._info.get_players_here(uid, self.players[uid].room, self.players)
        if not [x for x in players_here if x.lower() == player_to.lower()]:
            self.handle_messages(uid, self._data.messages['ARNNHR'].format(player_to))
            return

        if pid is None:
            self.handle_messages(uid, self._data.messages['ARNNHR'].format(player_to.capitalize()))
            return

        if amt_from <= 0:
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return

        if amt_from > self.players[uid].gold:
            self.handle_messages(uid, self._data.messages['DNTHVG'])
            return

        print(self.players[pid].enc, int(amt_from * 0.2), self.players[pid].max_enc)
        if self._info.get_enc(self.players[pid], self.items) + int(amt_from * 0.2) > self.players[pid].max_enc:
            self.handle_messages(
                uid, self._data.messages['CNTGGP'].format(self.players[pid].name))
            return

        self.players[uid].gold -= amt_from
        self.players[pid].gold += amt_from

        self.handle_messages(uid, self._data.messages['YOUGVG'].format(amt_from, self.players[pid].name))
        self.handle_messages(
            uid, tid=pid, message_to_target=self._data.messages['YOUGTG'].format(self.players[uid].name, amt_from))
        self.handle_messages(
            uid, tid=pid, message_to_room=self._data.messages['JSTGVG'].format(self.players[uid].name, self.players[pid].name))

    def _process_light_command(self, uid, command, params):
        """
        light a torch
        """
        item_to_light = None

        if not params:
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return

        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_to_light = self.items[item]
                break

        if not item_to_light:
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return

        if not item_to_light.equip_sub_type == 'light':
            self.handle_messages(uid, self._data.messages['NOTLIT'])
            return

        if item_to_light.is_activated:
            self.handle_messages(uid, self._data.messages['ALRLIT'])
            return

        item_to_light.is_activated = True
        item_to_light.effect_ticker = time.time()

        self.handle_messages(uid, self._data.messages['YOULIT'].format(item_to_light.type))
        self.handle_messages(
            uid,
            message_to_room=self._data.messages['OTHLIT'].format(self.players[uid].name, item_to_light.type)
        )

        self._process_look_command(uid)

    def _handle_give_item(self, uid, player_to, item_from):
        """
        give an item to another player
        """
        item_to_give = None
        index_of_item = None
        for index, item in enumerate(self.players[uid].inventory):
            if item_from in self.items[item].type:
                item_to_give = self.items[item]
                index_of_item = item
                break

        if not item_to_give:
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return

        pid = self._info.get_pid_by_name(self.players, player_to)
        print(pid)

        if pid == uid:
            self.handle_messages(uid, self._data.messages['NOGSLF'])
            return

        players_here = self._info.get_players_here(uid, self.players[uid].room, self.players)

        if not [x for x in players_here if x.lower() == player_to.lower()]:
            self.handle_messages(uid, self._data.messages['ARNNHR'].format(player_to))
            return

        if len(self.players[pid].inventory) >= 8:
            self.handle_messages(uid, self._data.messages['CNTGIV'].format(self.players[pid].name))
            self.handle_messages(uid, tid=pid, message_to_target=self._data.messages['TRDGIV'].format(self.players[pid].name, item_to_give.type))
            self.handle_messages(uid, tid=pid, message_to_room=self._data.messages['DNTGIV'].format(self.players[uid].name, self.players[pid].name))
            return

        if self._info.get_enc(self.players[pid], self.items) + item_to_give.weight >= self.players[pid].max_enc:
            self.handle_messages(uid, self._data.messages['CNTHDL'].format(self.players[pid].name))
            self.handle_messages(uid, tid=pid, message_to_target=self._data.messages['UCNHDL'].format(self.players[pid].name, item_to_give.type))
            self.handle_messages(uid, tid=pid, message_to_room=self._data.messages['DNTGIV'].format(self.players[uid].name, self.players[pid].name))
            return

        self.players[pid].inventory.append(index_of_item)
        self.players[uid].inventory.remove(index_of_item)

        print(uid, self.players[uid].name)
        print(pid, self.players[pid].name)

        print(uid, pid)

        message_to_room = self._data.messages['JSTGAV'].format(self.players[uid].name, player_to.capitalize())
        self.handle_messages(uid, tid=pid, message_to_room=message_to_room)

        message_to_target = self._data.messages['YOUGET'].format(self.players[uid].name, item_to_give.long)
        self.handle_messages(uid, tid=pid, message_to_target=message_to_target)

        message_to_player = self._data.messages['YOUGAV'].format(item_to_give.type, player_to.capitalize())
        self.handle_messages(uid, message_to_player=message_to_player)

    def _process_give_command(self, uid, command, params):
        """
        give something

        give <player> <item>
        give <player> <amt> gold

        """

        if len(params.split()) == 1:
            self._process_say_command(uid, command, params)
            return
        elif len(params.split()) == 2:
            player_to, item_from = params.split()
            self._handle_give_item(uid, player_to, item_from)
        elif len(params.split()) == 3:
            player_to, amt_from, gold = params.split()
            if gold == 'gold' and amt_from.isnumeric():
                self._handle_give_gold(uid, player_to, int(amt_from))
                return
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return
        else:
            self._process_say_command(uid, command, params)

        return

    def _process_drop_command(self, uid, params):
        """
        drop something
        """
        room = self._area.get_cur_room(self.players[uid].room)

        item_to_drop = None
        index_of_item = None
        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_to_drop = self.items[item]
                index_of_item = item
                break

        if not item_to_drop:
            self.handle_messages(uid, self._data.messages['DNTHAV'])
            return

        if room.is_town():
            self.handle_messages(uid, self._data.messages['NODHER'])
            return

        if len(room.items) >= 8:
            self.handle_messages(uid, self._data.messages['NDPITM'])
            return

        room.items.append(index_of_item)
        self.players[uid].inventory.remove(index_of_item)
        z, x, y = self.players[uid].room
        print(self._area.grid[z][x][y].items)

        # go through all the players in the game
        self.handle_messages(uid, message_to_room=self._data.messages['DRPOTH'].format(self.players[uid].name, item_to_drop.long))

        self.handle_messages(uid, self._data.messages['DRPITM'].format(item_to_drop.type))

    def _handle_drink_potion(self, uid, item_to_drink, index_of_item):
        """
        drink a potion
        """
        if item_to_drink.equip_sub_type == 'heal':
            boost = randint(item_to_drink.min_value_range, item_to_drink.max_value_range)
            if (self.players[uid].vit + boost) > self.players[uid].vit_max:
                self.players[uid].vit = self.players[uid].vit_max
            else:
                self.players[uid].vit += boost

        elif item_to_drink.equip_sub_type == 'cure poison':
            self.players[uid].status = Status.Healthy

        elif item_to_drink.equip_sub_type == 'minor mana boost':
            self.players[uid].man = self.players[uid].man_max

        elif item_to_drink.equip_sub_type == 'strength boost':
            if self.players[uid].str_boo > 0:
                self.handle_messages(uid, "Nothing happens!")
                return

            boost = randint(10, item_to_drink.min_value_range)
            print(self.players[uid].str + boost,  self.players[uid].max_stat, self.players[uid].max_stat - self.players[uid].str)
            if self.players[uid].str + boost > self.players[uid].max_stat:
                self.players[uid].str_boo = self.players[uid].max_stat - self.players[uid].str
            else:
                self.players[uid].str_boo = boost
            self.players[uid].str_ticker = time.time()

        elif item_to_drink.equip_sub_type == 'dexterity boost':
            if self.players[uid].dex_boo > 0:
                self.handle_messages(uid, "Nothing happens!")
                return

            boost = randint(10, item_to_drink.min_value_range)
            if self.players[uid].dex + boost > self.players[uid].max_stat:
                self.players[uid].dex_boo = self.players[uid].max_stat - self.players[uid].dex
            else:
                self.players[uid].dex_boo = boost
            self.players[uid].dex_ticker = time.time()

        elif item_to_drink.equip_sub_type == 'invisibility':
            self.players[uid].is_invisible = True
            self.players[uid].invisibility_ticker = time.time()

        self.items.pop(index_of_item)
        self.players[uid].inventory.remove(index_of_item)
        self.handle_messages(uid, f"You feel somehow different after drinking {item_to_drink.long}.")
        self.handle_messages(uid, message_to_room=f"{self.players[uid].name} just took a drink of something.")

        return

    def _process_drink_command(self, uid, command, params):
        """
        eat something
        """
        item_to_drink = None
        index_of_item = None
        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_to_drink = self.items[item]
                index_of_item = item

        if not item_to_drink:
            self.handle_messages(uid, "Sorry, you don't seem to have any.")
            return

        if not isinstance(item_to_drink, Equipment):
            self.handle_messages(uid, "Sorry, you can't drink that.")
            return

        if item_to_drink.equip_type == 'potion':
            self._handle_drink_potion(uid, item_to_drink, index_of_item)
            return

        if item_to_drink.equip_sub_type != 'water':
            self.handle_messages(uid, "Sorry, you can't drink that.")
            return

        self.handle_messages(uid, "The water quenches your thirst.")
        self.handle_messages(
            uid,
            message_to_room=f"{self.players[uid].name} just took a drink from {item_to_drink.long}.")

        # it's food, eat it
        self.players[uid].thirst_ticker = time.time()
        self.players[uid].status = Status.Healthy
        self.items.pop(index_of_item)
        self.players[uid].inventory.remove(index_of_item)

    def _process_eat_command(self, uid, command, params):
        """
        eat something
        """
        item_to_eat = None
        index_of_item = None
        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_to_eat = self.items[item]
                index_of_item= item

        if not item_to_eat:
            self.handle_messages(uid, "Sorry, you don't seem to have any.")
            return

        if not isinstance(item_to_eat, Equipment):
            self.handle_messages(uid, "Sorry, you can't eat that.")
            return

        if item_to_eat.equip_sub_type != 'food':
            self.handle_messages(uid, "Sorry, you can't eat that.")
            return

        self.handle_messages(uid, "You feel much better after eating a meal.")
        self.handle_messages(
            uid,
            message_to_room=f"{self.players[uid].name} just ate {item_to_eat.long}.")

        # it's food, eat it
        self.players[uid].hunger_ticker = time.time()
        self.players[uid].status = Status.Healthy
        self.items.pop(index_of_item)
        self.players[uid].inventory.remove(index_of_item)

    def _process_sell_command(self, uid, command, params):
        """
        sell something
        """
        room_is_shop = self._info.room_is_shop(self.players[uid])

        if not room_is_shop:
            self._process_say_command(uid, command, params)
            return

        items_in_shop = self._info.get_item_list(room_is_shop)
        item_for_sale = None
        index_of_item = None
        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_for_sale = self.items[item]
                index_of_item = item

        if not item_for_sale:
            self.handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        shop_is_interested = False
        for item_in_shop in items_in_shop:
            if item_for_sale.type == item_in_shop.type:
                shop_is_interested = True
                break

        if not shop_is_interested:
            self.handle_messages(uid, "Sorry, the shopkeeper doesn't want that.")
            return

        proceeds = -(-item_for_sale.value // 2)   # round up!

        # go through all the players in the game
        self.handle_messages(uid, "{} sold {}.".format(
            self.players[uid].name, item_for_sale.long))

        self.handle_messages(uid, "You sold {} for {} gold.".format(
            item_for_sale.long, proceeds))

        print(self.players[uid].inventory)
        print(index_of_item)

        # give player money and remove item from game
        self.players[uid].gold += proceeds
        self.players[uid].inventory.remove(index_of_item)
        self.items.pop(index_of_item)

        print(self.items)
        print(self.players[uid].inventory)

    def _process_health_command(self, uid):
        """
        get new stats
        """
        self.handle_messages(uid, f"{'Hit Points:':15}{self.players[uid].vit} / {self.players[uid].vit_max}")
        self.handle_messages(uid, f"{'Mana:':15}{self.players[uid].man} / {self.players[uid].man_max}")
        self.handle_messages(uid, f"{'Status:':15}{self.players[uid].status.name}")

    def _process_equip_command(self, uid, params):
        """
        get new stats
        """
        item_to_equip = None
        index_of_item = 0
        equipped = False

        for index, item in enumerate(self.players[uid].inventory):
            if params in self.items[item].type:
                item_to_equip = self.items[item]
                index_of_item = item

        if not item_to_equip:
            self.handle_messages(uid, "Sorry, you don't seem to have that.")
            return

        if not item_to_equip.can_use(self.players[uid]):
            self.handle_messages(uid, "Sorry, you can't equip that.")
            return

        if self.players[uid].level < item_to_equip.level:
            self.handle_messages(uid, "You're not a high enough level to equip that.")
            return

        print(type(item_to_equip))

        if isinstance(item_to_equip, Armor):
            print("armor", item_to_equip.type)
            print(self.players[uid].armor)

            # unequip first
            self.players[uid].inventory.append(self.players[uid].armor)
            old_item = self.players[uid].armor

            # equip new weapon
            self.players[uid].inventory.remove(index_of_item)
            self.items[self._next_item] = item_to_equip
            self.players[uid].armor = self._next_item
            self._next_item += 1
            equipped = True

        elif isinstance(item_to_equip, Weapon):
            print("weapon", item_to_equip.type)
            print(self.players[uid].weapon)

            # unequip first
            self.players[uid].inventory.append(self.players[uid].weapon)
            old_item = self.players[uid].weapon

            # equip new weapon
            self.players[uid].inventory.remove(index_of_item)
            self.items[self._next_item] = item_to_equip
            self.players[uid].weapon = self._next_item
            self._next_item += 1
            equipped = True

        if not equipped:
            return

        # go through all the players in the game
        self.handle_messages(uid, message_to_room="{} just equipped {}.".format(
            self.players[uid].name, item_to_equip.long))

        self.handle_messages(uid, "You just equipped {} and removed {}.".format(
            item_to_equip.long, self.items[old_item].long))

    def _process_experience_command(self, uid):
        """
        get new stats
        """
        self.handle_messages(uid, f"{'Level:':15}{self.players[uid].level}")
        self.handle_messages(uid, f"{'Experience:':15}{self.players[uid].experience}")
        self.handle_messages(uid, f"{'Rune':15}{'None'}")

    def _process_inventory_command(self, uid):
        """
        get new stats
        """
        inventory = []
        for item in self.players[uid].inventory:
            inventory.append(self.items[item].long)

        if not inventory:
            self.handle_messages(uid, f"You are carrying {self.players[uid].gold} gold coins.")
            return

        msg = f"You are carrying {self.players[uid].gold} gold coins "

        if len(inventory) == 1:
            msg += "and {}.".format(inventory[0])
        elif len(inventory) == 2:
            msg += "{} and {}.".format(inventory[0], inventory[1])
        else:
            msg += "{} and {}.".format(", ".join(inventory[:-1]), inventory[-1])

        self.handle_messages(uid, msg)

    def _process_list_items_command(self, uid):
        """
        list items in shops you can buy
        """
        room_is_shop = self._info.room_is_shop(self.players[uid])

        if not room_is_shop:
            return

        items = self._info.get_item_list(room_is_shop)

        self.handle_messages(uid, "")
        self.handle_messages(uid, "+======================+======+==+")
        self.handle_messages(uid, "| Item                 |   Price |")
        self.handle_messages(uid, "+----------------------+---------+")

        for item in sorted(items, key=lambda x: x.value):
            self.handle_messages(
                uid, (
                    f"| {item.type:21}"
                    f"| {item.value:7} |"
                )
            )

        self.handle_messages(uid, "+======================+=========+")

        self.handle_messages(uid, message_to_room="{} is browsing the wares.".format(
            self.players[uid].name))

    def _process_players_command(self, uid):
        """
        list players currently in the game
        """

        players = self._info.get_current_players(self.players)

        if not players:
            return

        if len(players) == 1:
            self.handle_messages(uid, "{} is playing.".format(players[0]))
        elif len(players) == 2:
            self.handle_messages(uid, "{} and {} are playing.".format(players[0], players[1]))
        else:
            self.handle_messages(uid, "{} and {} are playing.".format(", ".join(players[:-1]), players[-1]))

    def _process_quit_command(self, uid):
        """
        exit on your own terms
        """
        self.handle_messages(uid, "Goodbye, {}.".format(
            self.players[uid].name))
        self._mud.get_disconnect(uid)

    def _process_ring_command(self, uid):
        """
        exit on your own terms
        """
        self._gong.ring(uid)

    def _process_attack_command(self, uid, command, params):
        """
        exit on your own terms
        """
        room = self._area.get_cur_room(self.players[uid].room)
        location = self.players[uid].room
        print(location)
        print(room.mobs)
        if room.is_safe():
            self.handle_messages(uid, self._messages['NOFTHR'])
            print("room is safe, no attacking here")
            return

        if self.players[uid].resting:
            self.handle_messages(uid, self._messages['ATTEXH'])
            print("player is resting")
            return

        target = self._info.get_target(params, room.mobs, self.mobs)
        if not target:
            self.handle_messages(uid, self._messages['ARNNHR'].format(params))
            print(f"sorry {params} isn't here")
            return

        message_to_player, message_to_room, message_to_target = (
            self._combat.player_melee_attack(self.players[uid], target, self.items, self.mob_items))

        self.handle_messages(uid, message_to_player=message_to_player)
        self.handle_messages(uid, message_to_room=message_to_room)
        print(room.mobs)
        self._info.check_and_handle_kill(self.players[uid], target, room.mobs, self.mobs)
        print(room.mobs)
        print("attack!")

    def _process_go_command(self, uid, command):
        """ move around """

        command = command[:1].lower()

        # get current room and list of exits
        cur_exits = self._area.get_cur_exits(self.players[uid].room)

        if self.players[uid].resting:
            self.handle_messages(uid, self._data.messages['CNTMOV'])
            return

        if command not in cur_exits:
            self.handle_messages(uid, "You can't go that way!")
            return

        cur_player_room = self.players[uid].room
        next_player_room = self._area.get_next_room(cur_player_room, command)

        print(cur_player_room)

        # tell people you're leaving
        self.handle_messages(uid, message_to_room="{} just left to the {}.".format(
            self.players[uid].name, self._area.exits[command]))

        # move player to next room
        self.players[uid].room = next_player_room

        # tell people you've arrived
        self.handle_messages(uid, message_to_room="{} just arrived from the {}.".format(
            self.players[uid].name, self._area.exits[command]))

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
            self.players[pid] = None

            # send the new player a prompt for their name
            self._mud.send_message(pid, "What is your name?")

    def check_for_disconnected_players(self):
        """
        check to see if anyone disconnected since last update
        """
        for uid in self._mud.get_disconnected_players():
            print("disconnected ", uid)
            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self.players:
                continue

            # go through all the players in the game
            self.handle_messages(uid, global_message="{} quit the game".format(
                self.players[uid].name))

            # remove the player's entry in the player dictionary
            del self.players[uid]

    def check_for_new_commands(self):
        """
        check to see if any new commands are on the queue
        """
        for uid, command, params in self._mud.get_commands():

            # if for any reason the player isn't in the player map, skip them
            # move on to the next one
            if uid not in self.players:
                continue

            # if the player hasn't given their name yet, use this first command
            # their name and move them to the starting room.
            if self.players[uid] is None:
                if command.capitalize() in self.state:
                    if self.state[command.capitalize()] in self.players.values():
                        print(f"panic player {command.capitalize()} is already playing")
                        self._mud.get_disconnect(uid)
                        del self.players[uid]
                        continue
                    self.players[uid] = self.state[command.capitalize()]
                    self.handle_messages(uid, f"Welcome back {self.players[uid].name}.")
                    self._process_look_command(uid)
                    print("state ", self.state)
                    print("players ", self.players)
                    continue

                self.players[uid] = Player()
                self.players[uid].name = command.capitalize()
                self.state[self.players[uid].name] = self.players[uid]

                self.handle_messages(uid, "")
                self.handle_messages(uid, "+==========+============+")
                self.handle_messages(uid, "| Num      | Species    |")
                self.handle_messages(uid, "+----------+------------+")
                for num, species in self._species.items():
                    self.handle_messages(
                        uid, (
                            f"| {num:<9}"
                            f"| {species['type']:11}|"
                        )
                    )
                self.handle_messages(uid, "+==========+============+")
                self.handle_messages(uid, "")
                self.handle_messages(uid, "What species are you?")

            elif self.players[uid].species is None:

                self.players[uid].species = int(command)

                self.handle_messages(uid, "")
                self.handle_messages(uid, "+==========+============+")
                self.handle_messages(uid, "| Num      | Class      |")
                self.handle_messages(uid, "+----------+------------+")
                for num, classes in self._classes.items():
                    self.handle_messages(
                        uid, (
                            f"| {num:<9}"
                            f"| {classes['type']:11}|"
                        )
                    )
                self.handle_messages(uid, "+==========+============+")
                self.handle_messages(uid, "")
                self.handle_messages(uid, "What class are you?")

            elif self.players[uid].p_class is None:

                self.players[uid].p_class = int(command)
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

            # 'light' command
            elif command == "light" or command == "li":
                self._process_light_command(uid, command, params)

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

            # 'drink' command
            elif command == "drink":
                if not params:
                    self._process_say_command(uid, command, params)
                else:
                    self._process_drink_command(uid, command, params)

            # 'eat' command
            elif command == "eat":
                if not params:
                    self._process_say_command(uid, command, params)
                else:
                    self._process_eat_command(uid, command, params)

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

            # 'attack' command
            elif command == "attack" or command == "a":
                if params:
                    self._process_attack_command(uid, command, params)
                else:
                    self._process_say_command(uid, command, params)

            # 'sell' if params otherwise 'go'
            elif command == "s":
                if not params:
                    self._process_go_command(uid, command)
                else:
                    self._process_sell_command(uid, command, params)

            # 'drop' if params otherwise 'go'
            elif command == "d":
                if not params:
                    self._process_go_command(uid, command)
                else:
                    self._process_drop_command(uid, params)

            elif command == "ring" or command == "ri":
                if not params:
                    self._process_say_command(uid, command, params)
                elif params == "gong" or params == "g":
                    self._process_ring_command(uid)
                else:
                    self._process_say_command(uid, command, params)

            # 'quit' command
            elif command == "quit":
                self._process_quit_command(uid)

            # everything else assume player is talking
            else:
                self._process_say_command(uid, command, params)

    def save_state(self):
        """
        pickle stuff to disk
        """
        with open('/tmp/players.pkl', "wb") as file:
            pickle.dump(self.state, file)

        with open('/tmp/items.pkl', 'wb') as file:
            pickle.dump(self.items, file)


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

    game.save_state()


def _initialize_lairs(game):
    """
    populate lairs for the first time
    """
    for z, level in enumerate(game.grid):
        for x, row in enumerate(level):
            for y, cnum in enumerate(row):
                if game.grid[z][x][y].lair:
                    for index, mob in enumerate(game.grid[z][x][y].mob_types):
                        game.mobs[game.next_mob] = Mob(mob, game)
                        game.mobs[game.next_mob].room = [z, x, y]
                        game.mobs[game.next_mob].mid = game.next_mob
                        game.grid[z][x][y].mobs.append(game.next_mob)
                        game.next_mob += 1
                    print(f"({z}, {x}, {y})", game.grid[z][x][y].mobs)

    print([y.name for x, y in game.mobs.items()])


def _initialize_jobs(mud, players, items):
    """ run some background tasks """
    job_defaults = {
        'coalesce': True
    }
    scheduler = BackgroundScheduler()
    scheduler.configure(job_defaults=job_defaults, timezone='UTC')

    game = Game(mud, players, items)
    _initialize_lairs(game)
    sustenance = Sustenance(game)
    regenerate = Regenerate(game)
    slow_status = SlowStatus(game)
    item_effect = ItemEffect(game)
    mob_activity = MobActivity(game)
    repopulate_lairs = RepopulateLairs(game)

    rest = Rest(game)

    scheduler.add_job(
        _game_loop,
        'interval',
        seconds=0.2,
        args=[mud, game],
        id='game_loop'
    )
    scheduler.add_job(
        regenerate.execute,
        'interval',
        seconds=15,
        id='regenerate',
    )
    scheduler.add_job(
        slow_status.execute,
        'interval',
        seconds=15,
        id='slow_status',
    )
    scheduler.add_job(
        item_effect.execute,
        'interval',
        seconds=15,
        id='item_effect',
    )
    scheduler.add_job(
        sustenance.execute,
        'interval',
        seconds=15,
        id='sustenance',
    )
    scheduler.add_job(
        mob_activity.execute,
        'interval',
        seconds=3,
        id='mob_activity',
    )
    scheduler.add_job(
        rest.execute,
        'interval',
        seconds=1,
        id='rest',
    )
    scheduler.add_job(
        repopulate_lairs.execute,
        'interval',
        seconds=10,
        id='repopulate_lairs',
    )

    print("jobs started, ready for player one")
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


def _load_state():
    """
    read state from disk
    """
    players = {}
    items = {}
    try:
        with open("/tmp/players.pkl", "rb") as file:
            players = pickle.load(file)
    except Exception as ex:
        print(ex)

    try:
        with open('/tmp/items.pkl', 'rb') as file:
            items = pickle.load(file)
    except Exception as ex:
        print(ex)

    return players, items


def main():
    """
    function main
    args: none
    returns: none
    """
    players, items = _load_state()

    # start the server
    mud = Mud()

    # schedule the game jobs
    _initialize_jobs(mud, players, items)


if __name__ == '__main__':
    sys.exit(main())
