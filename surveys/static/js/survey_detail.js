$(function () {
    $('.answers').on('click', '.label', function () {

        // FIXME: reimplement to handle removal correctly.

        // Filter by similar results
        var k = $(this).data('key');
        var v = $(this).data('value');

        $(".answers .key-" + k).filter(function () {
            return $(this).data('value') === v;
        }).toggleClass('label-info').toggleClass('label-primary');

        $(".answers>li").filter(function () {
            return $(this).find('.key-' + k).data('value') !== v;
        }).toggle($(this).hasClass('label-info'));

        $(":checkbox:hidden").prop('checked', false);

        $('body').trigger('foo');



    });

});
