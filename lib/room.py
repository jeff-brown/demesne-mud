""" rooms class """
import yaml


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

    def is_exit(self, exit):
        """ check to see if this is an exit command """
        _is_exit = False
        for short, long in self.exits.items():
            if short == exit or long == exit:
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
