define(['tkclient/log'], function (log) {
    var connection = {
        socket: null,
        isopen: false
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

    var connect = function (callback) {
        connection.socket = new WebSocket("ws://localhost:9000");
        connection.socket.binaryType = "arraybuffer";
        connection.socket.onopen = function () {
            log.write("Connected!");
            connection.isopen = true;
            callback(connection);
        };
        connection.socket.onmessage = function (e) {
            if (typeof e.data == "string") {
                log.write("Text message received: " + e.data);
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
        };
        return connection;
    };

    return {
        connect: connect
    }
});