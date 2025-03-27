.. _JSON 响应正文生成模块:

:mod:`http` -- JSON 响应正文生成模块
=======================================

:mod:`http` 模块源代码在文件 `applications/common/utils/http.py` 下，主要用于生成 JSON 格式的响应正文。

对于大部分 JSON 格式响应的数据，请尽量遵循响应格式规范。如此方便后续前后端的分离和项目的构建。

.. module:: http

函数
------------

.. function:: success_api(msg: str = "成功")

    返回成功的 API 响应。

    :param msg: 成功消息内容，默认为 "成功"。
    :return: 返回 JSON 格式的响应，包含 `success` 和 `msg` 字段。


.. function:: fail_api(msg: str = "失败")

    返回失败的 API 响应。

    :param msg: 失败消息内容，默认为 "失败"。
    :return: 返回 JSON 格式的响应，包含 `success` 和 `msg` 字段。


.. function:: table_api(msg: str = "", count=0, data=None, limit=10)

    返回动态表格渲染所需的 API 响应。

    :param msg: 响应消息内容，默认为空字符串。
    :param count: 数据总数，默认为 0。
    :param data: 表格数据，默认为 None。
    :param limit: 每页数据条数，默认为 10。
    :return: 返回 JSON 格式的响应，包含 `msg`、`code`、`data`、`count` 和 `limit` 字段。

**示例：**

.. code-block:: python

    from applications.common.utils.http import success_api, fail_api

    @bp.get('/init')
    def init():
        if ...:
            return success_api(msg="初始化成功")
        return fail_api(msg="初始化失败")

.. code-block:: python

    from applications.common.utils.http import table_api

    @bp.get('/data')
    def data():
        return table_api(data=[], total=0)
