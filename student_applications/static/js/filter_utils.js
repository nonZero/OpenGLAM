$(function () {
    'use strict';

    const apps = $('.apps .app');
    const tags = $('.utag');
    let needed = 0;

    const refresh = () => {
        $(".visible-apps").text(apps.filter(":visible").length);
    };

    tags.click(function () {
        const t = $(this).data('tag');
        const b = $(this).hasClass("label-success");
        needed += b ? -1 : 1;

        tags.filter((i, el) => $(el).data('tag') === t)
            .toggleClass('label-default')
            .toggleClass('label-success');

        apps.hide()
            .filter((i, el) => $(el).find(".utag.label-success").length === needed)
            .show();
        refresh();
    });

    refresh();

    $(".total-apps").text(apps.length);

});
