from string import uppercase
import sys
import re
import json

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from protocol import WebGame, GAME_VERSION
import wsconfig


PROTOCOL_ERRORS = {
    404: 'Game not existent',
    405: 'Game already exists',
    406: 'Game is full',
    407: 'Invalid game code',
    408: 'Invalid nickname',
    490: 'Unknown Protocol Error'
}

PROTOCOL_VERSION = GAME_VERSION


class TodesKniffelServerProtocol(WebSocketServerProtocol):
    games = {}
    MSG_SKELETON = {
        'version': PROTOCOL_VERSION,
    }

    def __init__(self, *args, **kwargs):
        self.player = None

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            self.message_broker(payload)

    def onClose(self, wasClean, code, reason):
        if self.player:
            game_code = self.player.game.game_code
            if self.player.game.nobody_left():
                del self.games[game_code]
                print(u"{} deleted".format(game_code))
            else:
                game = self.games[game_code]
                self.player.delete()
                self.distribute_message(self.protocol_message(type='update', values=[game.get_newplayer()]))
                self.distribute_message(self.protocol_message(type='update', values=[game.render()]))
                self.distribute_message(self.protocol_message(type='update', values=game.status_update()))
            print(u"{} left".format(self.player.nickname))
        print("WebSocket connection closed: {}".format(reason))

    def message_broker(self, payload):
        msg = json.loads(payload)
        msg_type = msg['type']
        ret = PROTOCOL_TYPE_HANDLERS[msg_type](self, msg)
        self.distribute_message(ret)

    def distribute_message(self, message):
        if message:
            if type(message) != list:
                message = [message]
            for message in message:
                if message:
                    if message.get('type') == 'update':
                        if message.get('values'):
                            for val in message['values']:
                                if val.get('broadcast'):
                                    game = self.games[val['game']]
                                    game.broadcast(json.dumps(
                                        self.protocol_message(type='update', values=[val])
                                    ))
                                else:
                                    self.sendMessage(json.dumps(
                                        self.protocol_message(type='update', values=[val])
                                    ))
                    else:
                        self.sendMessage(json.dumps(message))

    def join(self, msg):
        game_code = msg['value']['game_code'].upper()
        nickname = msg['value']['nickname']
        if not re.match(r"^[\w]{1,32}$", nickname, re.UNICODE):
            return self.protocol_error(408)
        game = self.games.get(game_code)
        if self.games.get(game_code):
            player = self.games[game_code].get_player_slot(nickname, self)
            if player:
                self.player = player
                return [game.game_message(
                    type='slot',
                    game_code=game.game_code,
                    playerno=player.id,
                    token=player.token,
                    players=game.get_players(),
                    pointrows=game.point_config,
                )] + [self.protocol_message(type='update', values=game.status_update())]
            else:
                return self.protocol_error(406)
        else:
            return self.protocol_error(404)

    def new_game(self, msg):
        playercount = msg['value']['playercount']
        game_code = msg['value']['game_code'].upper()
        game_config = msg['value']['game_config']
        if not re.match(r"^[\w]{1,32}$", game_code, re.UNICODE):
            return self.protocol_error(407)

        if self.games.get(game_code):
            return self.protocol_error(405)
        else:
            game = WebGame(playercount, game_code=game_code, point_config=game_config)
            self.games[game.game_code] = game
            return self.join(msg)

    def play(self, msg):
        game = self.games.get(msg['game'])
        token = msg['auth']
        args = msg.get('args', [])
        if game.active_player.token != token:
            return game.game_error(301)
        else:
            messages = game.protocol_handler(msg['value'], *args)
            if type(messages) != list:
                messages = [messages]
            return self.protocol_message(type='update', values=messages)

    def protocol_message(self, **kwargs):
        message = self.MSG_SKELETON.copy()
        message.update(kwargs)
        return message

    def protocol_error(self, code):
        try:
            return self.protocol_message(type='error',
                                         error=PROTOCOL_ERRORS[code],
                                         code=code)
        except KeyError:
            return self.protocol_message(type='error',
                                         error=PROTOCOL_ERRORS[504],
                                         code=504)


PROTOCOL_TYPE_HANDLERS = {
    'join': TodesKniffelServerProtocol.join,
    'new': TodesKniffelServerProtocol.new_game,
    'play': TodesKniffelServerProtocol.play

}


def start_server():
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    if debug:
        log.startLogging(sys.stdout)

    ws_factory = WebSocketServerFactory("ws://{}:{}".format(wsconfig.URL, wsconfig.PORT))
    ws_factory.protocol = TodesKniffelServerProtocol

    reactor.listenTCP(wsconfig.PORT, ws_factory)
    reactor.run()
