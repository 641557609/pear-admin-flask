.. _update:

更新日志
================

此章节展示更新说明。

版本号说明
----------------------

版本号由主版本号、次版本号、修订号和 Pear Admin Layui 版本号组成。

2025 年 1 月 26 日（v2.0.0-4.0.5）
------------------------------------

.. important::

    同步与迁移查看 :ref:`migration1` 章节。

* 权限管理（后台框架）增加 组件（_component） 打开方式，根据 Pear Admin Layui ，此方式将会将目标页面作为 div 嵌入框架内部。
* 权限管理完善批量删除的功能（先前没有实现）。
* 增加 权限管理、角色管理 等添加、更新路由的参数效验。（先前参数输错会导致程序崩溃）
* 修改增加编辑页面中的 sort（排序） 参数的输入框为数字输入。
* 修改编辑页面的默认留空文本。将默认的“请输入标题”改为更合理的内容。
* 修改了权限名称中对于 “权限编辑” 权限的标注错误。
* 修复没有子部门的公司无法删除的问题
* 修复操作日志和登录日志接口查询相反和接口匹配错误的问题
* 系统监控改为异步操作，并完善系统监控的功能
* 删除字典时会一并删除字典值（特性更新）
* 流程修改，超级管理员也会被记录日志
* 修复邮件发送设置后台路由错误的问题
* 后台首页文件修改，system/console/console.html --> system/analysis/main.html
* 验证码生成模块重命名 gen_captcha --> captcha
* 移除文件 system/common/memory.html（此原先仅作用于系统监控）
* 移除前端框架模块 botton.js （pear-btn） ，故前端页面中的 pear-btn 需要替换为 layui-btn ( 直接搜索替换，其附属的 pear-btn- 都要替换* )
* 保留了前端框架中未使用的模块（在 Pear Admin Layui 已经移除），但是默认不启用，需要自行在 static/system/component/pear/pear.js 和 static/system/component/pear/css/pear.css 添加
* 加入了程序缓存模块，applications/common/utils/cache.py
* 增加后台消息接口
* 系统监控中对硬盘的获取，如果是在 docker 中就获取根目录的数据
* 更正登录之后重定向由于路由更改从而设置错误的问题
* 将 applications/common/admin_log.py 与 applications/common/admin.py 合并，仅留下 applications/common/admin.py
* 优化代码结构，新增函数 `normal_log` 减少代码复用
* 添加了新插件的事件
* 修改了验证码生成路由
* 为 ModelFilter 增加了字符转义

已知问题以及解决方式
~~~~~~~~~~~~~~~~~~~~~~~

主项目 Pear Admin Layui 存在如下的问题：

* 对于组件式嵌入页面（_component），存在 JavaScript 无法解绑的问题，由于无法解除 JavaScript 注册，可能会因为不同页面的同标识的按钮绑定到同一个事件。
* 主项目无法对子页面（iframe）同步更新主题色和修改夜间模式。
* 主项目无法刷新以 iframe 嵌入的子页面。

对此给出的解决方法如下：

* 仅后台主页和个人资料页面使用组件方式嵌入，其余使用 iframe 嵌入。
* 在框架中添加 JavaScript 脚本，用于通知所有子 iframe 改变颜色。
* 修改 admin.js 并提交 PR，等待主项目合并。