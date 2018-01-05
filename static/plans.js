$(document).ready(function() {
    /**
     * 弹出显示提示信息
     * @param message
     * @param danger
     */
    var promptMsg = function(message, danger) {
        danger = (danger === true) ? 'alert-danger' : 'alert-success';
        $('<div>').appendTo('body').addClass('alert ' + danger).html(message).show().delay(1500).fadeOut();
    };



    /**
     * 点击内容区域显示添加、编辑、删除计划按钮
     */
    $('.plan-title').on('click', function(event) {
        event.stopPropagation();
        var self = $(this);
        var parentLi = self.parent().parent('li');
        var planItem = parentLi.children('.plan-item');
        var planTitle = planItem.children('.plan-title');
        var currentValue = parentLi.find('.plan-check').val().split('/').slice(-2, -1)[0];

        editPlan(planTitle);
        showOperation(planItem);
        addPlan(currentValue, parentLi);
        removePlan(currentValue, parentLi);
    });

    /**
     * 显示操作按钮（save、add、delete）
     */
    var showOperation = function(planItem) {
        var edit = ' <span class="plan-save btn btn-success btn-xs small">Save</span> ';
        var add = ' <span class="plan-add btn btn-primary btn-xs small">Add</span> ';
        var remove = ' <span class="plan-remove btn btn-danger btn-xs small">Delete</span>';

        $('.plan-list').find('.operation').remove();
        planItem.append('<div class="operation">' + edit + add + remove + '</div>');
    };

    /**
     * 点击其他区域隐藏操作按钮
     */
    $(document).on('click', function(event) {
        $(this).find('.operation').remove();
        console.log(event);
        resetTitleForm();
    });

    /**
     * 添加计划按钮
     * @param currentValue string 当前节点的值
     * @param parentLi object 上级<li>节点
     */
    var addPlan = function(currentValue, parentLi) {
        $('.plan-add').on('click', function(event) {
            event.stopPropagation();
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

    /**
     * 保存新增的计划
     */
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
            function(result) {
                if (result.status) {
                    promptMsg('Success.');
                    setTimeout(function() {
                        window.location.reload();
                    }, 1500)
                } else {
                    promptMsg('Failed.', true);
                }
            },
            'json'
        ).fail(function() { promptMsg('Failed.', true); });
    });


    /**
     * 删除计划
     * @param currentValue
     * @param parentLi object 上级<li>节点
     */
    var removePlan = function(currentValue, parentLi) {
        $('.plan-remove').on('click', function() {
            var childUl = parentLi.children('ul');
            var message = childUl.length > 0 ? 'Delete this item and its children?' : 'Delete?';
            var yes = confirm(message);

            if (yes) {
                $.get(
                    '/plan_delete/' + currentValue,
                    function(result) {
                        if (result.status) {
                            promptMsg('Success.');
                            parentLi.remove();
                        } else {
                            promptMsg('Failed.', true);
                        }
                    },
                    'json'
                ).fail(function() { promptMsg('Failed.', true); });
            }
        });
    };


    /**
     * 勾选或取消计划
     */
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

/*    $('.plan-title').on('click', function() {
        editPlan($(this));
    });*/

    /**
     * 显示编辑form
     * @param planTitle .plan-title对象
     */
    var editPlan = function(planTitle) {
        var url = planTitle.data('url'),
            value= planTitle.html();

        var form = '<input name="title" class="plan-title-value" value="' + value + '" />';

        resetTitleForm();
        planTitle.hide();
        planTitle.before(form);

        $('.plan-save').on('click', function() {
            $.post(
                url,
                {title: $('.plan-title-value').val()},
                function(restult) {
                    console.log('result')
                },
                'json'
            );
        })
    };

    //$('.plan-title-value').on('click', function(event) {event.stopPropagation();});

    /**
     * 重置编辑输入框
     */
    var resetTitleForm = function() {
        $('.plan-title').show();
        $('.plan-title-value').remove();
    }
});
