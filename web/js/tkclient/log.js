define(['tkclient/config'], function(config){
    var write = function (msg) {
        if (config.debug) {
            console.log(msg);
        }
    };
    return {
        write: write
    }
});