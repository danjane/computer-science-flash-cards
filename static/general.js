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


    /**
     * 鼠标悬浮时显示添加、编辑、删除计划按钮
     */
    $('.plan-item').mouseenter(function() {
        var self = $(this);
        var parentLi = self.parent();

        var add = ' <span class="text-button plan-add">Add</span>';
        var edit = ' <span class="text-button plan-edit">Edit</span>';
        var remove = ' <span class="text-button plan-remove">Delete</span>';

        var currentValue = self.find('input').val().split('/').slice(-2, -1)[0];

        $('.plan-list').find('.operation').remove();
        self.append('<div class="operation">' + add + edit + remove + '</div>');

        addPlan(currentValue, parentLi);

    });

    /**
     * 添加计划按钮
     * @param currentValue string 当前节点的值
     * @param parentLi object 上级<li>节点
     */
    var addPlan = function(currentValue, parentLi) {
        $('.plan-add').on('click', function() {
            var form = '<input name="title[]" class="plan-add-value" data-parent="' + currentValue + '" value="" placeholder="Title"/>';
            var childUl = parentLi.children('ul');

            var node = '';
            if (childUl.length > 0) {
                node = '<li>' + form + '</li>';
                childUl.prepend(node);
            } else {
                node = '<ul><li>' + form + '</li></ul>';
                parentLi.append(node);
            }

            $('.submit-add').removeClass('hidden');
        });
    };

    var submitAddPlan = function() {
        $('.submit-add-plan').on('click', function() {
            var parentIds = [], titles = [];
            $(".plan-add-value").each(function() {
                var parentId = $(this).data('parent'),
                    title = $(this).val();

                if (parentId && title) {
                    parentIds.push(parentId);
                    titles.push(title);
                }
            });

            $.post(
                $(this).data('url'),
                {parent_ids: parentIds, titles: titles},
                function(result) {console.log('ok了');
                    window.location.reload();
                },
                'json'
            );
        });
    };
    submitAddPlan();

    /**
     * 鼠标移出时删除操作按钮
     */
    $('.plan-item').mouseleave(function() {
        var self = $(this);
        self.find('.operation').remove();
    });


    $('.plan-check').on('click', function() {
        var self = $(this);
        var url = self.val();
        var checked = self.is(':checked');
        var finish = Number(checked);

        $.get(
            url + finish,
            function(result) {
                if (Number(result.finish) === 1 && checked === false) {
                    self.prop('checked', true)
                }
                if (Number(result.finish) === 0 && checked === true) {
                    self.prop('checked', false)
                }
            },
            'json'
        )
    });

    // to remove the short delay on click on touch devices
    FastClick.attach(document.body);
});
