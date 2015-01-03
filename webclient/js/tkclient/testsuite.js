var connection = {
    socket: null,
    isopen: false
};

var player_token;
var playerno;
var game_code;

function handle_message(msg){
    msg = JSON.parse(msg);
    switch (msg['type']) {
        case 'slot':
            player_token = msg['token'];
            game_code = msg['game_code'];
            break;
        case 'update':
            var update_body = msg['value'];
            if (update_body['content']['type'] == 'error') {
                alert(update_body['content']['error']);
                return;
            }
            switch (update_body['action']) {
                case 'roll':
                    update_dice(update_body['content']['value']
            }
        case 'error':
            alert(msg['error']);
            break;
    }
}

function join(code) {
    var request = {
        type: 'join',
        value: code
    };
    connection.sendText(
        JSON.stringify(request)
    )
}

function new_game(code, playercount){
        var request = {
        type: 'new',
        value: {
            playercount: playercount,
            game_code: code
        }
    };
    connection.sendText(
        JSON.stringify(request)
    )
}

function play(command, args){
    var request = {
        type: 'play',
        value: command,
        args: args,
        game: game_code,
        auth: player_token
    };
    connection.sendText(
        JSON.stringify(request)
    )
}


connection.sendText = function(msg) {
    if (connection.isopen) {
        connection.socket.send(msg);
        console.log("Text message sent.");
    } else {
        console.log("Connection not opened.");
    }
};

connection.sendBinary = function() {
    if (connection.isopen) {
        var buf = new ArrayBuffer(32);
        var arr = new Uint8Array(buf);
        for (i = 0; i < arr.length; ++i) arr[i] = i;
        connection.socket.send(buf);
        console.log("Binary message sent.");
    } else {
        console.log("Connection not opened.");
    }
};

var connect = function () {
    connection.socket = new WebSocket("ws://localhost:9000");
    connection.socket.binaryType = "arraybuffer";
    connection.socket.onopen = function () {
        console.log("Connected!");
        connection.isopen = true;
    };
    connection.socket.onmessage = function (e) {
        if (typeof e.data == "string") {
            console.log("Text message received: " + e.data);
            handle_message(e.data);
        } else {
            var arr = new Uint8Array(e.data);
            var hex = '';
            for (var i = 0; i < arr.length; i++) {
                hex += ('00' + arr[i].toString(16)).substr(-2);
            }
            console.log("Binary message received: " + hex);
        }
    };
    connection.socket.onclose = function (e) {
        console.log("Connection closed.");
        connection.socket = null;
        connection.isopen = false;
    };
    return connection;
};

connect();