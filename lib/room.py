""" rooms class """
import yaml

from lib.dungeon import Dungeon


class Room:
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        with open("conf/t1.yaml", "rb") as stream:
            try:
                self._t1 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d1.yaml", "rb") as stream:
            try:
                self._d1 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d2.yaml", "rb") as stream:
            try:
                self._d2 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open("conf/d3.yaml", "rb") as stream:
            try:
                self._d3 = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.exits = {
            'e': 'east',
            'w': 'west',
            'n': 'north',
            's': 'south',
            'u': 'up',
            'd': 'down'
        }

        self.rooms = []

        dungeon = Dungeon()
        self._grid = dungeon.grid

        self._d0 = []
        self._d9 = []
        self._d0.append(self._t1[0])
        self._d9.append(self._t1[0])

        self.rooms.append(self._d0)
        self.rooms.append(self._t1)
        self.rooms.append(self._d1)
        self.rooms.append(self._d2)
        self.rooms.append(self._d3)
        self.rooms.append(self._d9)

    def get_cur_room(self, location):
        """ get the current room """
        z, x, y = location
        return self._grid[z][x][y]

    def get_cur_exits(self, location):
        """ get list of exits from current room """
        _exits = []

        z, x, y = location
        room = self._grid[z][x][y]
        print("current loc [{},{},{}] in {}.".format(
            z, x, y, self.rooms[z][room]["short"]))

        if self._grid[z][x - 1][y] > 0:
            _exits.append("n")
        if self._grid[z][x + 1][y] > 0:
            _exits.append("s")
        if self._grid[z][x][y + 1] > 0:
            _exits.append("e")
        if self._grid[z][x][y - 1] > 0:
            _exits.append("w")
        if self.rooms[z][room]["stairs"]:
            if self._grid[z + 1][x][y] > 0:
                _exits.append("d")
            if self._grid[z - 1][x][y] > 0:
                _exits.append("u")

        return _exits

    def get_next_room(self, location, direction):
        """ get next room given a location and a direction"""
        # get current room and list of exits
        cur_exits = self.get_cur_exits(location)

        cur_player_room = location
        next_player_room = cur_player_room.copy()

        # if the specified exit is found in the room's exits list
        if direction in cur_exits:
            # update the player's current room to the one the exit leads to
            if direction == "s":
                next_player_room[1] += 1
            if direction == "n":
                next_player_room[1] -= 1
            if direction == "e":
                next_player_room[2] += 1
            if direction == "w":
                next_player_room[2] -= 1
            if direction == "u":
                next_player_room[0] -= 1
            if direction == "d":
                next_player_room[0] += 1

        return next_player_room

    def is_exit(self, _exit):
        """ check to see if this is an exit command """
        _is_exit = False
        for short, long in self.exits.items():
            if short == _exit or long == _exit:
                _is_exit = True
                break

        return _is_exit

    @staticmethod
    def get_exit_text(exits):
        """ get the exit text """

        if not exits:
            message = "There are no visible exits."

        elif len(exits) == 1:
            message = f"The only visible exit is to the {exits[0]}."

        elif len(exits) == 2:
            message = f"There are visible exits to the {exits[0]} and {exits[1]}."

        else:
            message = f"There are visible exits to the {', '.join(exits[:-1])} and {exits[-1]}."

        return message
