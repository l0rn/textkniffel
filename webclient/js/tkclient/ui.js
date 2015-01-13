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
    var audio = [];
    var initControls = function(connection){
        $('.dice-container').each(function() {
            $(this).click(function() {
                var diceno = parseInt($(this).children('canvas')[0].id.split('-')[1]);
                connection.play('save', [diceno]);

            });
        });
        $('#ui-roll').click(function() {
            connection.play('roll');
        });
        for (var i = 1; i <= 5; i++){
            audio['d' + i] = new Audio('res/d' + i + '.wav');
        }

    };

    var next_player = function(player) {
        if (player == gamestate.my_player_num && gamestate.players.length > 1){
            $('#your-turn-dialog').modal('show');
        }
        var name = 'Niemand';
        if (gamestate.players[player - 1]['active']){
            name = gamestate.players[player - 1]['nickname'];
        }
        $('.ui-active-player').html(name);
    };

    var connectionFailureDialog = function(conn){
        $('#connection-failure-dialog').modal('show');
    };

    var gameStartDialog = function(conn) {
        $('#additional-wrapper').hide();
        $('#ui-new').click(function() {
            if ($('#additional-wrapper').is(":hidden")) {
                $('#additional-wrapper').fadeIn('slow');
            } else {
                var game_code = $('#game-code').val();
                var playercount = parseInt($('#playercount').val());
                var nickname = $('#nickname').val();
                var game_config = $('#game-config').val();
                conn.new_game(game_code, playercount, nickname, game_config);
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
                'pointrows': gamestate.pointrows,
                'player_num': gamestate.players[i]['player_number'],
                'player_name': gamestate.players[i]['nickname'] ? gamestate.players[i]['nickname'] : 'free slot',
                'rowcount': gamestate.pointrows.length
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
            var player_tab = $('#name-player-' + gamestate.my_player_num);
            player_tab.addClass('red');
            player_tab.tab('show');
            $('#point-tab-player-' + gamestate.my_player_num + ' .point-cell').addClass('writable');

            $('.point-row td.writable').each(function() {
                $(this).click(function() {
                    var field = this.id.split("-")[0];
                    var row = parseInt(this.id.split("-")[1]);
                    connection.play('points', [field, row]);
                })
            });
        });


    };

    var updateNicknames = function (){
        for(var i = 0; i < gamestate.players.length; i++){
            if (gamestate.players[i]['active']) {
                $('#name-player-' + gamestate.players[i]['player_number']).html(gamestate.players[i]['nickname']);
            }
        }
    };

    var updateDice = function(list, turnsleft, rolled) {
        var sum = list.reduce(function(pv, cv) { return pv + cv; }, 0);
        if (rolled && sum > 0){
            audio['d' + rolled].play();
        }
        for (var i = 0; i < 5; i++) {
            draw.drawdice(list[i], $('#d-'+ (i+1)));
        }
        $('.ui-turnsleft').html(turnsleft);
    };

    var saveDice = function(list) {
        for (var i = 0; i < 5; i++) {
            if (list[i]) {
                $('#save-d'+ (i+1)).show();
            } else {
                $('#save-d'+ (i+1)).hide();
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
                    updateDice(msg['value'], msg['turnsleft'], msg['rolled']);
                    break;
                case 'points':
                    if (msg['assigned']) {
                        updateField(msg['field'], msg['value']);
                        $('.preview').remove();
                    }
                    if (msg['preview']) {
                        $('#' + msg['field']).html('<span class="preview">' + msg['value'] + '</span>');
                    } else {
                        clearDice();
                    }
                    break;
                case 'save':
                    saveDice(msg['value']);
                    break;
                case 'next_player':
                    next_player(msg['value']);
                    break;
                case 'newplayer':
                    gamestate.players = msg['players'];
                    updateNicknames();
                    break;
                case 'render':
                    initUI(gamestate.connection);
                    break;
            }
        }
    };

    return {
        uiupdate: uiupdate,
        initControls: initControls,
        initUI: initUI,
        gameStartDialog: gameStartDialog,
        connectionFailureDialog: connectionFailureDialog,
        updateNicknames: updateNicknames
    }
});
