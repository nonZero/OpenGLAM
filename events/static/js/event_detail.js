$(function () {

    function refreshEmails() {
        var boxes = $('.user-email:checked');

        $('#emails').val(boxes.map(function () {
            return $(this).data('email');
        }).get().join('\n')).prop('rows', boxes.length);
    }

    $('.user-email').change(refreshEmails);

    refreshEmails();

    $(".grouper").click(function () {
        var boxes = $(this).parent('.group').find(':checkbox');
        boxes.prop('checked', boxes.length > boxes.filter(':checked').length);
        refreshEmails();
    });

})
;
