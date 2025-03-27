.. _简单增删改查模块:

:mod:`curd` -- 简单增删改查模块
=======================================

:mod:`curd` 模块源代码在文件 `applications/common/curd.py` 下，主要集结了一些简单实用的增删改查。

.. module:: curd

类
-------

.. class:: LogicalDeleteMixin

   逻辑删除混入类，为模型提供软删除功能。

   **示例：**

   .. code-block:: python

      class Test(db.Model, LogicalDeleteMixin):
          __tablename__ = 'admin_test'
          id = db.Column(db.Integer, primary_key=True, comment='角色ID')

      # 软删除
      Test.query.filter_by(id=1).soft_delete()

      # 查询所有未删除的记录
      Test.query.logic_all()


函数
--------------

.. function:: auto_model_jsonify(data, model: db.Model)

   自动序列化模型数据为 JSON 格式，无需手动定义 Schema。

   **示例：**

   .. code-block:: python

      power_data = curd.auto_model_jsonify(model=Dept, data=dept)

   :param data: 需要序列化的 SQLAlchemy 查询结果。
   :param model: SQLAlchemy 模型类。
   :return: 返回序列化后的 JSON 数据。


.. function:: model_to_dicts(schema: ma.Schema, data)

   使用指定的 Schema 序列化 SQLAlchemy 查询结果。

   :param schema: Marshmallow Schema 类。
   :param data: SQLAlchemy 查询结果。
   :return: 返回序列化后的数据，返回字典。


.. function:: get_one_by_id(model: db.Model, id)

   根据 ID 查询单个记录。

   :param model: SQLAlchemy 模型类。
   :param id: 记录的主键 ID。
   :return: 返回查询到的记录，如果未找到则返回 None。


.. function:: delete_one_by_id(model: db.Model, id)

   根据 ID 删除单个记录。

   :param model: SQLAlchemy 模型类。
   :param id: 记录的主键 ID。
   :return: 返回删除操作影响的行数。


.. function:: enable_status(model: db.Model, id)

   启用指定 ID 的记录。

   :param model: SQLAlchemy 模型类。
   :param id: 记录的主键 ID。
   :return: 如果操作成功返回 True，否则返回 False。


.. function:: disable_status(model: db.Model, id)

   停用指定 ID 的记录。

   :param model: SQLAlchemy 模型类。
   :param id: 记录的主键 ID。
   :return: 如果操作成功返回 True，否则返回 False。