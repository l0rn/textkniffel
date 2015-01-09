define(['tkclient/log', 'tkclient/config', 'tkclient/gamestate', 'tkclient/ui'], function (log, config, gamestate, ui) {
    var connection = {
        socket: null,
        isopen: false
    };

    connection.join = function(game_code, nickname) {
        var request = {
            type: 'join',
            value: {
                game_code: game_code,
                nickname: nickname
            }
        };
        connection.sendText(
            JSON.stringify(request)
        )
    };

    connection.new_game = function(code, playercount, nickname) {
            var request = {
            type: 'new',
            value: {
                playercount: playercount,
                game_code: code,
                nickname: nickname
            }
        };
        connection.sendText(
            JSON.stringify(request)
        );
    };

    connection.play = function(command, args) {
        var request = {
            type: 'play',
            value: command,
            args: args,
            game: gamestate.game_code,
            auth: gamestate.player_token
        };
        connection.sendText(
            JSON.stringify(request)
        );
    };

    connection.sendText = function(msg) {
        if (connection.isopen) {
            connection.socket.send(msg);
            log.write("Text message sent.");
        } else {
            log.write("Connection not opened.");
        }
    };

    connection.sendBinary = function() {
        if (connection.isopen) {
            var buf = new ArrayBuffer(32);
            var arr = new Uint8Array(buf);
            for (i = 0; i < arr.length; ++i) arr[i] = i;
            connection.socket.send(buf);
            log.write("Binary message sent.");
        } else {
            log.write("Connection not opened.");
        }
    };

    connection.handle_message = function(msg){
        msg = JSON.parse(msg);
        switch (msg['type']) {
            case 'slot':
                gamestate.player_token = msg['token'];
                gamestate.game_code = msg['game_code'];
                gamestate.players = msg['players'];
                gamestate.my_player_num = msg['playerno'];
                gamestate.pointrows = msg['pointrows'];
                ui.initUI(connection);
                $('#create-game-dialog').modal('hide');
                break;
            case 'update':
                ui.uiupdate(msg['values']);
                break;
            case 'error':
                alert(msg['error']);
                break;
        }
    };

    var connect = function (success, failure) {
        connection.socket = new WebSocket(config.serverUrl);
        connection.socket.binaryType = "arraybuffer";
        connection.socket.onopen = function () {
            log.write("Connected!");
            connection.isopen = true;
            success(connection);
        };
        connection.socket.onmessage = function (e) {
            if (typeof e.data == "string") {
                log.write("Text message received: " + e.data);
                connection.handle_message(e.data);
            } else {
                var arr = new Uint8Array(e.data);
                var hex = '';
                for (var i = 0; i < arr.length; i++) {
                    hex += ('00' + arr[i].toString(16)).substr(-2);
                }
                log.write("Binary message received: " + hex);
            }
        };
        connection.socket.onclose = function (e) {
            log.write("Connection closed.");
            connection.socket = null;
            connection.isopen = false;
            failure(connection);
        };
        return connection;
    };

    return {
        connect: connect
    }
});