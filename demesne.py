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
        self._info = Info(mud)
        self._tick = 6  # 6 seconds

        # counter for assigning each client a new id
        self._nextid = 0

    def _movement(self, coords):
        """
        return current room and possible exits
        """
        exits = []

        z_coord = coords[0]
        x_coord = coords[1]
        y_coord = coords[2]

        room = self._grid[z_coord][x_coord][y_coord]
        print("current loc [{},{},{}] in {}.".format(
            z_coord, x_coord, y_coord, self._rooms[z_coord][room]["short"]))
        if self._grid[z_coord][x_coord - 1][y_coord] > 0:
            exits.append("n")
        if self._grid[z_coord][x_coord + 1][y_coord] > 0:
            exits.append("s")
        if self._grid[z_coord][x_coord][y_coord + 1] > 0:
            exits.append("e")
        if self._grid[z_coord][x_coord][y_coord - 1] > 0:
            exits.append("w")
        if self._rooms[z_coord][room]["stairs"]:
            if self._grid[z_coord + 1][x_coord][y_coord] > 0:
                exits.append("d")
            if self._grid[z_coord - 1][x_coord][y_coord] > 0:
                exits.append("u")

        return room, exits

    def _process_look_command(self, uid, command=None, params=None, loc=None):
        """
        write out the room and any players or items in it
        """

        if not loc:
            loc = self._players[uid]["room"]

        print("loc", loc)
        room, _ = self._movement(loc)
        cur_room = self._rooms[loc[0]][room]

        print("room", room)
        print("cur_room", cur_room)
        print("player", self._players[uid]["name"])

        players_here = self._info.get_players_here(uid, loc, self._players)

        if command and not params:
            self._mud.send_message(uid, cur_room["long"])
            for pid, _ in self._players.items():
                if pid != uid:
                    self._mud.send_message(pid, "{} is looking at around.".format(
                        self._players[uid]["name"]))
            return

        if params:
            if self._room.is_exit(params):
                self._mud.send_message(
                    uid, "You are looking to the {}.".format(self._room.exits[params[0]]))
                return

            if self._players[uid]["name"].lower() == params.lower():
                self._mud.send_message(uid, "You can't look at yourself!")
                return
            can_see = [x for x in players_here if x.lower() == params.lower()]
            if can_see:
                self._mud.send_message(uid, "You see {}.".format(can_see[0]))
                for pid, player in self._players.items():
                    if player["name"].lower() == params.lower():
                        self._mud.send_message(pid, "{} is looking at you!".format(
                            self._players[uid]["name"]))
                    elif pid != uid:
                        self._mud.send_message(pid, "{} is looking at {}.".format(
                            self._players[uid]["name"], params.capitalize()))
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
        self._players[uid]["room"] = [1, 4, 2]
        self._players[uid]["level"] = 1

        # go through all the players in the game
        for pid, _ in self._players.items():
            # send each player a message to tell them about the new player
            if pid != uid:
                self._mud.send_message(pid, "{} entered the game".format(
                    self._players[uid]["name"]))

        # send the new player a welcome message
        self._mud.send_message(uid, "Welcome to the game, {}. ".format(
            self._players[uid]["name"]))
        print(self._players)
        # send the new player the description of their current room
        self._process_look_command(uid)

    def _process_say_command(self, uid, command, params):
        """
        say stuff to other folks
        """
        for pid, player in self._players.items():
            # if they're in the same room as the player
            if player["room"] == self._players[uid]["room"] \
                    and pid != uid:
                # send them a message telling them what the player said
                self._mud.send_message(
                    pid, (
                        "{} says: {}".format(
                            self._players[uid]["name"],
                            " ".join([command, params])
                        )
                    )
                )
                self._mud.send_message(uid, "--- Message Sent ---")

                return True

        self._mud.send_message(
            uid, "Sorry, that is not an appropriate command.")

        return False

    def _process_players_command(self, uid, command, params):
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
            self._players[uid]["name"]))
        self._mud.get_disconnect(uid)

    def _process_go_command(self, uid, command):
        """ move around """

        command = command[:1].lower()

        # get current room and list of exits
        cur_room_num, cur_exits = self._movement(self._players[uid]["room"])

        cur_room = self._rooms[self._players[uid]["room"][0]][cur_room_num]
        cur_player_room = self._players[uid]["room"]
        next_player_room = cur_player_room.copy()

        # if the specified exit is found in the room's exits list
        if command in cur_exits:
            print("_process_go_command:cur_room", cur_room)
            print("next_player_room", next_player_room)
            # update the player's current room to the one the exit leads to
            if command == "s":
                next_player_room[1] += 1
            if command == "n":
                next_player_room[1] -= 1
            if command == "e":
                next_player_room[2] += 1
            if command == "w":
                next_player_room[2] -= 1
            if command == "u":
                next_player_room[0] -= 1
            if command == "d":
                next_player_room[0] += 1

            next_room_num, _ = (
                self._movement(next_player_room)
            )
            next_room = self._rooms[next_player_room[0]][next_room_num]
            print("next_player_room", next_player_room)
            print("next_room_num", next_room_num)
            print("next_room", next_room)

            # go through all the players in the game
            for pid, player in self._players.items():
                # if player is in the same room and isn't the player
                # sending the command
                if player["room"] == self._players[uid]["room"] \
                        and pid != uid:
                    # send them a message telling them that the player
                    # left the room
                    self._mud.send_message(
                        pid, "{} just left to the {}.".format(
                            self._players[uid]["name"], self._room.exits[command]))

            # move player to next room
            self._players[uid]["room"] = next_player_room

            # go through all the players in the game
            for pid, player in self._players.items():
                # if player is in the same (new) room and isn't the player
                # sending the command
                if player["room"] == self._players[uid]["room"] \
                        and pid != uid:
                    # send them a message telling them that the player
                    # entered the room
                    self._mud.send_message(
                        pid, "{} just arrived from the {}.".format(
                            self._players[uid]["name"], self._room.exits[command]))

            # send the player a message telling them where they are now
            self._process_look_command(uid)

        # the specified exit wasn't found in the current room
        else:
            # send back an 'unknown exit' message
            self._mud.send_message(uid, "You can't go that way.")

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
            self._players[pid] = {
                "name": None,
                "room": None
            }

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
                        self._players[uid]["name"]))

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
            if self._players[uid]["name"] is None:

                self._players[uid]["name"] = command.capitalize()
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
                self._process_players_command(uid, command, params)

            # 'exits' command
            elif command == "exits" or command == "ex":
                self._process_exits_command(uid, command, params)

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