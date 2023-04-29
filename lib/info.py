""" info class """
from lib import data
from lib.room import Room
from lib.weapon import Weapon
from lib.armor import Armor
from lib.equipment import Equipment


class Info:
    """
    This class contains all the basic informational commands
    """

    def __init__(self):
        """ read in the config files

        cha_msg_1_limit=30
        cha_msg_2_limit=21
        cha_msg_3_limit=15
        cha_msg_4_limit=5

        CMSG1=stunningly attractive
        CMSG2=somewhat attractive
        CMSG3=rather plain looking

        phy_msg_1_limit=30
        phy_msg_2_limit=19
        phy_msg_3_limit=9

        PMSG1=and powerfully built {0} {1} {2}
        PMSG3=and slightly built {0} {1} {2}

        kno_msg_1_limit=30
        kno_msg_2_limit=19
        kno_msg_3_limit=8

        KMSG1=with a worldly air about {0}.
        KMSG2=with an inexperienced look about {0}.

        agi_msg_1_limit=30
        agi_msg_2_limit=19
        agi_msg_3_limit=9

        AMSG1=You notice that {0} movements are very quick and agile.
        AMSG2=You notice that {0} movements are rather slow and clumsy.

        int_msg_1_limit=30
        int_msg_2_limit=19
        int_msg_3_limit=8

        IMSG1={0} has a bright look in {1} eyes.
        IMSG2={0} has a dull look in {1} eyes.

        health_msg_1_percent=100
        health_msg_2_percent=75
        health_msg_3_percent=50
        health_msg_4_percent=25
        health_msg_5_percent=0

        HMSG1=and {0} is sorely wounded.
        HMSG2=and {0} seems to be moderately wounded.
        HMSG3=and {0} appears to be wounded.
        HMSG4=and looks as if {0} is lightly wounded.
        HMSG5=and {0} seems to be in good physical condition.

        Jeff is a stunningly attractive and moderately built halfling rouge,
        with a worldly air about them. You notice that their movements are very
        quick and agile. They have a bright look in their eyes. They are
        wearing robes, is armed with a dagger, and they seems to be in good
        physical condition..

        """
        print(f"init {__name__}")
        self._room = Room()
        self._rooms = self._room.rooms
        self._data = data
        self._max_encumbrance = [
            0,
            50, 100, 150, 200, 250, 300, 350, 400, 450, 500,
            550, 600, 650, 700, 750, 800, 850, 900, 950, 1000,
            1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450, 1500,
            1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000,
            2050, 2100, 2150, 2200, 2250, 2300, 2350, 2400, 2450, 2500
        ]

        self._cha_msg = [20, 10]
        self._cha_msgs = [
            'stunningly attractive',
            'somewhat attractive',
            'rather plain looking'
        ]
        self._str_msg = [20, 10]
        self._str_msgs = [
            ' and powerfully built {0} {1}',
            ' and moderately built {0} {1}',
            ' and slightly built {0} {1}'
        ]
        self._int_msg = [20, 10]
        self._int_msgs = [
            ' They have a bright look in their eyes.',
            ' They have a dull look in their eyes.'
        ]
        self._wis_msg = [20, 10]
        self._wis_msgs = [
            ', with a worldly air about them.',
            ', with an inexperienced look about them.',
            '.'
        ]
        self._dex_msg = [20, 10]
        self._dex_msgs = [
            ' You notice that their movements are very quick and agile.',
            ' You notice that their movements are rather slow and clumsy.'
        ]
        self._vit_msg = [100, 75, 50, 25, 0]
        self._vit_msgs = [
            ' and they are sorely wounded.',
            ' and they seem to be moderately wounded.',
            ' and they appear to be wounded.',
            ' and looks as if they are lightly wounded.',
            ' and they seem to be in good physical condition.'
        ]

        self._wearing_msg = ' They are wearing {0}, are armed with {1}'

        self._spell_casters = [2, 3, 6, 8]
        self._promo_spell_casters = [10, 11, 14, 16]
        self._magic_items = ["potion", "minor magic item", "major magic item"]
        self._equipment_items = [
            "supply", "supply weapon", "ranged weapon ammo", "ammo container",
            "thrown weapon container"
        ]
        self._shops = ["armor shop", "weapon shop", "magic shop", "equipment shop"]
        self._taverns = ["tavern", "inn"]
        self._temples = ["temple"]

    @staticmethod
    def get_current_players(players):
        """
        get formatted list of players
        """
        _players = []
        for _, player in players.items():
            _players.append(player.name)

        return _players

    def get_shop_types(self):
        """
        get formatted list of players
        """
        return self._shops

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
    def get_pids_here(uid, location, players):
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
                    _players_here.append(pid)

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

    def get_max_enc(self, _str):
        """ return max encumbrance based on strength"""
        return self._max_encumbrance[_str]

    @staticmethod
    def get_enc(_player, _items):
        """ return max encumbrance based on strength"""

        enc = 0
        enc += _items[_player.weapon].weight
        enc += _items[_player.weapon].weight
        for inv in _player.inventory:
            enc += _items[inv].weight
        enc += _player.gold * 0.2

        return int(enc)

    def get_inspect_message(self, _player, _items):
        """ return max encumbrance based on strength
                self._cha_msg = [20, 10]
        self._cha_msgs = [
            'stunningly attractive',
            'somewhat attractive',
            'rather plain looking'
        ]

        """
        msg = "{} is a ".format(_player.name)

        # cha
        if _player.cha < self._cha_msg[1]:
            msg += self._cha_msgs[2]
        elif self._cha_msg[0] > _player.cha >= self._cha_msg[1]:
            msg += self._cha_msgs[1]
        else:
            msg += self._cha_msgs[0]

        # str
        if _player.get_str() < self._str_msg[1]:
            msg += self._str_msgs[2].format(_player.get_species(), _player.get_class())
        elif self._str_msg[0] > _player.str >= self._str_msg[1]:
            msg += self._str_msgs[1].format(_player.get_species(), _player.get_class())
        else:
            msg += self._str_msgs[0].format(_player.get_species(), _player.get_class())

        # wis
        if _player.wis < self._wis_msg[1]:
            msg += self._wis_msgs[1]
        elif _player.wis >= self._wis_msg[0]:
            msg += self._wis_msgs[0]
        else:
            msg += self._wis_msgs[2]

        # dex
        if _player.get_dex() < self._dex_msg[1]:
            msg += self._dex_msgs[1]
        elif _player.dex >= self._dex_msg[0]:
            msg += self._dex_msgs[0]

        # int
        if _player.int < self._int_msg[1]:
            msg += self._int_msgs[1]
        elif _player.int >= self._int_msg[0]:
            msg += self._int_msgs[0]

        # wearing
        msg += self._wearing_msg.format(
            _items[_player.armor].long,
            _items[_player.weapon].long
        )

        # vit
        vit_perc = int(_player.vit / _player.vit_max * 100)
        if self._vit_msg[4] <= vit_perc < self._vit_msg[3]:
            msg += self._vit_msgs[0]
        elif self._vit_msg[3] <= vit_perc < self._vit_msg[2]:
            msg += self._vit_msgs[1]
        elif self._vit_msg[2] <= vit_perc < self._vit_msg[1]:
            msg += self._vit_msgs[2]
        elif self._vit_msg[1] <= vit_perc < self._vit_msg[0]:
            msg += self._vit_msgs[3]
        else:
            msg += self._vit_msgs[4]

        return msg

    def get_item_list(self, shop, town=1):
        """
        get list of items based on the shop type
        """
        shop = shop.lower()
        items = []
        if shop == "magic shop":
            for vnum, magic in self._data.equipment.items():
                if magic["town"] == town \
                        and magic["equip_type"] \
                        in self._magic_items:
                    items.append(Equipment(vnum))
        elif shop == "armor shop":
            for vnum, armor in self._data.armor.items():
                if armor["town"] == town:
                    items.append(Armor(vnum))
        elif shop == "weapon shop":
            for vnum, weapon in self._data.weapons.items():
                if weapon["town"] == town:
                    items.append(Weapon(vnum))
        elif shop == "equipment shop":
            for vnum, equipment in self._data.equipment.items():
                if equipment["town"] == town \
                        and equipment["equip_type"] \
                        in self._equipment_items:
                    items.append(Equipment(vnum))

        return items

    def room_is_shop(self, _player):
        """ is this room a shop """
        cur_room = self._rooms[_player.room[0]][self._room.get_cur_room(_player.room)]
        shops = list(set(cur_room["flags"]).intersection(set(self._shops)))
        return shops[0] if shops else None

    def room_is_tavern(self, _player):
        """ is this room a shop """
        cur_room = self._rooms[_player.room[0]][self._room.get_cur_room(_player.room)]
        taverns = list(set(cur_room["flags"]).intersection(set(self._taverns)))
        return taverns[0] if taverns else None

    def room_is_temple(self, _player):
        """ is this room a shop """
        cur_room = self._rooms[_player.room[0]][self._room.get_cur_room(_player.room)]
        temples = list(set(cur_room["flags"]).intersection(set(self._temples)))
        return temples[0] if temples else None

    def get_room_type(self, _player):
        """ is this room a shop """

        cur_room = self._rooms[_player.room[0]][self._room.get_cur_room(_player.room)]
        shop_types = self.get_shop_types()

        return list(set(cur_room["flags"]).intersection(set(shop_types)))



