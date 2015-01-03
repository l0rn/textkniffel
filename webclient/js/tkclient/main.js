require.config({
    baseUrl: 'js',
});

requirejs(['tkclient/draw', 'tkclient/api', 'tkclient/connection', 'tkclient/gamestate', 'tkclient/ui'], function (draw, api, connection, state, ui) {

    var successCallback = function(conn) {
        $(document).ready(function() {
            ui.gameStartDialog(conn);
        });
    };
    var failureCallback = function(conn) {
        $(document).ready(function() {
            ui.connectionFailureDialog(conn);
        });
    };
    connection.connect(successCallback, failureCallback);
});
