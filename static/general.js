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

    var mySwiper = new Swiper ('.swiper-container', {
        pagination: {
            el: '.swiper-pagination',
            type: 'fraction'
        },
        speed: 200,
        autoHeight: true,
        preventClicks: false,
        preventClicksPropagation: false,
        hashNavigation: true,
        scrollbar: {
            el: '.swiper-scrollbar'
        }
    });

    mySwiper.on('click', function() {
        var self = mySwiper.slides[mySwiper.realIndex];

        var front = self.getElementsByClassName("front")[0];
        var back = self.getElementsByClassName("back")[0];

        if (isVisible(front)) {
            front.style.display = 'none';
            back.style.display = 'block';
        } else {
            front.style.display = 'block';
            back.style.display = 'none';
        }
    });

    initInput(mySwiper.realIndex);
    mySwiper.on('slideChange', function() {
        initInput(mySwiper.realIndex);
    });

    function initInput(index) {
        var swiper = mySwiper.slides[index];
        var id = swiper.getAttribute('data-id');
        var known = swiper.getAttribute('data-known');
        var editLink = document.getElementsByClassName('edit-link')[0];
        var knownButton = document.getElementsByClassName('known-button')[0];

        document.getElementsByClassName('mark-known')[0].value = id;
        editLink.href = editLink.getAttribute('data-url') + id;

        var classVal = knownButton.getAttribute("class");
        if (parseInt(known) === 1) {
            classVal = classVal.replace(" btn-muted","");
        } else {
            classVal = classVal.replace(" btn-muted","");
            classVal = classVal.concat(" btn-muted");
        }
        knownButton.setAttribute("class", classVal );
    }


    var isVisible = function(elem) {
        return !(elem.offsetWidth <= 0 && elem.offsetHeight <= 0);
    };

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
