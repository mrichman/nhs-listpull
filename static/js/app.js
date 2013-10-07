$(document).ready(function() {

    $('.dropdown-menu li a').click(function(e){
        e.preventDefault();
        $('.row').hide();
        $('#job_status').show();
        var href = $(this).attr('href');
        $(href).show();
    });

    $('button.generate').click(function() {
        $.blockUI({ message: $('#domMessage') });
    });

});