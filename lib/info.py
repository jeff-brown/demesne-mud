""" info class """
import json


class Info:
    """
    This class contains all the basic informational commands
    """

    def __init__(self, mud):
        """ read in the config files """

    def get_current_players(self, players):
        """
        get formatted list of players
        """
        _players = []
        for _, player in players.items():
            _players.append(player['name'])

        return _players

    def get_players_here(self, uid, location, players):
        """
        get list of who else is here
        """
        _players_here = []
        for pid, player in players.items():
            # if they're in the same room as the player
            if player["room"] == location and \
                    pid != uid:
                # ... and they have a name to be shown
                if player["name"] is not None:
                    # add their name to the list
                    _players_here.append(player["name"])

        return _players_here
