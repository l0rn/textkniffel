define(['tkclient/config', 'tkclient/draw', 'tkclient/gamestate', 'tkclient/log'], function (config, draw, gamestate, log) {
    function loadTemplate(name) {
        //load templates
        return $.ajax({
            type: 'GET',
            url: 'templates/' + name +'.html',
            async: false,
            success: function (response) {
                // success
                $.templates(name, response);
            }
        });
    }

    function initControls(connection){
        $('.dice-container').each(function() {
            $(this).click(function() {
                var diceno = parseInt($(this).children('canvas')[0].id.split('-')[1]);
                connection.play('save', [diceno]);

            });
        });
        $('.point-row td.writable').each(function() {
            $(this).click(function() {
                var field = this.id.split("-")[0];
                var row = parseInt(this.id.split("-")[1]);
                connection.play('points', [field, row]);
            })
        });
        $('#ui-roll').click(function() {
            connection.play('roll');
        });

    }

    var next_player = function(player) {
        if (player == gamestate.my_player_num - 1){
            $('#your-turn-dialog').modal('show');
        }
        var name = 'Niemand';
        if (gamestate.players[player]['active']){
            name = gamestate.players[player]['nickname'];
        }
        $('.ui-active-player').html(name);
    };

    var connectionFailureDialog = function(conn){
        $('#connection-failure-dialog').modal('show');
    };

    var gameStartDialog = function(conn) {
        $('#playercount-wrapper').hide();
        $('#ui-new').click(function() {
            if ($('#playercount-wrapper').is(":hidden")) {
                $('#playercount-wrapper').fadeIn('slow');
            } else {
                var game_code = $('#game-code').val();
                var playercount = parseInt($('#playercount').val());
                var nickname = $('#nickname').val();
                conn.new_game(game_code, playercount, nickname);
            }
        });
        $('#ui-join').click(function() {
            var game_code = $('#game-code').val();
            var nickname = $('#nickname').val();
            conn.join(game_code, nickname);
        });
        $('#create-game-dialog').modal('show');
    };

    var initUI = function (connection){

        var players = [];
        for (var i = 0; i < gamestate.players.length; i++){
            players.push({
                'player': 'player-' + gamestate.players[i]['player_number'],
                'player_num': gamestate.players[i]['player_number'],
                'player_name': gamestate.players[i]['nickname'] ? gamestate.players[i]['nickname'] : 'free slot'
            })
        }
        $.when(
        loadTemplate('pointtable').done(function(template) {
            var out = $.templates.pointtable.render(players);
            $('#point-tabs-content').html(out);
        }),
        loadTemplate('pointnav').done(function(template) {
            var out = $.templates.pointnav.render(players);
            $('#point-tabs-nav').html(out);
        })).done(function (){
            $('#name-player-' + gamestate.my_player_num).addClass('red');
            $('#point-tab-player-'  + gamestate.my_player_num).tab('show');
            $('#point-tab-player-' + gamestate.my_player_num + ' .point-cell').addClass('writable');
            initControls(connection);
        });


    };

    var updateNicknames = function (){
        for(var i = 0; i < gamestate.players.length; i++){
            if (gamestate.players[i]['active']) {
                $('#name-player-' + gamestate.players[i]['player_number']).html(gamestate.players[i]['nickname']);
            }
        }
    };

    var updateDice = function(list, turnsleft) {
        for (var i = 0; i < 5; i++) {
            draw.drawdice(list[i], $('#d-'+ (i+1)));
        }
        $('.ui-turnsleft').html(turnsleft);
    };

    var saveDice = function(list) {
        for (var i = 0; i < 5; i++) {
            if (list[i]) {
                $('#d-'+ (i+1)).parent().addClass('saved');
            } else {
                $('#d-'+ (i+1)).parent().removeClass('saved');
            }
        }
    };

    var clearDice = function() {
        updateDice([0,0,0,0,0]);
        saveDice([false,false,false,false])
    };



    var updateField = function(field, value){
        $('#' + field).html(value);
    };

    var uiupdate = function (messages) {
        for (var i = 0; i <= messages.length-1; i++){
            var msg = messages[i];
            if (msg['type'] == 'error') {
                alert(msg['error']);
                continue;
            }
            switch (msg['type']) {
                case 'dice':
                    updateDice(msg['value'], msg['turnsleft']);
                    break;
                case 'points':
                    updateField(msg['field'], msg['value']);
                    clearDice();
                    break;
                case 'save':
                    saveDice(msg['value']);
                    break;
                case 'next_player':
                    next_player(msg['value']);
            }
        }
    };

    return {
        uiupdate: uiupdate,
        initUI: initUI,
        gameStartDialog: gameStartDialog,
        connectionFailureDialog: connectionFailureDialog,
        updateNicknames: updateNicknames
    }
});
