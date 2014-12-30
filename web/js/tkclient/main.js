require.config({
    baseUrl: 'js'
});

requirejs(['tkclient/draw', 'tkclient/api', 'tkclient/connection', 'tkclient/gamestate', 'tkclient/ui'], function (draw, api, connection, state, ui) {
    var connectionEstablished = function(conn) {
        $(document).ready(function() {
            ui.initUI(conn);
        });

    };
    connection.connect(connectionEstablished);
});
