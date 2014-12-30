define(['jquery', 'tkclient/draw', 'tkclient/connection'], function ($, draw) {
    function initControls(conn){
        $('#playercount-wrapper').hide();
        $('.point-row td.writable').each(function() {
            $(this).click(function() {
                var field = this.id.split("-")[0];
                var row = parseInt(this.id.split("-")[1]);
                conn.play('points', [field, row]);
            })
        });
        $('#ui-roll').click(function() {
            conn.play('roll');
        });
        $('#ui-new').click(function() {
            if ($('#playercount-wrapper').is(":hidden")) {
                $('#playercount-wrapper').fadeIn('slow');
            } else {
                var game_code = $('#game-code').val();
                var playercount = parseInt($('#playercount').val());
                conn.new_game(game_code, playercount);
            }
        });
        $('#ui-join').click(function() {
            var game_code = $('#game-code').val();
            conn.join(game_code);
        });

        $('.dice-container').each(function() {
            $(this).click(function() {
                var diceno = parseInt($(this).children('canvas')[0].id.split('-')[1]);
                conn.play('save', [diceno]);

            });
        });
        $('#create-game-dialog').modal('show');
    }

    var initUI = function (conn){
        initControls(conn);
    };

    var updateDice = function(list) {
        for (var i = 0; i < 5; i++) {
            draw.drawdice(list[i], $('#d-'+ (i+1)));
        }
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
                    updateDice(msg['value']);
                    break;
                case 'points':
                    updateField(msg['field'], msg['value']);
                    clearDice();
                    break;
                case 'save':
                    saveDice(msg['value']);
            }
        }
    };

    return {
        uiupdate: uiupdate,
        initUI: initUI
    }
});
