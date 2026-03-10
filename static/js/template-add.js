layui.use(['form', 'jquery', 'layer'], function () {
    let form = layui.form
    let $ = layui.jquery
    let layer = layui.layer
    form.on('submit(template-save)', function (data) {
        $.ajax({
            url: '/mission/template/save',
            data: JSON.stringify(data.field),
            dataType: 'json',
            contentType: 'application/json',
            type: 'post',
            success: function (result) {
                if (result.success) {
                    layer.msg(result.msg, {icon: 1, time: 1000}, function () {
                        parent.layer.close(parent.layer.getFrameIndex(window.name))//关闭当前页
                        parent.layui.table.reload('template-table')
                    })
                } else {
                    layer.msg(result.msg, {icon: 2, time: 1000})
                }
            }
        })
        return false
    })

    // 变量提取功能
    $('#extract-variables').on('click', function() {
        const sqlTemplate = $('#sql_template').val();

        if (!sqlTemplate.trim()) {
            layer.msg('请先输入SQL模板', {icon: 2, time: 2000});
            return;
        }

        // 提取变量：匹配 {{变量名}} 格式
        const variablePattern = /\{\{\s*([^}]+)\s*\}\}/g;
        const variables = [];
        let match;

        while ((match = variablePattern.exec(sqlTemplate)) !== null) {
            const variableName = match[1].trim();
            if (!variables.includes(variableName)) {
                variables.push(variableName);
            }
        }

        if (variables.length === 0) {
            layer.msg('未检测到变量，请检查SQL模板中是否包含 {{变量名}} 格式的变量', {icon: 0, time: 3000});
            $('#variables-container').hide();
            return;
        }

        // 显示提取的变量
        $('#variables-container').show();
        const variablesHtml = variables.map((variable, index) =>
            `<div class="layui-row" style="margin-bottom: 10px; padding: 8px; background: #f8f8f8; border-radius: 4px;">
                <div class="layui-col-md8">
                    <strong>变量${index + 1}:</strong> <code style="color: #009688;">${variable}</code>
                </div>
                <div class="layui-col-md4">
                    <span class="layui-badge layui-bg-blue">已检测</span>
                </div>
            </div>`
        ).join('');

        $('#variables-list').html(variablesHtml);

        layer.msg(`成功提取 ${variables.length} 个变量`, {icon: 1, time: 2000});
    });
    // SQL模板输入时自动隐藏变量列表
    $('#sql_template').on('input', function() {
        $('#variables-container').hide();
    });

    $('#cancel').on('click', function(){
        parent.layer.close(parent.layer.getFrameIndex(window.name))//关闭当前页
        return false;
    })
})