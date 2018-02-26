$(document).ready(function(){

    $('.modal').on('show.bs.modal', function(e) {
        var submitButton = $(this).find('button[type=submit]');
        var form = $(this).find('form');

        submitButton.attr('disabled', false);
        form.on('submit', function() {
            submitButton.attr('disabled', true);
        });
    });

    $('#deleteCategory').on('show.bs.modal', function(e) {
        $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    });

    $('.alert').show().delay(1500).fadeOut();

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
