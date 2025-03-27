.. _字段构造模块:

:mod:`helper` -- 字段构造模块
=======================================

:mod:`helper` 模块源代码在文件 `applications/common/helper.py` 下，主要集结了一些常用的字段构造方法。

.. module:: helper

类
--------

.. class:: ModelFilter

   ORM 多条件查询构造器，支持多种查询条件组合。

   **示例：**

   .. code-block:: python

      from applications.common.helper import ModelFilter
      mf = ModelFilter()
      mf.exact('name', 'John')  # 添加精确匹配条件
      mf.vague('email', 'example.com')  # 添加模糊匹配条件
      query = User.query.filter(mf.get_filter(User))


   .. attribute:: filter_field

      存储字段过滤条件的字典。


   .. attribute:: filter_list

      存储最终的过滤条件列表。


   .. method:: __init__()

      初始化过滤条件存储字典和列表。

   .. method:: escape_like(value: str, escape_char: str = '\\')

      转义LIKE查询中的特殊字符（%, _ 和转义字符本身）

      :param value: 需要转义的原始字符串
      :param escape_char: 转义字符（默认反斜杠）
      :return: 转义后的安全字符串


   .. method:: exact(field_name, value)

      添加精确匹配条件。

      :param field_name: 模型字段名称。
      :param value: 匹配的值。


   .. method:: neq(field_name, value)

      添加不等于条件。

      :param field_name: 模型字段名称。
      :param value: 不匹配的值。


   .. method:: greater(field_name, value)

      添加大于条件。

      :param field_name: 模型字段名称。
      :param value: 大于的值。


   .. method:: less(field_name, value)

      添加小于条件。

      :param field_name: 模型字段名称。
      :param value: 小于的值。


   .. method:: vague(field_name, value: str)

      添加模糊匹配条件（左右模糊）。

      :param field_name: 模型字段名称。
      :param value: 模糊匹配的值。


   .. method:: left_vague(field_name, value: str)

      添加左模糊匹配条件。

      :param field_name: 模型字段名称。
      :param value: 左模糊匹配的值。


   .. method:: right_vague(field_name, value: str)

      添加右模糊匹配条件。

      :param field_name: 模型字段名称。
      :param value: 右模糊匹配的值。


   .. method:: contains(field_name, value: str)

      添加包含条件。

      :param field_name: 模型字段名称。
      :param value: 包含的值。


   .. method:: between(field_name, value1, value2)

      添加范围查询条件。

      :param field_name: 模型字段名称。
      :param value1: 范围起始值。
      :param value2: 范围结束值。


   .. method:: get_filter(model: db.Model)

      获取最终的 SQLAlchemy 过滤条件。

      :param model: SQLAlchemy 模型类。
      :return: 返回组合后的过滤条件。