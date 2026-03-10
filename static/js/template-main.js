layui.use(['table', 'form', 'jquery', 'popup', 'common'], function () {
    let table = layui.table
    let form = layui.form
    let $ = layui.jquery
    let popup = layui.popup

    let MODULE_PATH = '/mission/template/'

    let cols = [
        [
            {type: 'checkbox', fixed: 'left'},
            {title: '模板编号', field: 'id', align: 'center', sort: true},
            {title: '模板名称', field: 'template_name', align: 'center', sort: true},
            {title: '创建者', field: 'creator', align: 'center', sort: true},
            {title: '原始SQL模板', field: 'sql_template', align: 'center'},
            {title: '备注', field: 'remark', align: 'center'},
            {title: '更新时间', field: 'update_time', align: 'center', sort: true},
            {title: '任务类型', field: 'template_type',align: 'center', sort: true},
            {title: '操作', toolbar: '#template-bar', align: 'center', width: 240}
        ]
    ]

    table.render({
        elem: '#template-table',
        url: MODULE_PATH + 'data',
        page: true,
        cols: cols,
        skin: 'line',
        toolbar: '#template-toolbar',
        cellExpandedMode: 'tips',
        defaultToolbar: [{
            layEvent: 'refresh',
            icon: 'layui-icon-refresh',
        }, 'filter', 'print', 'exports']
    })

    // 注意：由于Layui的table模块不直接支持自定义的toolbar模板ID，
    // 需要使用表格的tool事件来监听按钮点击。

    // 监听行工具事件
    table.on('tool(template-table)', function (obj) {
        if (obj.event === 'remove') {
            window.remove(obj)
        } else if (obj.event === 'edit') {
            window.edit(obj)
        } else if (obj.event === 'create') {
            window.create(obj)
        }
    })

    table.on('toolbar(template-table)', function (obj) {
        if (obj.event === 'add') {
            window.add()
        } else if (obj.event === 'refresh') {
            window.refresh()
        } else if (obj.event === 'batchRemove') {
            window.batchRemove(obj)
        }
    })
    //查询按钮
    form.on('submit(template_query)', function (data) {
        table.reload('template-table', {where: data.field})
        return false
    })


    window.add = function () {
        layer.open({
            type: 2,
            title: '新增模板',
            shade: 0.1,
            area: ['1200px', '800px'],
            anim: 5, // 0-6 选定动画形式，-1 不开启
            maxmin: true, // 允许全屏最小化
            content: MODULE_PATH + 'add'
        })
    }

    window.create = function (obj) {
        layer.open({
            type: 2,
            title: '新增任务',
            shade: 0.1,
            area: ['1000px', '800px'],
            anim: 2, // 0-6 选定动画形式，-1 不开启
            shadeClose: true, // 点击遮罩区域，关闭弹层
            maxmin: true, // 允许全屏最小化
            content: '/mission/task/add/' + obj.data['id']
        })
    }

    window.edit = function (obj) {
        layer.open({
            type: 2,    // 层类型
            title: '修改模板',
            shade: 0.1, // 遮罩透明度
            shadeClose: true, // 点击遮罩区域，关闭弹层
            area: ['1200px', '800px'],
            maxmin: true, // 允许全屏最小化
            anim: 5, // 0-6 选定动画形式，-1 不开启
            content: MODULE_PATH + 'edit/' + obj.data['id']
        })
    }

    window.remove = function (obj) {
        layer.confirm('确定要删除该任务', {icon: 3, title: '提示'}, function (index) {
            layer.close(index)
            let loading = layer.load()
            $.ajax({
                url: MODULE_PATH + 'remove/' + obj.data['id'],
                dataType: 'json',
                type: 'delete',
                success: function (result) {
                    layer.close(loading)
                    if (result.success) {
                        layer.msg(result.msg, {icon: 1, time: 1000}, function () {
                            obj.del()
                        })
                    } else {
                        layer.msg(result.msg, {icon: 2, time: 1000})
                    }
                },
                error: function() {
                    // 请求失败，给出提示
                    layer.msg('请求失败，请稍后再试！');
                }
            })
        })
    }

    window.batchRemove = function (obj) {
        let data = table.checkStatus(obj.config.id).data
        if (data.length === 0) {
            layer.msg('未选中数据', {
                icon: 3,
                time: 1000
            })
            return false
        }
        var ids = []
        var hasCheck = table.checkStatus('template-table')
        var hasCheckData = hasCheck.data
        if (hasCheckData.length > 0) {
            $.each(hasCheckData, function (index, element) {
                ids.push(element.id)
            })
        }
        console.log(ids)
        layer.confirm('确定要删除选中任务', {
            icon: 3,
            title: '提示'
        }, function (index) {
            layer.close(index)
            let loading = layer.load()
            $.ajax({

                url: MODULE_PATH + 'batchRemove',
                data: {ids: ids},
                dataType: 'json',
                type: 'delete',
                success: function (result) {
                    layer.close(loading)
                    if (result.success) {
                        popup.success(result.msg, function () {
                            table.reload('template-table')
                        })
                    } else {
                        popup.failure(result.msg)
                    }
                }
            })
        })
    }

    window.refresh = function () {
        table.reload('template-table')
    }
})