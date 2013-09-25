$(document).ready(function() {
    $('.dropdown-menu li a').click(function(e){
        e.preventDefault();
        $('.row').hide();
        href = $(this).attr('href');
        $(href).show();
    });
});

