:mod:`admin` -- 后台函数模块
=======================================

:mod:`admin` 模块源代码在文件 `applications/common/admin.py` 下，主要集结了一些常用的后台需要频繁调用的函数。

.. module:: admin

函数
-------------

.. function:: get_captcha()

    生成验证码图片及其对应的验证码字符串。

    :return: 返回验证码图片的响应对象和验证码字符串。

    **示例：**

    .. code-block:: python

        from applications.common.admin import get_captcha

        @bp.get('/getCaptcha')
        def captcha():
            resp, code = get_captcha()
            session["code"] = code
            return resp


.. function:: normal_log(method, url, ip, user_agent, desc, uid, is_access)

   记录通用日志信息到数据库。

   :param method: 请求方法（如 GET、POST）。
   :param url: 请求的 URL。
   :param ip: 客户端的 IP 地址。
   :param user_agent: 客户端的 User-Agent 信息。
   :param desc: 日志描述信息。
   :param uid: 用户 ID。
   :param is_access: 是否成功访问（True 或 False）。
   :return: 返回日志记录的 ID。


.. function:: login_log(request, uid, is_access)

    记录用户登录日志。

    :param request: Flask 请求对象。
    :param uid: 用户 ID。
    :param is_access: 是否成功登录（True 或 False）。
    :return: 返回日志记录的 ID。


.. function:: admin_log(request, is_access, desc=None)

   记录管理员操作日志。

   :param request: Flask 请求对象。
   :param is_access: 是否成功操作（True 或 False）。
   :param desc: 日志描述信息（可选）。如果未提供，则从请求数据中提取。
   :return: 返回日志记录的 ID。