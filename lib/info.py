""" info class """
import yaml


class Info:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):
        """ read in the config files """

    @staticmethod
    def get_current_players(players):
        """
        get formatted list of players
        """
        _players = []
        for _, player in players.items():
            _players.append(player.name)

        return _players

    @staticmethod
    def get_players_here(uid, location, players):
        """
        get list of who else is here
        """
        _players_here = []
        for pid, player in players.items():
            # if they're in the same room as the player
            if player.room == location and \
                    pid != uid:
                # ... and they have a name to be shown
                if player.name is not None:
                    # add their name to the list
                    _players_here.append(player.name)

        return _players_here

    @staticmethod
    def get_pid_by_name(players, player_name):
        """ lookup player pid by name """
        for pid, player in players.items():
            # if they're in the same room as the player
            if player.name.lower() == player_name.lower():
                return pid

        return None

    def can_see(self, uid, location, players, player_name):
        """
        get list of who else is here
        """
        _players_here = self.get_players_here(uid, location, players)
        for pid, player in players.items():
            # if they're in the same room as the player
            if player.room == location and \
                    pid != uid:
                # ... and they have a name to be shown
                if player.name is not None:
                    # add their name to the list
                    _players_here.append(pid)

        return _players_here

    @staticmethod
    def get_species():
        """ read species from conf """
        with open("conf/species.yaml", "rb") as stream:
            try:
                _species = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _species

    @staticmethod
    def get_classes():
        """ read classes from conf"""
        with open("conf/classes.yaml", "rb") as stream:
            try:
                _classes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _classes

    @staticmethod
    def get_stat_ranges():
        """ read classes from conf"""
        with open("conf/stat_ranges.yaml", "rb") as stream:
            try:
                _stat_ranges = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _stat_ranges
