""" regeneration job """
import time

from enums.status import Status


class Regenerate:
    """ reg class """

    def __init__(self, game):

        self._game = game
        print(f"init {__name__}")

    def execute(self):
        """
        execute regeneration job
        """

        for pid, player in self._game.players.items():
            if not player.is_playing:
                return

            if player.status is Status.Thirsty:
                if player.take_damage(1):
                    self._game.handle_messages(pid, "You've passed out from dehydration.")
                    self._game.handle_messages(pid, "You awaken after an unknown amount of time...")
                    self._game.handle_messages(
                        pid,
                        message_to_room=f"{player.name} loses conciousness and falls to the floor.")
                    player.handle_death(self._game.items)
            elif player.status is Status.Hungry:
                if player.take_damage(1):
                    self._game.handle_messages(pid, "You've passed out from lack of food.")
                    self._game.handle_messages(pid, "You awaken after an unknown amount of time...")
                    self._game.handle_messages(
                        pid,
                        message_to_room=f"{player.name} loses conciousness and falls to the floor.")
                    player.handle_death(self._game.items)
            else:
                print(player.status)

        """ do regenerate
        if (player.getStatus().equals(Status.HUNGRY)) {
        String playerHungerDeath = TaMessageManager.YOUDED2.getMessage();
        int damage = Dice.roll(MIN_SUSTENANCE_DAMAGE, MAX_SUSTENANCE_DAMAGE);
        takeDamage(player, playerHungerDeath, damage);
        } else if (player.getStatus().equals(Status.THIRSTY)) {
        String playerThirstDeath = TaMessageManager.YOUDED3.getMessage();
        int damage = Dice.roll(MIN_SUSTENANCE_DAMAGE, MAX_SUSTENANCE_DAMAGE);
        takeDamage(player, playerThirstDeath, damage);
        } else if (player.getStatus().equals(Status.POISONED)) {
        String playerPoisonDeath = TaMessageManager.YOUDED.getMessage();
        int damage = Dice.roll(0, player.getPoisonDamage());
        takeDamage(player, playerPoisonDeath, damage);
        } else if (player.getStatus().equals(Status.PARALYSED)) {
        if (player.decreaseParalysisTicker(TIMER_WAKEUP)) {
        player.setStatus(Status.HEALTHY);
        player.print(TaMessageManager.PAR1.getMessage());
        }
        } else if (Dice.roll(1, 100) < player.getStats().getStamina().gethpRegeneration()) {
        // Don't regenerate dead players.
        if (player.getVitality().getCurVitality() > 0) {
        player.getVitality().addCurVitality(1);
        }
        }

        if (Dice.roll(1, 100) < PLAYER_MANA_REGEN) {
        player.getMana().addCurMana(1);
        """

