import sys
import re
import json

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from protocol import WebGame, ERROR_CODES
import wsconfig


class TodesKniffelServerProtocol(WebSocketServerProtocol):
    games = {}

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
            if type(ret) != tuple:
                ret = (ret,)
            for message in ret:
                if message:
                    if message.get('broadcast'):
                        game = self.games.get(message['game_code'])
                        game.broadcast(json.dumps(message))
                    else:
                        self.sendMessage(json.dumps(message))

    def join(self, msg):
        game_code = msg['value']['game_code']
        nickname = msg['value']['nickname']

        if not re.match(r"^[\w]{0,10}$", game_code):
            return {
                'type': 'error',
                'code': 407,
                'error': ERROR_CODES[407]
            }
        elif self.games.get(game_code):
            game = self.games[game_code]
            player_num, player = self.games[game_code].get_player_slot(nickname, self)
            if player and player_num:
                return {
                    'type': 'slot',
                    'game_code': game_code,
                    'playerno': player_num,
                    'token': player.token,
                    'players': game.get_players()
                }, {
                    'type': 'newplayer',
                    'broadcast': True,
                    'game_code': game_code,
                    'players': game.get_players()
                }, {

                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': game.get_all_points()
                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': (game.get_active_player(),)
                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': (game.show()[0],)
                }
            else:
                return {
                    'type': 'error',
                    'code': 406,
                    'error': ERROR_CODES[406]
                }
        else:
            return {
                'type': 'error',
                'code': 404,
                'error': ERROR_CODES[404]
            }

    def new_game(self, msg):
        playercount = msg['value']['playercount']
        game_code = msg['value']['game_code']
        nickname = msg['value']['nickname']
        if not re.match(r"^[\w]{0,10}$", game_code):
            return {
                'type': 'error',
                'code': 407,
                'error': ERROR_CODES[407]
            }

        if self.games.get(game_code):
            return {
                'type': 'error',
                'code': 405,
                'error': ERROR_CODES[405]
            }
        else:
            game = WebGame(playercount)
            self.games[game_code] = game
            player_num, player = self.games[game_code].get_player_slot(nickname, self)
            if player and player_num:
                return {
                    'type': 'slot',
                    'game_code': game_code,
                    'playerno': player_num,
                    'token': player.token,
                    'players': game.get_players()
                }, {
                    'type': 'newplayer',
                    'broadcast': True,
                    'game_code': game_code,
                    'players': game.get_players()
                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': game.get_all_points()
                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': (game.get_active_player(),)
                }, {
                    'type': 'update',
                    'game_code': game_code,
                    'broadcast': True,
                    'values': (game.show()[0],)
                }
            else:
                return {
                    'type': 'error',
                    'code': 406,
                    'error': ERROR_CODES[406]
                }

    def play(self, msg):
        game = self.games.get(msg['game'])
        token = msg['auth']
        args = msg.get('args', [])
        if game.active_player.token != token:
            return ({
                'type': 'error',
                'code': 301,
                'error': ERROR_CODES[301]
            },)
        else:
            value, errors = game.protocol_handler(msg['value'], *args)
            if value and type(value) != tuple:
                value = (value,)
            if errors and type(errors) != tuple:
                errors = (errors,)
            values = {
                'type': 'update',
                'game_code': msg['game'],
                'broadcast': True,
                'values': value
            } if value else None
            errors = {
                'type': 'update',
                'game_code': msg['game'],
                'values': errors
            } if errors else None
            return values, errors

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