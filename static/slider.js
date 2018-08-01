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