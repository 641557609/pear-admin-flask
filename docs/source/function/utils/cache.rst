:mod:`cache` -- 应用缓存模块
================================

:mod:`cache` 模块源代码在文件 `applications/common/utils/cache.py` 下，主要用于简单的程序数据缓存。

目前此模块仅启用应用程序缓存，暂时没有联动 Redis 等数据库缓存的功能，后续有意向添加。您可以在自己的项目中添加相关的函数，当然也非常欢迎提交 PR ，一起完善项目。

.. warning::

    此模块目前仅用于简单的缓存记录，不能记录大量的、持久的缓存。缓存内容存在内存中，在程序结束后清空！具体的例子是 `系统监控` 页面，用于缓存 5 秒内的 CPU 与内存
    的监控数据。

.. module:: cache

变量
-----------

.. py:data:: cache_dict

    一个字典，用于存放缓存数据与缓存的过期时间戳。

函数
-----------

.. function:: cache_set_internal(key, value, expired=5)

    程序内部实现的记录缓存，用于简单、体量不大的缓存记录，在程序结束后销毁。对于高速、体量大的环境请配置 Redis 等服务自行记录。
    记录缓存，存储键值对，并记录当前时间作为缓存的时间戳。

    :param key: 键
    :param value: 值
    :param expired: 过期时间（秒），默认5秒

.. function:: cache_get_internal(key)

    获取缓存，根据键从缓存中获取值，并检查是否过期。

    :param key: 键
    :return: 如果缓存存在且未过期，返回缓存的值；否则返回 None

.. function:: cache_auto_internal(key, call, expired=5)

    如果缓存存在直接返回缓存内容，缓存不存在或者过期执行 call 函数，并取得返回值记录并返回。

    :param key: 键
    :param call: 获取新值的地方
    :param expired: 过期时间（秒），默认5秒

    **示例：**

    .. code-block:: python

        from application.common.utils.cache import cache_auto_internal

        def fetch_data():
            # 模拟从数据库或接口获取数据
            return "new_data"

        # 使用 cache_auto_internal 获取缓存或调用 fetch_data 获取新值
        result = cache_auto_internal("my_key", fetch_data, expired=10)
        print(result)  # 输出: "new_data"（如果缓存不存在或已过期）