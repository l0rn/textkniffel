require.config({
    baseUrl: 'js',
    paths: {
        // the left side is the module ID,
        // the right side is the path to
        // the jQuery file, relative to baseUrl.
        // Also, the path should NOT include
        // the '.js' file extension. This example
        // is using jQuery 1.9.0 located at
        // js/lib/jquery-1.9.0.js, relative to
        // the HTML page.
        jquery: 'lib/jquery-2.1.3.min'
    }
});

// get ui api
requirejs(['jquery', 'tkclient/draw', 'tkclient/api', 'tkclient/connection'], function ($, draw, api, connection) {
    var handler = function(conn) {
        conn.sendText('roll');
        conn.sendText('roll');
        conn.sendText('roll');
        conn.sendText('roll');
    };
    connection.connect(handler);
});
