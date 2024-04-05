""" training class """
import random

from lib import data
from lib.info import Info
from lib.spell import Spell


class Guild:
    """
    @DynamicAttrs
    This class contains all the basic training commands
    """

    def __init__(self, game):
        """ read in the config files """
        print(f"init {__name__}")
        self._game = game
        self._info = Info(game)
        self._messages = data.messages
        self.training_cost_modifier = 5
        self.stat_increase_chance = 25
        self._spell_casters = [8, 2, 3, 6]
        self._max_spells = 8

    @staticmethod
    def _get_spell_vnum_by_name(name):
        """
        lookup spell vnum by name
        """
        for vnum, spell in data.spells.items():
            if spell["name"] == name:
                return vnum

        return None

    @staticmethod
    def _spell_book_contains(player, spell):
        """
        check if spellbook contains spell
        """
        for s in player.spellbook:
            if s.name == spell.name:
                return True

        return False

    def handle_training(self, player):
        """
        ring the bells
        """
        print(__name__)
        pid = self._info.get_pid_by_name(self._game.players, player.name)
        training_cost = int((player.level + 1) * self.training_cost_modifier)
        if training_cost > player.gold:
            self._game.handle_messages(pid, self._messages['CNTAFD'].format('to buy training.'))
            print("you broke")
            return

        exp_req = self._info.get_exp_gain(player)
        if player.experience < exp_req:
            self._game.handle_messages(pid, self._messages['NOTRDY'])
            print("you stupid")
            return

        player.gold -= training_cost
        player.level += 1
        player.increase_vitality()
        player.increase_stat()
        # player.increase_mana()

        self._game.handle_messages(pid, self._messages['GNDLEV'])
        self._game.handle_messages(pid, message_to_room=self._messages['GOTTRN'].format(player.name))

        return

    def handle_buy(self, player, spell_name):
        """
        buy spells
        """
        vnum = self._get_spell_vnum_by_name(spell_name)
        pid = self._info.get_pid_by_name(self._game.players, player.name)

        if player.p_class not in self._spell_casters:
            self._game.handle_messages(pid, self._messages['WARNSP'].format(player.get_class() + "s"))
            return

        if vnum is None:
            self._game.handle_messages(pid, self._messages['NOSSPL'])
            return

        spell = Spell(vnum)
        if spell.p_class != player.p_class:
            self._game.handle_messages(pid, self._messages['OUTRLM'].format(player.get_class() + "s"))
            return

        if self._spell_book_contains(player, spell):
            self._game.handle_messages(pid, self._messages['ALRHVS'])
            return

        if player.level < spell.get_level():
            self._game.handle_messages(pid, self._messages['TOOBIG'])
            return

        if len(player.spellbook) == self._max_spells:
            self._game.handle_messages(pid, self._messages['BOKFUL'])
            return

        """
        9
        0.29
        20
        12
        """
        variance = random.randint(0, 20) - 10
        print(variance)
        percent_markup = (player.get_buy_modifier() + variance) / 100
        print(percent_markup)
        print(player.get_buy_modifier())
        mod_cost = int((spell.cost * percent_markup) + spell.cost)
        print(mod_cost)

        if mod_cost < 1:
            mod_cost = 1

        if mod_cost > player.gold:
            self._game.handle_messages(pid, self._messages['CNTAFS'])
            return

        """
        player.subtractGold(modCost);
        String messageToPlayer = MessageFormat.format(TaMessageManager.YOUGOT.getMessage(), spell.getName(), modCost);
        player.print(messageToPlayer);
        String messageToRoom = MessageFormat.format(TaMessageManager.BYSOTH.getMessage(),
        player.getName(), spell.getName());
        room.print(player, messageToRoom, false);
        player.getSpellbook().scribeSpell(spell);
        """
        player.gold -= spell.cost
        self._game.handle_messages(pid, self._messages['YOUGOT'].format(spell.name, mod_cost))
        self._game.handle_messages(pid, message_to_room=self._messages['BYSOTH'].format(player.name))
        player.spellbook.append(spell)


