$(document).ready(function(){
    var added = false;
    $('.addCategory').on('click', function(e) {
        e.preventDefault();

        $('.editing').remove();
        $('.behind').removeClass('hidden');

        if (added === false) {
            var item = $('.emptyCategory')
                .clone(true)
                .removeClass('hidden emptyCategory')
                .addClass('adding');
            $('.categoryPanel').prepend(item);
            added = true;
        }
    });

    $('.editCategory').on('click', function(e) {
        e.preventDefault();
        var parent = $(this).parents('.categoryItem');

        $('.adding').remove();
        $('.editing').remove();
        $('.behind').removeClass('hidden');
        parent.addClass('hidden behind');

        var id = parent.find('.categoryId').html();
        var name = parent.find('.categoryName').html();

        var item = $('.emptyCategory')
                .clone(true)
                .removeClass('hidden emptyCategory')
                .addClass('editing');
        item.find('.categoryId').val(id);
        item.find('.categoryName').val(name);
        parent.before(item);
        added = false;
    });

    $('.undoCategory').on('click', function() {
        $(this).parents('.categoryItem').remove();
        $('.behind').removeClass('hidden');
        added = false;
    });

    $('#confirm-delete').on('show.bs.modal', function(e) {
        $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    });

    $('.alert').show().delay(1500).fadeOut();

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
