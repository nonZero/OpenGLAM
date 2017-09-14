$(function () {

    var limit = Number($('.limit').text());

    function update() {
        var items = $(".bid input[type=range]");
        var total = items.map(function () {
            return $(this).val();
        }).get().reduce(function (prev, current) {
            return prev + Number(current);
        }, 0);
        $('.total').text(total).toggleClass('text-danger', total > limit).toggleClass('text-warning', total < limit).toggleClass('text-success', total == limit);
        $('.bid button').prop('disabled', total != limit);

        var data = items.map(function () {
            return [[$(this).data('id'), Number($(this).val())]];
        }).get();

        $('#v').val(JSON.stringify(data));
    }

    update();


    $(".bid-item input[type=range]").on("input", function () {
        $(this).closest('.bid-item').find('input[type=number]').val($(this).val());
        update();
        return false;
    });
    $(".bid-item input[type=number]").on("input", function () {
        $(this).closest('.bid-item').find('input[type=range]').val($(this).val());
        update();
    });
});
