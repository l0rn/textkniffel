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

    def get_player_slot(self, nickname, socket):
        for player in self.players:
            if not player.token:
                player.token = str(uuid.uuid4())
                player.nickname = nickname
                player.socket = socket
                return self.players.index(player) + 1, player
        return None, None

    def broadcast(self, msg):
        for player in self.players:
            if player.socket is not None:
                player.socket.sendMessage(msg)

    def get_players(self):
        players = []
        for player in self.players:
            players.append({
                'active': True if player.token else False,
                'nickname': player.nickname,
                'player_number': self.players.index(player) + 1,
            })
        return players

    def protocol_handler(self, msg, *args, **kwargs):
        return PROTOCOL_MESSAGES[msg](self, *args, **kwargs)

    def roll(self, *args, **kwargs):
        try:
            self.active_player.roll_dice()
            return self.show()
        except NoTurnsLeftException:
            return None, {
                'type': 'error',
                'code': 302,
                'error': ERROR_CODES[302]
            }

    def show(self, *args, **kwargs):
        return {
            'type': 'dice',
            'turnsleft': self.active_player.max_turns - self.active_player.turn,
            'value': self.active_player.dice.valuelist()
        }, None

    def save(self, n, *args, **kwargs):
        self.active_player.save_dice([n])
        return {
            'type': 'save',
            'value': self.active_player.dice.savelist()
        }, None

    def get_active_player(self):
        return {
            'type': 'next_player',
            'value': self.active_player_number
        }

    def points(self, field, row, *args, **kwargs):
        try:
            player = self.active_player
            player_number = self.active_player_number + 1
            try:
                player.entry_points(field, self.active_player.dice.valuelist())
            except FieldAlreadyAssignedException:
                return None, {
                    'type': 'error',
                    'code': 304,
                    'error': ERROR_CODES[304]
                }
            return ({
                'type': 'points',
                'field': '{}-{}-player-{}'.format(field, row, player_number),
                'value': player.points.points[field][0]
            }, {
               'type': 'points',
               'field': 'subtotal-{}-player-{}'.format(row, player_number),
               'value': player.points.subtotal()
            }, {
               'type': 'points',
               'field': 'total-{}-player-{}'.format(row, player_number),
               'value': player.points.sumpoints()
            }, {
               'type': 'points',
               'field': 'bonus-{}-player-{}'.format(row, player_number),
               'value': player.points.bonus()
            }, {
                'type': 'next_player',
                'value': self.active_player_number
            }, self.show()[0]),  None

        except PlayerFinishedException:
            return {
                'type': 'points',
                'field': '{}-{}'.format(field, row),
                'value': player.points.points[field][0]
            }, {
                'type': 'error',
                'code': 330,
                'error': ERROR_CODES[330]
            }

        except TurnEndException:
            return None, {
                'type': 'error',
                'code': 303,
                'error': ERROR_CODES[303]
            }

    def get_all_points(self):
        ret = []
        for player in self.players:
            for field, value in player.points.points.iteritems():
                if value[1]:
                    ret.append({
                        'type': 'points',
                        'field': '{}-{}-player-{}'.format(field, 1, self.players.index(player) + 1),
                        'value': value[0]
                    })
        return tuple(ret)

PROTOCOL_MESSAGES = {
    'roll': WebGame.roll,
    'show': WebGame.show,
    'save': WebGame.save,
    'points': WebGame.points
}