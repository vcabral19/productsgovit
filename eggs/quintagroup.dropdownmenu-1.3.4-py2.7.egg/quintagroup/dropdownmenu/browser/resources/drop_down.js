jQuery(window).load(function() {
    $(".globalnav-toggle").click(function() {
        $(".globalnav").slideToggle(500);
        $("#globalnav-wrapper").toggleClass("open");
    });
    $(".globalnav li ul").parent(".globalnav li").addClass("plus");
    $(".globalnav li > a.hasChildrens").click(function(event) {
        if ($(window).width() <= 768) {
            if ($(this).parent().is(':not(.open)')) {
                event.preventDefault();
                $(".globalnav li").not($(this).parents()).removeClass("open");
                $(".globalnav ul").not($(this).parents()).slideUp(350);
                $(this).parent().toggleClass("open");
                $(this).next().slideToggle(500);
            }
        }
    });
    $(window).resize(function() {
        if ($(window).width() >= 768) {
            $(".globalnav li").removeClass('open');
            $(".globalnav ul").removeAttr('style');
            $(".globalnav").removeAttr('style');
        }
    });
});