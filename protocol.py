from game import Game
from player import PlayerFinishedException, TurnEndException, NoTurnsLeftException


class WebGame(Game):

    def protocol_handler(self, msg, *args, **kwargs):
        return PROTOCOL_MESSAGES[msg](self, *args, **kwargs)

    def roll(self, *args, **kwargs):
        try:
            self.active_player.roll_dice()
            return self.show()
        except NoTurnsLeftException:
            return 'NOTURNSLEFT'

    def show(self, *args, **kwargs):
        return str(self.active_player.dice.valuelist())

    def save(self, n, *args, **kwargs):
        self.active_player.save_dice([n])
        return self.active_player.dice.values()

    def point(self, field, *args, **kwargs):
        try:
            self.active_player.entry_points(field, self.active_player.dice.valuelist())
            return self.active_player.points[field][0]
        except PlayerFinishedException:
            return 'FINISHED'
        except TurnEndException:
            return 'TURNEND'


PROTOCOL_MESSAGES = {
    'roll': WebGame.roll,
    'show': WebGame.show,
    'save': WebGame.save,
    'point': WebGame.point
}