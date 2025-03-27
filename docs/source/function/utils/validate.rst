:mod:`validate` -- 效验模块
==================================

:mod:`validate` 模块源代码在文件 `applications/common/utils/validate.py` 下，主要用于数据效验与过滤。

.. module:: validate

函数
-------------

.. function:: str_escape(s)

   对字符串进行 XSS 过滤，返回转义后的安全字符串。

   :param s: 需要转义的字符串。
   :return: 返回转义后的字符串，如果输入为空则返回 None。


.. function:: between(*args, **kwargs)

   验证数字是否介于最小值和最大值之间。
   适用于整数、浮点数、小数和日期等类型。

   :param value: 需要验证的数字。
   :param min: 数字的最小值（可选）。
   :param max: 数字的最大值（可选）。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import between

      between(5, min=2)  # True
      between(13.2, min=13, max=14)  # True
      between(500, max=400)  # ValidationFailure(func=between, args=...)


.. function:: domain(*args, **kwargs)

   验证给定值是否为有效的域名。

   :param value: 需要验证的域名字符串。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import domain

      domain('example.com')  # True
      domain('example.com/')  # ValidationFailure(func=domain, ...)


.. function:: email(*args, **kwargs)

   验证给定值是否为有效的电子邮件地址。

   :param value: 需要验证的电子邮件地址。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import email

      email('someone@example.com')  # True
      email('bogus@@')  # ValidationFailure(func=email, ...)


.. function:: iban(*args, **kwargs)

   验证给定值是否为有效的 IBAN 代码。

   :param value: 需要验证的 IBAN 代码。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import iban

      iban('DE29100500001061045672')  # True
      iban('123456')  # ValidationFailure(func=iban, ...)


.. function:: ipv4(*args, **kwargs)

   验证给定值是否为有效的 IPv4 地址。

   :param value: 需要验证的 IPv4 地址。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import ipv4

      ipv4('123.0.0.7')  # True
      ipv4('900.80.70.11')  # ValidationFailure(func=ipv4, args={'value': '900.80.70.11'})


.. function:: ipv6(*args, **kwargs)

   验证给定值是否为有效的 IPv6 地址。

   :param value: 需要验证的 IPv6 地址。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import ipv6

      ipv6('abcd:ef::42:1')  # True
      ipv6('abc.0.0.1')  # ValidationFailure(func=ipv6, args={'value': 'abc.0.0.1'})


.. function:: length(*args, **kwargs)

   验证给定字符串的长度是否在指定范围内。

   :param value: 需要验证的字符串。
   :param min: 字符串的最小长度（可选）。
   :param max: 字符串的最大长度（可选）。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import length

      length('something', min=2)  # True
      length('something', min=9, max=9)  # True
      length('something', max=5)  # ValidationFailure(func=length, ...)


.. function:: mac_address(*args, **kwargs)

   验证给定值是否为有效的 MAC 地址。

   :param value: 需要验证的 MAC 地址。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import mac_address

      mac_address('01:23:45:67:ab:CD')  # True
      mac_address('00:00:00:00:00')  # ValidationFailure(func=mac_address, args={'value': '00:00:00:00:00'})


.. function:: slug(*args, **kwargs)

   验证给定值是否为有效的 Slug 格式。
   有效的 Slug 只能包含字母数字字符、连字符和下划线。

   :param value: 需要验证的字符串。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import slug

      slug('my.slug')  # ValidationFailure(func=slug, args={'value': 'my.slug'})
      slug('my-slug-2134')  # True


.. function:: url(*args, **kwargs)

   验证给定值是否为有效的 URL。

   :param value: 需要验证的 URL。
   :param public: 是否仅允许公共 URL（可选）。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import url

      url('http://foobar.dk')  # True
      url('http://10.0.0.1')  # True
      url('http://foobar.d')  # ValidationFailure(func=url, ...)
      url('http://10.0.0.1', public=True)  # ValidationFailure(func=url, ...)


.. function:: uuid(*args, **kwargs)

   验证给定值是否为有效的 UUID。

   :param value: 需要验证的 UUID。
   :return: 如果验证成功返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import uuid

      uuid('2bc1c94f-0deb-43e9-92a1-4775189ec9f8')  # True
      uuid('2bc1c94f 0deb-43e9-92a1-4775189ec9f8')  # ValidationFailure(func=uuid, ...)


.. function:: even(value)

   验证给定值是否为偶数。

   :param value: 需要验证的数字。
   :return: 如果是偶数返回 True，否则返回 ValidationFailure。

   **示例：**

   .. code-block:: python

      from applications.common.utils.validate import even

      even(4)  # True
      even(5)  # ValidationFailure(func=even, args={'value': 5})