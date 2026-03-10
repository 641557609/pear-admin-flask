    layui.use(['form', 'jquery', 'laydate'], function () {

        let form = layui.form
        let $ = layui.jquery
        let laydate = layui.laydate;
        let transfer = layui.transfer;
        const config = window.TASK_CONFIG || {};
        const employees = config.employees || [];
        const selectedEmployees = config.selectedEmployees || [];
        // Excel模板选择切换
        form.on('radio(excel_template_filter)', function(data){
            const useTemplate = data.value === '1';
            const $select = $('select[name="excel_template_id"]');

            $('#excel_template_select').toggle(useTemplate);

            if (useTemplate) {
                // 选择使用模板时，添加必填验证
                $select.attr('lay-verify', 'required');
            } else {
                // 选择不使用时，移除必填验证并清空值
                $select.removeAttr('lay-verify').val('');
            }

            form.render();
        });

        // 初始化Excel模板状态
        const useExcelTemplate = $('input[name="use_excel_template"]:checked').val() === '1';
        const $select = $('select[name="excel_template_id"]');

        $('#excel_template_select').toggle(useExcelTemplate);

        // 根据初始状态设置必填验证
        if (useExcelTemplate) {
            $select.attr('lay-verify', 'required');
        } else {
            $select.removeAttr('lay-verify').val('');
        }
        // 根据变量类型生成内容模块
        form.on('select(var-type)', function (data) {
            const { value: varType } = data;
            const typeName = $(data.elem).attr('name')
            const variableName = typeName.replace('_type', '');
            const container = $(`#${variableName}Container`); // 直接使用模板字符串
            const htmlGenerator = {
                timestamp: () => `
                    <select name="${variableName}_value" lay-verify="required" lay-search>
                        <option value="">请选择动态时间</option>
                        ${['MonthStart:本月初', 'MonthEnd:本月末', 'LastMonthStart:上月初', 'LastMonthEnd:上月末',
                        'NextMonthStart:下月初', 'NextMonthEnd:下月末', 'LastYearToday:去年今天', 'LastYearMonthStart:去年今月月初',
                        'LastYearMonthEnd:去年今月月末', 'LastYearLastMonthStart:去年上月月初', 'LastYearLastMonthEnd:去年上月月末'
                        ]
                            .map(opt => {
                                const [value, text] = opt.split(':');
                                return `<option value="${value}">${text}</option>`;
                            }).join('')}
                    </select>
                `,
                fixed: () => `<input type="text" name="${variableName}_value" lay-verify="required" class="layui-input" placeholder="请输入变量值">`,
                sql: () => `
                    <textarea name="${variableName}_value"
                              class="layui-textarea"
                              placeholder="输入包含&#123;&#123;变量&#125;&#125;的SQL"
                              style="resize: none" lay-verify="required"></textarea>
                `
            };

            // 使用策略模式代替switch-case
            const html = htmlGenerator[varType]?.() || '';

            // 统一更新逻辑
            container.html(html);
            form.render();
        })

        let currentState = {
            mode: config.initialMode || 'by_plan',
            timeConfig: {}
        };

        // 初始化模板系统
        function initTemplates() {
            const container = document.getElementById('config_content');
            const templates = {
                by_plan: document.getElementById('template_by_plan').content.cloneNode(true),
                by_timing: document.getElementById('template_by_timing').content.cloneNode(true),
                by_user: document.getElementById('template_by_user').content.cloneNode(true)
            };
            const timeMode = config.initialTimeMode;

            // 清空容器并注入模板
            container.innerHTML = '';
            Object.entries(templates).forEach(([key, template]) => {
                const wrapper = document.createElement('div');
                wrapper.classList.add('template-item');
                wrapper.style.display = "none";
                wrapper.dataset.mode = key;
                wrapper.appendChild(template);
                container.appendChild(wrapper);
            });

            // 初始化默认显示
            document.querySelector(`[data-mode="${currentState.mode}"]`).style.display = 'block';
            if (currentState.mode === 'by_plan'){
                switch(timeMode) {
                case 'every_hour':
                    renderTimePicker('time', 'HH:mm:ss');
                    break;
                case 'every_day':
                    // 日时间选择器
                    renderTimePicker('time', 'HH:mm:ss');
                    break;
                case 'every_week':
                    // 周时间选择器
                    renderTimePicker('time', 'HH:mm:ss');
                    break;
                case 'every_month':
                    // 月时间选择器
                    renderTimePicker('datetime', 'dd日HH:mm:ss');
                    break;
                }
            }
            else if (currentState.mode === 'by_timing'){
                initDateTimePicker();
            }
        }

        // 日期时间选择器
        function initDateTimePicker() {
            laydate.render({
                elem: '#datetime_picker',
                type: 'datetime',
                fullPanel: true,
                format: 'yyyy-MM-dd HH:mm:ss',
                trigger: 'click',
                done: function(value) {
                    currentState.timeConfig.executionTime = value;
                }
            });
        }


        // 处理模式切换
        form.on('radio(mode_filter)', function(data){
            const mode = data.value;
            currentState.mode = mode;

            // 隐藏所有模板
            document.querySelectorAll('.template-item').forEach(el => {
                el.style.display = 'none';
            });

            // 显示当前模板
            const currentTemplate = document.querySelector(`[data-mode="${mode}"]`);
                if (currentTemplate) {
                    currentTemplate.style.display = 'block';
                    switch(mode) {
                        case 'by_plan':
                            renderTimePicker('time', 'HH:mm:ss', inputHtml);
                            document.getElementById('interval').checked = true
                            document.getElementById('datetime_picker').setAttribute('lay-filter', '')
                            document.getElementById('datetime_picker').setAttribute('name', 'no_picker_time')
                            break;
                        case 'by_timing':
                            document.getElementById('frequency_config').innerHTML = ''
                            document.getElementById('datetime_picker').setAttribute('lay-filter', 'required')
                            document.getElementById('datetime_picker').setAttribute('name', 'picker_time')
                            initDateTimePicker();
                            break;
                        case 'by_user':
                            document.getElementById('frequency_config').innerHTML = ''
                            document.getElementById('datetime_picker').setAttribute('lay-filter', '')
                            document.getElementById('datetime_picker').setAttribute('name', 'no_picker_time')
                            break;
                    }
                }
            form.render();
        });


        // 处理时间模式切换
        form.on('radio(time_filter)', function(data){
            const timeMode = data.value;
            currentState.timeConfig.subMode = timeMode;
            switch(timeMode) {
                case 'every_hour':
                    renderTimePicker('time', 'HH:mm:ss', inputHtml);
                    break;
                case 'every_day':
                    // 日时间选择器
                    renderTimePicker('time', 'HH:mm:ss', inputHtml);
                    break;
                case 'every_week':
                    // 周时间选择器
                    renderTimePicker('time', 'HH:mm:ss', weekHtml + inputHtml);
                    break;
                case 'every_month':
                    // 月时间选择器
                    renderTimePicker('datetime', 'dd日HH:mm:ss', inputHtml);
                    break;
            }
        });

        const inputHtml = `
                            <div class="layui-form-item">
                                <label class="layui-form-label"><b>具体时间</b></label>
                                <div class="layui-input-block">
                                    <input type="text" class="layui-input time-picker" name="picker_time" placeholder="请选择具体时间"  lay-verify="required" readonly>
                                </div>
                            </div>`

        const weekHtml = `
                            <div class="layui-form-item">
                                <label class="layui-form-label"><b>选择时间</b></label>
                                <div class="layui-input-block">
                                    <input type="checkbox" name="weekday" value="mon" title="周一" checked>
                                    <input type="checkbox" name="weekday" value="tue" title="周二" checked>
                                    <input type="checkbox" name="weekday" value="wed" title="周三" checked>
                                    <input type="checkbox" name="weekday" value="thu" title="周四" checked>
                                    <input type="checkbox" name="weekday" value="fri" title="周五" checked>
                                    <input type="checkbox" name="weekday" value="sat" title="周六" checked>
                                    <input type="checkbox" name="weekday" value="sun" title="周日" checked>
                                </div>
                            </div>`;

        //时间选择器渲染
        function renderTimePicker(timeType, format, Html) {
            if (Html) {
                document.getElementById('frequency_config').innerHTML = Html;
            }
            laydate.render({
                elem: '.time-picker',
                type: timeType,
                format: format,
                fullPanel: true,
                trigger: 'click',
                done: function(value) {
                    currentState.timeConfig.executionTime = value;
                }
            });
            form.render();
        }

        // 初始化入口
        initTemplates();


        // 渲染穿梭框
        transfer.render({
            elem: '#transfer-employee',
            id: 'transfer-employee',
            data: employees,
            title: ['候选接收人', '已选接收人'],
            showSearch: true,
            height: 350,
            width:230,
            value:selectedEmployees
        });

        // 指定接收人列
        form.on('switch(column_receiver)', function (){
            if(this.checked){
                document.getElementById('column_name').innerHTML=`
                <input type="text" name="column_name" class="layui-input" lay-verify="required" placeholder="请输入需要指定的列名">
                `
            }else{
                document.getElementById('column_name').innerHTML = '';
            }
        })

        form.on('submit(task-save)', function (data) {
            let selected_employees = {};
            //获取选中发送人
            if(document.getElementById('transfer-employee')){
                selected_employees = transfer.getData('transfer-employee');
            }
            const checkboxes = document.querySelectorAll('input[name="weekday"]');
            const selected_values = [];
            checkboxes.forEach((checkbox) => {
                if (checkbox.checked) {
                    // 如果被选中，将值添加到数组中
                    selected_values.push(checkbox.value);
                }
            });
            $.ajax({
                url: '/mission/task/update',
                data: JSON.stringify({"data_field":data.field, "selected_employees":selected_employees, "week":selected_values}),
                dataType: 'json',
                contentType: 'application/json',
                type: 'post',
                success: function (result) {
                    if (result.success) {
                        layer.msg(result.msg, {icon: 1, time: 1000}, function () {
                            parent.layer.close(parent.layer.getFrameIndex(window.name))//关闭当前页
                            parent.layui.table.reload('task-table')
                        })
                    } else {
                        layer.msg(result.msg, {icon: 2, time: 1000})
                    }
                }
            })
            return false
        })

        $('#cancel').on('click', function(){
            parent.layer.close(parent.layer.getFrameIndex(window.name))//关闭当前页
            return false;
        })
    })