(function ($) {

    "use strict";

    var pluginName = "fixCode";

    var ascii = /^[\x00-\xFF]+$/;
    var english = /[a-zA-Z]/;

    var isEnglish = function (s) {
        return ascii.test(s) && english.test(s);
    };

    var fixCode = function (el) {
        if (isEnglish($(el).text())) {
            $(el).css('direction', 'ltr').css('white-space', 'pre').css('font-family', 'monospace');
        }
    };

    $.fn[pluginName] = function () {
        return this.each(function () {
            fixCode(this);
        });
    };

})(jQuery);
