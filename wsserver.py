import sys
import re
import json

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from protocol import WebGame, GAME_ERRORS, GAME_VERSION
import wsconfig


PROTOCOL_ERRORS = {
    404: 'Game not existent',
    405: 'Game already exists',
    406: 'Game is full',
    407: 'Invalid game code',
    490: 'Unknown Protocol Error'
}

PROTOCOL_VERSION = GAME_VERSION


class TodesKniffelServerProtocol(WebSocketServerProtocol):
    games = {}
    MSG_SKELETON = {
        'version': PROTOCOL_VERSION,
    }

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            self.message_broker(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

    def message_broker(self, payload):
        msg = json.loads(payload)
        msg_type = msg['type']
        ret = PROTOCOL_TYPE_HANDLERS[msg_type](self, msg)
        if ret:
            if type(ret) != list:
                ret = [ret]
            for message in ret:
                if message:
                    if message.get('update') and message.get('broadcast'):
                        game = self.games.get(message['game_code'])
                        game.broadcast(json.dumps(message))
                    else:
                        self.sendMessage(json.dumps(message))

    def join(self, msg):
        game_code = msg['value']['game_code']
        nickname = msg['value']['nickname']
        game = self.games.get(game_code)

        if not re.match(r"^[\w]{0,10}$", game_code):
            return game.game_error(407)
        elif self.games.get(game_code):
            player = self.games[game_code].get_player_slot(nickname, self)
            if player:
                return [game.game_message(
                    type='slot',
                    game_code=game.game_code,
                    playerno=player.id,
                    token=player.token,
                    players=game.get_players(),
                    pointrows=game.point_config,
                )] + [self.protocol_message(type='update', values=game.status_update())]
            else:
                return game.game_error(406)
        else:
            return game.game_error(404)

    def new_game(self, msg):
        playercount = msg['value']['playercount']
        game_code = msg['value']['game_code']
        if not re.match(r"^[\w]{0,10}$", game_code):
            return self.protocol_error(407)

        if self.games.get(game_code):
            return self.protocol_error(405)
        else:
            game = WebGame(playercount, game_code=game_code, point_config='TODES_CONFIG')
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

    ws_factory = WebSocketServerFactory("ws://{}:{}".format(wsconfig.URL, wsconfig.PORT),
                                        debug=debug,
                                        debugCodePaths=debug)

    ws_factory.protocol = TodesKniffelServerProtocol
    ws_factory.setProtocolOptions(allowHixie76=True)

    reactor.listenTCP(wsconfig.PORT, ws_factory)
    reactor.run()