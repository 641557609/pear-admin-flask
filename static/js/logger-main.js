layui.use(['table', 'form', 'jquery', 'popup', 'common'], function () {
    let table = layui.table
    let form = layui.form
    let $ = layui.jquery
    let popup = layui.popup
    let laydate = layui.laydate;
    let MODULE_PATH = '/mission/logger/'

    let cols = [
        [
            {type: 'checkbox', fixed: 'left'},
            {title: '日志编号', field: 'logger_id', align: 'center', sort: true},
            {title: '任务编号', field: 'task_id', align: 'center', sort: true},
            {title: '任务名称', field: 'task_name', align: 'center', width: 100, sort: true},
            {title: '触发方式', field: 'trigger_mode', align: 'center', sort: true},
            {title: '运行结果', field: 'status', align: 'center', sort: true},
            {title: '文件路径', field: 'result_path', align: 'center'},
            {title: '执行耗时（秒）', field: 'execution_time',align: 'center', sort: true},
            {title: '执行时间', field: 'run_time', align: 'center'},
            {title: '操作', toolbar: '#logger-bar', align: 'center', width: 240}
        ]
    ]

    table.render({
        elem: '#logger-table',
        url: MODULE_PATH + 'data',
        page: true,
        cols: cols,
        skin: 'line',
        toolbar: '#logger-toolbar',
        defaultToolbar: [{
            layEvent: 'refresh',
            icon: 'layui-icon-refresh',
        }, 'filter', 'print', 'exports']
    })

    // 注意：由于Layui的table模块不直接支持自定义的toolbar模板ID，
    // 需要使用表格的tool事件来监听按钮点击。

    // 监听行工具事件
    table.on('tool(logger-table)', function (obj) {
        if (obj.event === 'remove') {
            window.remove(obj)
        } else if (obj.event === 'detail') {
            window.detail(obj)
        }
    })

    table.on('toolbar(logger-table)', function (obj) {
        if (obj.event === 'refresh') {
            window.refresh()
        } else if (obj.event === 'batchRemove') {
            window.batchRemove(obj)
        }
    })
    //查询按钮
    form.on('submit(logger-query)', function (data) {
        table.reload('logger-table', {where: data.field})
        return false
    })


    window.detail = function (obj) {
        layer.open({
            type: 2,
            title: '日志详情',
            shade: 0.1,
            area: ['1200px', '800px'],
            anim: 1, // 0-6 选定动画形式，-1 不开启
            shadeClose: true, // 点击遮罩区域，关闭弹层
            maxmin: true, // 允许全屏最小化
            content: MODULE_PATH + 'detail/' + obj.data['logger_id'],
        })
    }

    window.remove = function (obj) {
        layer.confirm('确定要删除该日志', {icon: 3, title: '提示'}, function (index) {
            layer.close(index)
            let loading = layer.load()
            $.ajax({
                url: MODULE_PATH + 'remove/' + obj.data['logger_id'],
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
        var hasCheck = table.checkStatus('logger-table')
        var hasCheckData = hasCheck.data
        if (hasCheckData.length > 0) {
            $.each(hasCheckData, function (index, element) {
                ids.push(element.logger_id)
            })
        }
        console.log(ids)
        layer.confirm('确定要删除选中日志', {
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
                            table.reload('logger-table')
                        })
                    } else {
                        popup.failure(result.msg)
                    }
                }
            })
        })
    }
    // 日期范围 - 左右面板独立选择模式
    laydate.render({
        elem: '#ID-laydate-range',
        range: ['#ID-laydate-start-date', '#ID-laydate-end-date'],
        rangeLinked: true
    });
    window.refresh = function () {
        table.reload('logger-table')
    }
})