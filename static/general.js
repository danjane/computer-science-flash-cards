$(document).ready(function(){

    $('.modal').on('show.bs.modal', function(e) {
        var submitButton = $(this).find('button[type=submit]');
        var form = $(this).find('form');

        // 禁用提交按钮，防止重复提交
        submitButton.attr('disabled', false);
        form.on('submit', function() {
            submitButton.attr('disabled', true);
        });
    });

    $('.alert').show().delay(1500).fadeOut();

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
