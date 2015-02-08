define(function () {
    var game_code = null;
    var token = null;
    var players = null;
    var my_player_num = null;
    var connection = null;

    return {
        connection: connection,
        game_code: game_code,
        player_token: token,
        players: players,
        my_player_num: my_player_num
    }
});