layui.use(['table', 'form'], function() {
    let table = layui.table;
    let laydate = layui.laydate;
    let form = layui.form;

    let cols = [[
            {title: '文件名', field: 'name', sort: true},
            {title: '大小', field: 'size', templet: d => (d.size/1024).toFixed(2)+' KB', sort: true},
            {title: '创建时间', field: 'ctime', sort: true},
            {title: '操作', toolbar: '#file-bar', width: 100}
        ]]
    table.render({
        elem: '#file-table',
        url: '/file/repository/data',
        page: true,
        cols: cols
    });

    //查询按钮
    form.on('submit(file-query)', function (data) {
        table.reload('file-table', {where: data.field})
        return false
    })

    table.on('tool(file-table)', function(obj){
        if(obj.event === 'download'){
            window.location.href = `/file/repository/download/${obj.data.name}`;
        }
    });

    laydate.render({
        elem: '#ID-laydate-range',
        range: ['#ID-laydate-start-date', '#ID-laydate-end-date'],
        rangeLinked: true
    });
});
