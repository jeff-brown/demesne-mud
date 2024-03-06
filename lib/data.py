""" data class """
import yaml


class Data:

    def __init__(self):
        """
        initialize all the data files
        """

        self.species = self._get_species()
        self.classes = self._get_classes()
        self.armor = self._get_armor()
        self.weapons = self._get_weapons()
        self.equipment = self._get_equipment()
        self.stat_ranges = self._get_stat_ranges()
        self.chambers = self._get_chambers()
        self.areas = self._get_areas()
        self.npcs = self._get_npcs()
        self.mobs = self._get_mobs()
        self.messages = self._get_messages()

        print(f"init {__name__}")

    @staticmethod
    def _get_species(conf="conf/species.yaml"):
        """ read species from conf """
        with open(conf, "rb") as stream:
            try:
                _species = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _species

    @staticmethod
    def _get_npcs(conf="conf/npcs.yaml"):
        """ read species from conf """
        with open(conf, "rb") as stream:
            try:
                _npcs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _npcs

    @staticmethod
    def _get_messages(conf="conf/messages.properties"):
        """ read species from conf """
        _messages = {}

        with open(conf, "r") as stream:
            try:
                messages = stream.read()
            except yaml.YAMLError as exc:
                print(exc)

        for m in messages.split("\n"):
            _messages[m.split('=')[0]] = m.split('=')[1]
        return _messages

    @staticmethod
    def _get_mobs(conf="conf/mobs.yaml"):
        """ read species from conf """
        with open(conf, "rb") as stream:
            try:
                _mobs = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _mobs

    @staticmethod
    def _get_areas(conf="conf/areas.yaml"):
        """ read species from conf """
        with open(conf, "rb") as stream:
            try:
                _areas = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _areas

    @staticmethod
    def _get_chambers(conf="conf/chambers.yaml"):
        """ read species from conf """
        with open(conf, "rb") as stream:
            try:
                _chambers = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _chambers

    @staticmethod
    def _get_classes(conf="conf/classes.yaml"):
        """ read classes from conf"""
        with open(conf, "rb") as stream:
            try:
                _classes = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _classes

    @staticmethod
    def _get_equipment(conf="conf/equipment.yaml"):
        """ read equipment from conf"""
        with open(conf, "rb") as stream:
            try:
                _equipment = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _equipment

    @staticmethod
    def _get_stat_ranges(conf="conf/stat_ranges.yaml"):
        """ read stat_ranges from conf"""
        with open(conf, "rb") as stream:
            try:
                _stat_ranges = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _stat_ranges

    @staticmethod
    def _get_weapons(conf="conf/weapons.yaml"):
        """ read stat_ranges from conf"""
        with open(conf, "rb") as stream:
            try:
                _weapons = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _weapons

    @staticmethod
    def _get_armor(conf="conf/armor.yaml"):
        """ read stat_ranges from conf"""
        with open(conf, "rb") as stream:
            try:
                _armor = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return _armor

    @staticmethod
    def _get_data_file(file):
        """ read generic data file """
        with open(file, "rb") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return data

    def get_armor_by_type(self, _type):
        """ ger armor vnum by type """
        for vnum, armor in self.armor.items():
            if armor['type'] == _type.lower():
                return vnum

    def get_weapon_by_type(self, _type):
        """ ger armor vnum by type """
        for vnum, weapon in self.weapons.items():
            if weapon['type'] == _type.lower():
                return vnum

    def get_equipment_by_type(self, _type):
        """ ger armor vnum by type """
        for vnum, equipment in self.equipment.items():
            if equipment['type'] == _type.lower():
                return vnum




