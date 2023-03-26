""" dungeon class """
from lib import data
from lib.chamber import Chamber


class Area:
    """
    This class contains all of the functions to allow the game to operate
    """

    def __init__(self):
        """ read in the config files """
        self.grid = []

        self.exits = {
            'e': 'east',
            'w': 'west',
            'n': 'north',
            's': 'south',
            'u': 'up',
            'd': 'down'
        }

        for vnum, _area in data.areas.items():
            self.grid.append(_area['grid'])

        for z, level in enumerate(self.grid):
            for x, row in enumerate(level):
                for y, cnum in enumerate(row):
                    self.grid[z][x][y] = Chamber(cnum)

    def get_cur_room(self, location):
        """ get the current room """
        z, x, y = location
        return self.grid[z][x][y]

    def get_cur_exits(self, location):
        """ get list of exits from current room """
        _exits = []

        z, x, y = location
        room = self.grid[z][x][y]

        if self.grid[z][x - 1][y].vnum > 0:
            _exits.append("n")
        if self.grid[z][x + 1][y].vnum > 0:
            _exits.append("s")
        if self.grid[z][x][y + 1].vnum > 0:
            _exits.append("e")
        if self.grid[z][x][y - 1].vnum > 0:
            _exits.append("w")
        if room.stairs:
            if self.grid[z + 1][x][y].vnum > 0:
                _exits.append("d")
            if self.grid[z - 1][x][y].vnum > 0:
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
