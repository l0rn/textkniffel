define([], function () {
    var loadTemplate = function (name) {
        //load templates
        return $.ajax({
            type: 'GET',
            url: 'templates/' + name + '.html',
            async: false,
            success: function (response) {
                // success
                $.templates(name, response);
            }
        });
    };

    return {
        loadTemplate: loadTemplate
    }
});
