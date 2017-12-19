$(document).ready(function(){
    if ($('.memorizePanel').length != 0) {

        $('.flipCard').click(function(){
            if ($('.cardFront').is(":visible") == true) {
                $('.cardFront').hide();
                $('.cardBack').show();
            } else {
                $('.cardFront').show();
                $('.cardBack').hide();
            }
        });
    }

    if ($('.cardForm').length != 0) {

        $('.cardForm').submit(function(){

            var frontTrim = $.trim($('#front').val());
            $('#front').val(frontTrim);
            var backTrim = $.trim($('#back').val());
            $('#back').val(backTrim);

            if (! $('#front').val() || ! $('#back').val()) {
                return false;
            }
        });
    }

    if ($('.editPanel').length != 0) {

        function checkit() {
            var checkedVal = $('input[name=category_id]:checked').val();
            if (checkedVal === undefined) {
                // hide the fields
                $('.fieldFront').hide();
                $('.fieldBack').hide();
                $('.saveButton').hide();
            } else {
                $('.toggleButton').removeClass('toggleSelected');
                $(this).addClass('toggleSelected');

                if (checkedVal == '1') {
                    $('textarea[name=back]').attr('rows', 5);
                } else {
                    $('textarea[name=back]').attr('rows', 12);
                }

                $('.fieldFront').show();
                $('.fieldBack').show();
                $('.saveButton').show();
            }
        }

        $('.toggleButton').click(checkit);

        checkit();
    }

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

    $('.carousel').on('swipeleft', function() {
        $(this).carousel('next');
    });

    $('.carousel').on('swiperight', function() {
        $(this).carousel('prev');
    });

    $('#carousel-slide').on('slid.bs.carousel', function () {
        var carouselData = $(this).data('bs.carousel');
        value = carouselData.getItemIndex(carouselData.$element.find('.item.active')) + 1;

        $('.slider-num').html(value);
    });

    $('.carousel .item').on('click', function(){
        var front = $(this).find('.front'),
            back = $(this).find('.back');

        if (front.is(":visible") === true) {
            front.hide();
            back.fadeIn();
        } else {
            back.hide();
            front.fadeIn();

        }
    });

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
