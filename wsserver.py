###############################################################################
##
##  Copyright (C) 2012-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
# ##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource

from dice import Dice

##
## Our WebSocket Server protocol
##
from protocol import WebGame


class TodesKniffelServerProtocol(WebSocketServerProtocol):
    game = WebGame(2)

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if not isBinary:
            ret = self.game.protocol_handler(payload)
            if ret:
                self.sendMessage(ret)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))



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