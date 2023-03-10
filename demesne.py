#!/usr/bin/python3

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

author: Mark Frimston - mfrimston@gmail.com
modified by: Jeff Brown - jeffbr@gmail.com
"""

import sys
import time

# import library objects
from lib.room import Room
from lib.dungeon import Dungeon
from lib.info import Info
from lib.player import Player

# import the MUD server class
from server.mud import Mud


class Game:
    """
    This class contains all the functions to allow the game to operate
    """

    def __init__(self, mud):
        # start the server
        self._room = Room()
        self._dungeon = Dungeon()
        self._grid = self._dungeon.grid  # town
        self._rooms = self._room.rooms
        self._mud = mud
        self._players = {}
        self._monsters = {}
        self._info = Info()
        self._tick = 6  # 6 seconds
        self._species = self._info.get_species()
        self._classes = self._info.get_classes()

        # counter for assigning each client a new id
        self._nextid = 0

    def _process_look_command(self, uid, command=None, params=None, loc=None):
        """
        write out the room and any players or items in it
        """

        if not loc:
            loc = self._players[uid].room

        print("loc", loc)
        room = self._room.get_cur_room(loc)
        exits = self._room.get_cur_exits(loc)
        cur_room = self._rooms[loc[0]][room]

        print("room", room)
        print("cur_room", cur_room)
        print("player", self._players[uid].name)

        players_here = self._info.get_players_here(uid, loc, self._players)

        if command and not params:
            self._mud.send_message(uid, cur_room["long"])
            for pid, _ in self._players.items():
                if pid != uid:
                    self._mud.send_message(pid, "{} is looking at around.".format(
                        self._players[uid].name))
            return

        if params:
            if self._room.is_exit(params):
                if params[0] in exits:
                    print(self._room.get_next_room(loc, params[0]))
                    self._process_look_command(uid, loc=self._room.get_next_room(loc, params[0]))
                else:
                    self._mud.send_message(uid, "You can't see anything in that direction!")
                return

            if self._players[uid].name.lower() == params.lower():
                self._mud.send_message(uid, "You can't look at yourself!")
                return

            if [x for x in players_here if x.lower() == params.lower()]:
                pid = self._info.get_pid_by_name(self._players, params)
                self._mud.send_message(uid, "You see {}. They are a {} {}.".format(
                    self._players[pid].name,
                    self._players[pid].get_species(),
                    self._players[pid].get_class()
                ))
                for pid, player in self._players.items():
                    if player.name.lower() == params.lower():
                        self._mud.send_message(pid, "{} is looking at you!".format(
                            self._players[uid].name))
                    elif pid != uid:
                        self._mud.send_message(pid, "{} is looking at {}.".format(
                            self._players[uid].name, params.capitalize()))
            else:
                self._mud.send_message(uid, "You don't see {} nearby.".format(params.capitalize()))
            return

        # send player a message containing the list of players in the room
        self._mud.send_message(uid, cur_room["short"])

        if len(players_here) == 0:
            self._mud.send_message(uid, "There is nobody here.")
        elif len(players_here) == 1:
            self._mud.send_message(uid, "{} is here with you.".format(players_here[0]))
        elif len(players_here) == 2:
            self._mud.send_message(uid, "{} and {} are here with you.".format(players_here[0], players_here[1]))
        else:
            self._mud.send_message(uid, "{} and {} are here with you.".format(", ".join(players_here[:-1]), players_here[-1]))

        self._mud.send_message(uid, "There is nothing on the floor.")

    def _process_help_command(self, uid, command, params):
        """
        write out the room and any players or items in it
        """
        if params == "info":
            self._mud.send_message(uid, """
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
        self._mud.send_message(uid, "Commands:")
        self._mud.send_message(
            uid, "  say <message>  - Says something out loud.")
        self._mud.send_message(
            uid, "  look           - Examines the surroundings")
        self._mud.send_message(
            uid, "  go <exit>      - Moves through the exit specified.")
        self._mud.send_message(
            uid, "  quit           - Quits the game.")

    def _process_new_player(self, uid):
        """
        add a new players name to the dictionary and stick them in a room
        """
        self._players[uid].set_base_stats()

        # go through all the players in the game
        for pid, _ in self._players.items():
            # send each player a message to tell them about the new player
            if pid != uid:
                self._mud.send_message(pid, "{} entered the game".format(
                    self._players[uid].name))

        # send the new player a welcome message
        self._mud.send_message(uid, "Welcome to the game, {}. ".format(
            self._players[uid].name))

        # send the new player the description of their current room
        self._process_look_command(uid)

    def _process_say_command(self, uid, command, params):
        """
        say stuff to other folks
        """
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player.room == self._players[uid].room \
                    and pid != uid:
                # send them a message telling them what the player said
                self._mud.send_message(
                    pid, (
                        "{} says: {}".format(
                            self._players[uid].name,
                            " ".join([command, params])
                        )
                    )
                )
                self._mud.send_message(uid, "--- Message Sent ---")

                return True

        self._mud.send_message(
            uid, "Sorry, that is not an appropriate command.")

        return False

    def _process_exits_command(self, uid):
        """
        list players currently in the game
        """
        exits = [self._room.exits[x] for x in self._room.get_cur_exits(self._players[uid].room)]
        if len(exits) == 0:
            self._mud.send_message(uid, "There are no exits.")
        elif len(exits) == 1:
            self._mud.send_message(uid, "There is an exit to the {}.".format(exits[0]))
        elif len(exits) == 2:
            self._mud.send_message(uid, "There are exits to the {} and {}.".format(exits[0], exits[1]))
        else:
            self._mud.send_message(uid, "There are exits to the {} and {}.".format(", ".join(exits[:-1]),
                                                                              exits[-1]))
        return

    def _process_players_command(self, uid):
        """
        list players currently in the game
        """

        players = self._info.get_current_players(self._players)

        if not players:
            return

        if len(players) == 1:
            self._mud.send_message(uid, "{} is playing.".format(players[0]))
        elif len(players) == 2:
            self._mud.send_message(uid, "{} and {} are playing.".format(players[0], players[1]))
        else:
            self._mud.send_message(uid, "{} and {} are playing.".format(", ".join(players[:-1]), players[-1]))

    def _process_quit_command(self, uid):
        """
        exit on your own terms
        """
        self._mud.send_message(uid, "Goodbye, {}.".format(
            self._players[uid].name))
        self._mud.get_disconnect(uid)

    def _process_go_command(self, uid, command):
        """ move around """

        command = command[:1].lower()

        # get current room and list of exits
        cur_exits = self._room.get_cur_exits(self._players[uid].room)

        if command not in cur_exits:
            self._mud.send_message(uid, "You can't go that way!")
            return

        cur_player_room = self._players[uid].room
        next_player_room = self._room.get_next_room(cur_player_room, command)

        next_room_num = self._room.get_cur_room(next_player_room)
        next_room = self._rooms[next_player_room[0]][next_room_num]
        print("next_player_room", next_player_room)
        print("next_room_num", next_room_num)
        print("next_room", next_room)

        # tell people you're leaving
        for pid, player in self._players.items():
            if player.room == self._players[uid].room \
                    and pid != uid:
                self._mud.send_message(
                    pid, "{} just left to the {}.".format(
                        self._players[uid].name, self._room.exits[command]))

        # move player to next room
        self._players[uid].room = next_player_room

        # tell people you've arrived
        for pid, player in self._players.items():
            if player.room == self._players[uid].room \
                    and pid != uid:
                self._mud.send_message(
                    pid, "{} just arrived from the {}.".format(
                        self._players[uid].name, self._room.exits[command]))

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
            self._mud.send_message(pid, "What is your name?")

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
            for pid, _ in self._players.items():
                # send each player a message to tell them about the diconnected
                # player
                if pid != uid:
                    self._mud.send_message(pid, "{} quit the game".format(
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

                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "| Num      | Species    |")
                self._mud.send_message(uid, "+----------+------------+")
                for num, species in self._species.items():
                    self._mud.send_message(
                        uid, (
                            f"| {num:<9}"
                            f"| {species['type']:11}|"
                        )
                    )
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "What species are you?")

            elif self._players[uid].species is None:

                self._players[uid].species = int(command)

                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "| Num      | Class      |")
                self._mud.send_message(uid, "+----------+------------+")
                for num, classes in self._classes.items():
                    self._mud.send_message(
                        uid, (
                            f"| {num:<9}"
                            f"| {classes['type']:11}|"
                        )
                    )
                self._mud.send_message(uid, "+==========+============+")
                self._mud.send_message(uid, "")
                self._mud.send_message(uid, "What class are you?")

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
                "south", "s",
                "up", "u",
                "down", "d"
            ]:
                self._process_go_command(uid, command)

            # 'look' command
            elif command == "look" or command == "l":
                self._process_look_command(uid, command, params)

            # 'players' command
            elif command == "players" or command == "pl":
                self._process_players_command(uid)

            # 'exits' command
            elif command == "exits" or command == "ex":
                self._process_exits_command(uid)

            # 'inventory' command
            elif command == "inventory" or command == "i":
                self._process_inventory_command(uid, command, params)

            # 'status' command
            elif command == "status" or command == "st":
                self._process_status_command(uid, command, params)

            # 'health' command
            elif command == "health" or command == "he":
                self._process_health_command(uid, command, params)

            # 'experience' command
            elif command == "experience" or command == "ep":
                self._process_experience_command(uid, command, params)

            # 'spells' command
            elif command == "spells" or command == "sp":
                self._process_spells_command(uid, command, params)

            # 'quit' command
            elif command == "quit":
                self._process_quit_command(uid)

            # everything else assume player is talking
            else:
                self._process_say_command(uid, command, params)


def main():
    """
    function main
    args: none
    returns: none
    """

    # start the server
    mud = Mud()

    # create an instance of the game
    game = Game(mud)

    # main game loop. We loop forever (i.e. until the program is terminated)
    while True:

        # pause for 1/5 of a second on each loop, so that we don't constantly
        # use 100% CPU time
        time.sleep(0.2)

        # 'update' must be called in the loop to keep the game running and give
        # us up-to-date information
        mud.update()

        game.check_for_new_players()

        game.check_for_disconnected_players()

        game.check_for_new_commands()


if __name__ == '__main__':
    sys.exit(main())
