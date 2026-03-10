layui.use(['table', 'form', 'jquery', 'popup', 'common'], function () {
    let table = layui.table
    let form = layui.form
    let $ = layui.jquery
    let popup = layui.popup

    let MODULE_PATH = '/mission/task/'

    let cols = [
        [
            {type: 'checkbox', fixed: 'left'},
            {title: '任务编号', field: 'task_id', align: 'center', sort: true},
            {title: '任务名称', field: 'task_name', align: 'center', width: 100, sort: true},
            {title: '模板名称', field: 'template_name', align: 'center', sort: true},
            {title: '模板类型', field: 'template_type', align: 'center', sort: true},
            {title: '触发方式', field: 'trigger_mode', align: 'center', sort: true},
            {title: '任务开启/关闭', field: 'enable', align: 'center', templet: '#task-enable'},
            {title: '接收人', field: 'receiver', align: 'center'},
            {title: '执行时间', field: 'run_time',align: 'center', sort: true},
            {title: '操作', toolbar: '#task-bar', align: 'center', width: 240}
        ]
    ]

    table.render({
        elem: '#task-table',
        url: MODULE_PATH + 'data',
        page: true,
        cols: cols,
        skin: 'line',
        toolbar: '#task-toolbar',
        defaultToolbar: [{
            layEvent: 'refresh',
            icon: 'layui-icon-refresh',
        }, 'filter', 'print', 'exports']
    })

    // 注意：由于Layui的table模块不直接支持自定义的toolbar模板ID，
    // 需要使用表格的tool事件来监听按钮点击。

    // 监听行工具事件
    table.on('tool(task-table)', function (obj) {
        if (obj.event === 'remove') {
            window.remove(obj)
        } else if (obj.event === 'edit') {
            window.edit(obj)
        } else if (obj.event === 'run') {
            window.run(obj)
        }
    })

    table.on('toolbar(task-table)', function (obj) {
        if (obj.event === 'add') {
            window.add()
        } else if (obj.event === 'refresh') {
            window.refresh()
        } else if (obj.event === 'batchRemove') {
            window.batchRemove(obj)
        }
    })
    //查询按钮
    form.on('submit(task-query)', function (data) {
        table.reload('task-table', {where: data.field})
        return false
    })

    form.on('switch(task-enable)', function (obj) {
        let operate
        if (obj.elem.checked) {
            operate = 'enable'
        } else {
            operate = 'disable'
        }
        let loading = layer.load()
        $.ajax({
            url: MODULE_PATH + operate,
            data: JSON.stringify({task_id: this.value}),
            dataType: 'json',
            contentType: 'application/json',
            type: 'put',
            success: function (result) {
                layer.close(loading)
                if (result.success) {
                    layer.msg(result.msg, {icon: 1, time: 1000})
                } else {
                    layer.msg(result.msg, {icon: 2, time: 1000})
                }
                table.reload('task-table')
            },
            error: function() {
                layer.close(loading)
                // 请求失败，给出提示
                layer.msg('请求失败，请稍后再试！');
            }
        })
    })

    window.add = function () {
        layer.open({
            type: 2,
            title: '新增任务',
            shade: 0.1,
            area: ['1000px', '800px'],
            anim: 2, // 0-6 选定动画形式，-1 不开启
            shadeClose: true, // 点击遮罩区域，关闭弹层
            maxmin: true, // 允许全屏最小化
            content: MODULE_PATH + 'add'
        })
    }

    // window.run = function (obj) {
    //     // 显示“正在运行”弹窗（1秒后自动关闭）
    //     let loading = layer.msg('正在运行...', {
    //         icon: 16,        // 加载图标
    //         time: 200,      // 0.5秒后自动关闭
    //         shade: 0.3       // 遮罩透明度
    //     });
    //
    //     // 异步调用后端接口
    //     $.ajax({
    //         url: MODULE_PATH + 'run/' + obj.data['task_id'],
    //         type: 'POST',
    //         success: function (result) {
    //             layer.close(loading);
    //             if (result.success) {
    //                 layer.msg(result.msg, {icon: 1, time: 1000});
    //             } else {
    //                 layer.msg(result.msg, {icon: 2, time: 2000});
    //             }
    //         },
    //         error: function () {
    //             layer.msg('请求失败，请检查网络', {icon: 2, time: 2000});
    //         }
    //     });
    // }
    window.run = function (obj) {
        // 判断任务类型，只有查询类型才显示撤回确认
        if (obj.data['template_type'] === '查询语句') {
            // 显示撤回确认对话框
            layer.confirm('检测到这是查询任务，是否撤回上次发送的文件？', {
                title: '文件撤回确认',
                btn: ['撤回并运行', '直接运行', '取消'],
                btn1: function(index) {
                    // 用户选择"撤回并运行"
                    layer.close(index);
                    executeRunTask(obj.data['task_id'], true);
                },
                btn2: function(index) {
                    // 用户选择"直接运行"
                    layer.close(index);
                    executeRunTask(obj.data['task_id'], false);
                },
                btn3: function(index) {
                    // 用户选择"取消"
                    layer.close(index);
                    // 不执行任何操作
                }
            });
        } else {
            // 非查询任务，直接运行
            executeRunTask(obj.data['task_id'], false);
        }
    }

    // 封装任务运行逻辑
    function executeRunTask(taskId, revokeLastFiles) {
        // 显示"正在运行"弹窗（1秒后自动关闭）
        let loading = layer.msg('正在运行...', {
            icon: 16,        // 加载图标
            time: 200,      // 0.5秒后自动关闭
            shade: 0.3       // 遮罩透明度
        });

        // 异步调用后端接口，带上撤回参数
        $.ajax({
            url: MODULE_PATH + 'run/' + taskId,
            type: 'POST',
            data: JSON.stringify({
                revoke_last_files: revokeLastFiles
            }),
            contentType: 'application/json',
            success: function (result) {
                layer.close(loading);
                if (result.success) {
                    layer.msg(result.msg, {icon: 1, time: 1000});
                } else {
                    layer.msg(result.msg, {icon: 2, time: 2000});
                }
            },
            error: function () {
                layer.close(loading);
                layer.msg('请求失败，请检查网络', {icon: 2, time: 2000});
            }
        });
    }

    window.edit = function (obj) {
        layer.open({
            type: 2,    // 层类型
            title: '修改任务',
            shade: 0.1, // 遮罩透明度
            shadeClose: true, // 点击遮罩区域，关闭弹层
            area: ['1000px', '800px'],
            maxmin: true, // 允许全屏最小化
            anim: 3, // 0-6 选定动画形式，-1 不开启
            content: MODULE_PATH + 'edit/' + obj.data['task_id']
        })
    }

    window.remove = function (obj) {
        layer.confirm('确定要删除该任务', {icon: 3, title: '提示'}, function (index) {
            layer.close(index)
            let loading = layer.load()
            $.ajax({
                url: MODULE_PATH + 'remove/' + obj.data['task_id'],
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
        var hasCheck = table.checkStatus('task-table')
        var hasCheckData = hasCheck.data
        if (hasCheckData.length > 0) {
            $.each(hasCheckData, function (index, element) {
                ids.push(element.task_id)
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
                            table.reload('task-table')
                        })
                    } else {
                        popup.failure(result.msg)
                    }
                }
            })
        })
    }

    window.refresh = function () {
        table.reload('task-table')
    }
})