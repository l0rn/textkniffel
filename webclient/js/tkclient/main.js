require.config({
    baseUrl: 'js'
});


requirejs(['tkclient/connection', 'tkclient/ui', 'tkclient/config'], function (connection, ui) {
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
