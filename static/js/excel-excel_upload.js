layui.use(['jquery', 'element', 'form', 'upload'], function () {
    var $ = layui.jquery;
    var element = layui.element;
    var form = layui.form;
    var upload = layui.upload;

    var uploadInst = null; // 上传实例

    // 初始化上传组件
    function initUpload() {
        uploadInst = upload.render({
            elem: '#excel-file'
            , url: '/file/excel/upload'
            , auto: false
            , multiple: false // 限制一次只能选择一个文件
            , accept: 'file'
            , exts: 'xls|xlsx|csv'
            , size: 50 * 1024 // 50MB
            , choose: function(obj) {
                // 重置状态
                resetUploadStatus();

                // 先清空之前的文件
                obj.preview(function(index, file, result){
                    // 显示文件信息
                    $('#file-name').text(file.name);
                    $('#file-size').text(formatFileSize(file.size));
                    $('#file-type').text(file.type || '未知');
                    $('#file-info').removeClass('hidden');

                    // 启用上传按钮
                    $('#excel-upload-button').prop('disabled', false);
                });
            }
            , bindAction: '#excel-upload-button'
            , before: function(obj) {
                // 显示上传进度条
                this.data = {
                    description: $('input[name="description"]').val()
                };
                showUploadStatus('正在上传...', 'info');
                $('#excel-upload-button').prop('disabled', true);
                $('#retry-button').hide(); // 隐藏重新上传按钮
            }
            , progress: function(n) {
                // 显示上传进度
                var percent = n + '%';
                showUploadStatus('上传进度: ' + percent, 'info');
            }
            , done: function (res) {
                layer.closeAll();
                if (res.success) {
                    showUploadStatus(res.msg, 'success');
                    setTimeout(function() {
                        try {
                            // 先刷新表格
                            if (window.parent && window.parent.layui && window.parent.layui.table) {
                                window.parent.layui.table.reload('dataTable');
                            }
                        } catch (e) {
                            console.warn('表格刷新失败:', e);
                        }

                        // 然后关闭窗口
                        try {
                            parent.layer.close(parent.layer.getFrameIndex(window.name));
                        } catch (e) {
                            console.warn('窗口关闭失败:', e);
                        }
                    }, 1000);
                } else {
                    showUploadStatus(res.msg, 'error');
                    showRetryButton();
                }
                $('#excel-upload-button').prop('disabled', false);
            }
            , error: function(index, upload) {
                layer.closeAll();
                showUploadStatus('上传失败，网络错误或服务器异常', 'error');
                showRetryButton();
                $('#excel-upload-button').prop('disabled', false);
            }
        });
    }

    // 显示上传状态
    function showUploadStatus(message, type) {
        var $status = $('#upload-status');
        var $message = $('#status-message');

        $status.removeClass('hidden success error');
        $status.addClass(type);
        $message.text(message);
        $status.show();
    }

    // 显示重新上传按钮
    function showRetryButton() {
        $('#retry-button').show();
    }

    // 隐藏重新上传按钮
    function hideRetryButton() {
        $('#retry-button').hide();
    }

    // 重置上传状态
    function resetUploadStatus() {
        $('#upload-status').addClass('hidden').hide();
        hideRetryButton();
        $('#excel-upload-button').prop('disabled', false);
    }

    // 重新上传功能 - 使用官方推荐的 inst.upload() 方法
    $('#retry-button').on('click', function() {
        if (uploadInst) {
            // 重置状态
            resetUploadStatus();

            // 使用官方推荐的重新上传方法
            uploadInst.upload(); // 无需传递参数，自动重新上传已选择的文件
        } else {
            layer.msg('请先选择文件', {icon: 2});
        }
    });

    // 取消按钮点击事件
    $('#cancel-button').on('click', function() {
        parent.layer.close(parent.layer.getFrameIndex(window.name));
    });

    // 初始化上传组件
    initUpload();

    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        var k = 1024;
        var sizes = ['B', 'KB', 'MB', 'GB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
    }
});