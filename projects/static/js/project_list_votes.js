$(function () {
    $('.user').hover(
        function() {
            var id = $(this).data('id');
            $(".user").not("[data-id="+id+"]").addClass("dimmed");
        },
        function() {
            $(".user").removeClass("dimmed");
        }
    );

    $(".blocks").sortable({
        containerSelector: '.blocks',
        itemSelector: '.block',
        handle: '.fa-arrows',
        placeholder: '<div class="panel panel-info placeholder"><div class="panel-heading">&nbsp;</div></div>'
    });
});
