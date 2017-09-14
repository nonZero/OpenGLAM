$(function () {
    "use strict";

    var form = $("#noteform");
    
    var refresh = function() {
        var valid = form.get(0).checkValidity();
        form.find("button").prop('disabled', !valid);
    };

    form.find(":input").on('input', refresh);

    form.ajaxForm({
        success: function(resp) {
            form.find(':input').prop('disabled', false);
            form.get(0).reset();
            form.find('.loader').hide();
            var el = $(resp.result.trim());
            $("#notes").prepend(el);
            el.hide().slideDown();
            refresh();
        },
        beforeSubmit: function() {
            form.find(':input').prop('disabled', true);
            form.find('.loader').show();
        },
        error: function() {
            alert("Unexpected error. Please reload page.");
        }
    })
});

$(function () {
    "use strict";
    $('body').on('click', '.close', function() {
        var el = $(this);
        $.post(el.data('url'), function(resp) {
            el.closest('li').replaceWith($(resp.result.trim()));
        });
        el.html('<i class="fa fa-spin fa-spinner"></i>');
    });
});

