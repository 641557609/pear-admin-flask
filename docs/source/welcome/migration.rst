.. _migration:

从旧项目迁移
=================

由于 `Pear Admin Layui <https://gitee.com/pear-admin/pear-admin-layui>`_ 框架（下面将会称其为 “主项目”）的更新获得了更好的性能与新的功能，
此项目 Pear Admin Flask 作为主项目的附属项目将会在一定时间进行迁移与同步。由于主项目的更新，此项目的部分功能被弃用这大大增加了同步的难度，所以在一段时间
内，此项目并未有同步的打算。为了获得性能更新，此项目于 2025 的新年前后开始逐步将项目代码进行同步与完善，迫不得已舍去了部分功能，这为以往基于此项目的作品更新
加大了难度，所以便有了此迁移章节。各位开发者，如果您想要同步自己原先以项目为基础的作品，请阅读该章节。

.. _migration1:

迁移到 v2.0.0-4.0.5 版本
----------------------------

更正验证码生成模块引用
~~~~~~~~~~~~~~~~~~~~~~

由于 ``applications/common/utils/gen_captcha.py`` 更名为 ``applications/common/utils/captcha.py`` ，需要修改导入引用。

例如：

.. code-block:: python

    from applications.common.utils.gen_captcha import vieCode

更正为：

.. code-block:: python

    from applications.common.utils.captcha import vieCode


后台首页路径修改
~~~~~~~~~~~~~~~~~~~~~~

由于为了对齐主项目，``system/console/console.html`` 更名为 ``system/analysis/main.html``，前端页面需要进行修改。

例如：

.. code-block:: html

    <a href="system/console/console.html"></a>

更正为：

.. code-block:: html

    <a href="system/analysis/main.html"></a>


公用模板修改
~~~~~~~~~~~~~~~~~~~~~~~~

移除了 ``templates/system/common/memory.html`` ，该文件原先仅用于系统监控页面，现在换为 JavaScript 函数进行换算。
详情参阅模板文件 ``templates/system/monitor.html``


移除 Pear Button 模块
~~~~~~~~~~~~~~~~~~~~~~~~

由于主项目不再使用 Pear Button 而直接使用 Layui Button。所以需要将所有的按钮 class 中的 “pear-btn” 变为 “layui-btn”。
（附属的 pear-btn-* 也要修改，建议是直接搜索替换。）


例如：

.. code-block:: html

    <button class="pear-btn pear-btn-primary pear-btn-md" lay-submit lay-filter="dept-query">
        <i class="layui-icon layui-icon-search"></i>
        查询
    </button>
    <button type="reset" class="pear-btn pear-btn-md">
        <i class="layui-icon layui-icon-refresh"></i>
        重置
    </button>

改为：

.. code-block:: html

    <button class="layui-btn layui-btn-md" lay-submit lay-filter="dept-query">
        <i class="layui-icon layui-icon-search"></i>
        查询
    </button>
    <button type="reset" class="layui-btn layui-btn-primary layui-btn-md">
        <i class="layui-icon layui-icon-refresh"></i>
        重置
    </button>

.. tip::

    你会注意到修改之后的 layui-btn-primary 属性添加在了 “重置” 按钮上，而不是 “查询” 按钮上，
    这是因为 layui-btn-primary 是默认白色的，而不加 layui-btn-primary 属性是跟随主题色的。这里需要特别注意一下。

合并日志模块
~~~~~~~~~~~~~~~~~~~~

为了减少冗余，将 applications/common/admin_log.py 与 applications/common/admin.py 合并，仅留下 applications/common/admin.py 。


例如：

.. code-block:: python

    from applications.common.admin_log import admin_log

改为：

.. code-block:: python

    from applications.common.admin import admin_log

验证码生成路由修改
~~~~~~~~~~~~~~~~~~~~~~~~

为了优化代码，将验证码生成路由改为了 system.passport.captcha 。这主要会影响前端模板渲染。

例如：

.. code-block:: html

    url_for('system.passport.get_captcha')

改为：

.. code-block:: python

    url_for('system.passport.captcha')
