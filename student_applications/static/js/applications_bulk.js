$(function () {

    var boxes = $('[name=users]:checkbox');


    var mark = function (b) {
        boxes.filter(':visible').prop('checked', b);
        refreshEmails();
    };
    $(".select-all").click(function () {
        mark(true);
    });
    $(".select-none").click(function () {
        mark(false);
    });

    function refreshEmails() {
        var checked = boxes.filter(':visible:checked');
        var emails = checked.map(function () {
            return $(this).data('email');
        }).get();
        $('#emails').val(emails.join('\n')).attr('rows', checked.length);
    }

    $(boxes).change(refreshEmails);

    $('body').on('foo', refreshEmails);

    refreshEmails();

});
