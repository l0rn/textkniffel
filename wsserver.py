import sys
import re
import json

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from protocol import WebGame, ERROR_CODES


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
        self.process_return_value(ret)

    def process_return_value(self, ret):
        if type(ret) == list:
            self.sendMessage(json.dumps(ret[0]))
            self.process_return_value(self, ret[1])
        elif type(ret) == dict:
            self.sendMessage(json.dumps(ret))

    def join(self, msg):
        game_code = msg['value']
        if not re.match(r"^[\w]{0,10}$", game_code):
            return {
                'type': 'error',
                'code': 407,
                'error': ERROR_CODES[407]
            }
        elif self.games.get(game_code):
            slot = self.games[game_code].get_player_slot()
            if slot:
                return {
                    'type': 'slot',
                    'game_code': game_code,
                    'playerno': slot[0],
                    'token': slot[1]
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
        if self.games.get(game_code):
            return {
                'type': 'error',
                'code': 405,
                'error': ERROR_CODES[405]
            }
        else:
            self.games[game_code] = WebGame(playercount)
            slot = self.games[game_code].get_player_slot()
            if slot:
                return {
                    'type': 'slot',
                    'game_code': game_code,
                    'playerno': slot[0],
                    'token': slot[1]
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
            return {
                'type': 'error',
                'code': 301,
                'error': ERROR_CODES[301]
            }
        else:
            value = game.protocol_handler(msg['value'], *args)
            if type(value) != tuple:
                value = (value,)
            if value:
                return {
                    'type': 'update',
                    'values': value
                }
        return None

PROTOCOL_TYPE_HANDLERS = {
    'join': TodesKniffelServerProtocol.join,
    'new': TodesKniffelServerProtocol.new_game,
    'play': TodesKniffelServerProtocol.play

}


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    if debug:
        log.startLogging(sys.stdout)

    ##
    ## create a Twisted Web resource for our WebSocket server
    ##
    wsFactory = WebSocketServerFactory("ws://localhost:9000",
                                       debug=debug,
                                       debugCodePaths=debug)

    wsFactory.protocol = TodesKniffelServerProtocol
    wsFactory.setProtocolOptions(allowHixie76=True)  # needed if Hixie76 is to be supported

    wsResource = WebSocketResource(wsFactory)

    reactor.listenTCP(9000, wsFactory)
    reactor.run()