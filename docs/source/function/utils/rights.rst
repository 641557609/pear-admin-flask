.. _权限验证模块:

:mod:`rights` -- 权限验证模块
==================================

:mod:`rights` 模块源代码在文件 `applications/common/utils/rights.py` 下，主要用于权限验证。

.. module:: rights

函数
---------------

.. function:: authorize(power: str, log: bool = False)

    用户权限判断，用于判断目前会话用户是否拥有访问权限。此函数是一个修饰器，可用于修饰视图函数。
    在模板中有与之对应的全局非修饰函数 authorize ，此函数定义位于 `applications/extensions/init_template_directives.py` 。
    示例中将会展示两种方式的用法。

    :param power: 权限标识
    :type power: str
    :param log: 是否记录日志，默认为 False
    :type log: bool, optional

    **修饰函数示例：**

    .. code-block:: python

        from applications.common.utils.rights import authorize

        @app.route("/test")
        @authorize("system:power:remove", log=True)
        def test_index():
            return 'You are allowed.'


    **在前端模板中：**

    .. code-block:: html

        {% if authorize("system:user:edit") %}
            <button class="pear-btn pear-btn-primary pear-btn-sm" lay-event="edit">
            <i class="pear-icon pear-icon-edit"></i>
            </button>
        {% endif %}


    .. important::

        `if authorize("system:user:edit")` 的方式仅适用于 **前端模板渲染** ，不得用于后端代码判断。
        如果后端想要使用，请使用 **power in session.get('permissions')** 来判断， `power` 是 `权限标识` 。

        .. code-block:: python

            from flask import session

            ...

            @bp.get('/test')
            def test():
                if 'system:user:edit' in session.get('permissions'):
                    ...

                ...


