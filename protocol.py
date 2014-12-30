import uuid
from game import Game
from player import PlayerFinishedException, TurnEndException, NoTurnsLeftException, WebPlayer
from points import FieldAlreadyAssignedException

ERROR_CODES = {
    404: 'Game not existent',
    405: 'Game already exists',
    406: 'Game is full',
    407: 'Invalid game code',
    301: 'It\'s not your turn',
    302: 'No casts are left for you',
    303: 'Your turn is over',
    304: 'This field is already assigned',
    330: 'The game is finished'
}


class WebGame(Game):

    def __init__(self, playercount, player_cls=WebPlayer):
        super(WebGame, self).__init__(playercount, player_cls=player_cls)

    def get_player_slot(self):
        for player in self.players:
            if not player.token:
                player.token = str(uuid.uuid4())
                return self.players.index(player) + 1, player.token
        return None

    def protocol_handler(self, msg, *args, **kwargs):
        return PROTOCOL_MESSAGES[msg](self, *args, **kwargs)

    def roll(self, *args, **kwargs):
        try:
            self.active_player.roll_dice()
            return self.show()
        except NoTurnsLeftException:
            return {
                'type': 'error',
                'code': 302,
                'error': ERROR_CODES[302]
            }

    def show(self, *args, **kwargs):
        return {
            'type': 'dice',
            'value': self.active_player.dice.valuelist()
        }

    def save(self, n, *args, **kwargs):
        self.active_player.save_dice([n])
        return {
            'type': 'save',
            'value': self.active_player.dice.savelist()
        }

    def points(self, field, row, *args, **kwargs):
        try:
            player = self.active_player
            try:
                player.entry_points(field, self.active_player.dice.valuelist())
            except FieldAlreadyAssignedException:
                return {
                    'type': 'error',
                    'code': 304,
                    'error': ERROR_CODES[304]
                }
            return {
                'type': 'points',
                'field': '{}-{}'.format(field, row),
                'value': player.points.points[field][0]
            }, {
               'type': 'points',
               'field': 'subtotal-{}'.format(row),
               'value': player.points.subtotal()
            }, {
               'type': 'points',
               'field': 'total-{}'.format(row),
               'value': player.points.sumpoints()
            }, {
               'type': 'points',
               'field': 'bonus-{}'.format(row),
               'value': player.points.bonus()
            }

        except PlayerFinishedException:
            return {
                'type': 'error',
                'code': 330,
                'error': ERROR_CODES[330]
            }, {
                'type': 'points',
                'field': '{}-{}'.format(field, row),
                'value': player.points.points[field][0]
            }
        except TurnEndException:
            return {
                'type': 'error',
                'code': 303,
                'error': ERROR_CODES[303]
            }


PROTOCOL_MESSAGES = {
    'roll': WebGame.roll,
    'show': WebGame.show,
    'save': WebGame.save,
    'points': WebGame.points
}