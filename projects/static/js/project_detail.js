$(function () {
    "use strict";

    var original = $("#voteform").serialize();

    var refresh = function() {
        $("#voteform .save").toggle($("#voteform").serialize() != original)
    };


    $("#voteform input").change(refresh);

    $("#voteform").ajaxForm({
        success: function() {
            $('#voteform button,#voteform input').prop('disabled', false);
            $('#voteform .ok').show().slideUp(1500);
            $('#voteform .loader').hide();
            original = $("#voteform").serialize();
            refresh();
        },
        beforeSubmit: function() {
            $('#voteform button,#voteform input').prop('disabled', true);
            $('#voteform .ok').hide();
            $('#voteform .loader').show();
        },
        error: function() {
            alert("Unexpected error. Please reload page.");
        }
    })
});

$(function () {
    "use strict";

    var form = $("#commentform");
    
    var refresh = function() {
        var valid = form.get(0).checkValidity();
        form.find("button").prop('disabled', !valid);
    };

    form.find("textarea,select").on('input', refresh);

    form.ajaxForm({
        success: function(resp) {
            form.find(':input').prop('disabled', false);
            form.get(0).reset();
            form.find('.loader').hide();
            var el = $(resp.result.trim());
            $("#comments>li:last").before(el);
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
    $('body').on('click', '.review', function() {
        var el = $(this);
        $.post(el.data('url'), function() {
            el.html('<i class="fa fa-check"></i>');
        });
        el.html('<i class="fa fa-spin fa-spinner"></i>');
    });
});

