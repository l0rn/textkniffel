import uuid
from game import Game
from player import PlayerFinishedException, TurnEndException, NoTurnsLeftException, WebPlayer
from points import FieldAlreadyAssignedException, POINTS, TurnDoesntMatchRestrictionException
import points

GAME_ERRORS = {
    301: 'It\'s not your turn',
    302: 'No casts are left for you',
    303: 'Your turn is over',
    304: 'This field is already assigned',
    305: 'Your turn doesn\'t match restriction',
    330: 'The game is finished',
    390: 'Unknown Game Error'
}


GAME_VERSION = '0.1'


class WebGame(Game):

    def __init__(self, playercount, game_code='', player_cls=WebPlayer, point_config='STD_CONFIG'):
        self.MSG_SKELETON = {
            'game': game_code,
            'version': GAME_VERSION,
        }
        self.game_code = game_code
        super(WebGame, self).__init__(playercount, player_cls=player_cls, point_config=point_config)

    def get_player_slot(self, nickname, socket):
        for player in self.players:
            if not player.token:
                player.token = str(uuid.uuid4())
                player.nickname = nickname
                player.socket = socket
                return player
        return None

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
                'player_number': player.id,
            })
        return players

    def get_newplayer(self):
        players = self.get_players()
        return self.game_message(
            type='newplayer',
            players=players,
            broadcast=True
        )

    def render(self):
        return self.game_message(
            type='render',
            broadcast=True
        )

    def protocol_handler(self, msg, *args, **kwargs):
        return GAME_MESSAGES[msg](self, *args, **kwargs)

    def show_dice(self):
        return self.preview_points() + [self.game_message(
            type='dice',
            turnsleft=self.active_player.max_turns - self.active_player.turn,
            rolled=len(self.active_player.dice.values) - sum(self.active_player.dice.savelist()),
            value=self.active_player.dice.valuelist(),
            broadcast=True
        )]

    def roll(self):
        try:
            self.active_player.roll_dice()
            return self.show_dice()
        except NoTurnsLeftException:
            return self.game_error(302)

    def save(self, n):
        self.active_player.save_dice([n])
        return self.game_message(
            type='save',
            value=self.active_player.dice.savelist(),
            broadcast=True
        )

    def nobody_left(self):
        return all([(not player.socket or not player.socket.state) for player in self.players])

    def get_next_player(self):
        return self.game_message(
            type='next_player',
            value=self.active_player.id,
            broadcast=True
        )

    def get_points(self, fields, columns, players):
        ret = []
        for player in players:
            points = player.points
            for column in columns:
                for field in fields:
                    ret.append(self.game_message(
                        type='points',
                        field='{}-{}-player-{}'.format(field, column, player.id),
                        value=points.get_field_value(field, column)[0],
                        assigned=points.get_field_value(field, column)[1],
                        broadcast=True,
                    ))
        return ret

    def preview_points(self):
        ret = []
        player = self.active_player
        for column in player.points.columns:
            for field in column.points:
                if field == 'bonus':
                    continue
                try:
                    columno = player.points.columns.index(column) + 1
                    score = player.entry_points(field, columno,
                                                self.active_player.dice.valuelist(), preview=True)
                    ret.append(self.game_message(
                        type='points',
                        field='{}-{}-player-{}'.format(field, columno, player.id),
                        value=score,
                        assigned=False,
                        broadcast=True,
                        preview=True
                    ))
                except FieldAlreadyAssignedException:
                    continue
        return ret

    def points(self, field, column, *args, **kwargs):
        ret = []
        player = self.active_player
        try:
            try:
                player.entry_points(field, column, self.active_player.dice.valuelist())
            except FieldAlreadyAssignedException:
                return self.game_error(304)
            except TurnDoesntMatchRestrictionException:
                return self.game_error(305)

        except PlayerFinishedException:
            ret.append(self.game_error(330))
        except TurnEndException:
            pass

        ret += self.get_points(
            fields=[field, 'subtotal', 'total', 'bonus'],
            columns=[column],
            players=[player]
        )
        ret += self.show_dice()
        return ret

    def get_all_points(self):
        ret = self.get_points(
            fields=POINTS.keys() + ['subtotal', 'bonus', 'total'],
            columns=[column['id'] for column in self.point_config],
            players=self.players
        )
        return ret

    def status_update(self):
        return [self.get_newplayer(), self.get_next_player()] + self.show_dice() + self.get_all_points()

    def game_message(self, **kwargs):
        message = self.MSG_SKELETON.copy()
        message.update(kwargs)
        return message

    def game_error(self, code, broadcast=False):
        try:
            return self.game_message(type='error',
                                     error=GAME_ERRORS[code],
                                     code=code,
                                     broadcast=broadcast)
        except KeyError:
            return self.game_message(type='error',
                                     error=GAME_ERRORS[504],
                                     code=504,
                                     broadcast=broadcast)

GAME_MESSAGES = {
    'roll': WebGame.roll,
    'show': WebGame.show_dice,
    'save': WebGame.save,
    'points': WebGame.points
}