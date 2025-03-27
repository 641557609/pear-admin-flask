开发技巧
===================

开发 Web 过程中需要用到许多技巧来加速开发，本章节将介绍开发的小技巧与一些需要注意的细节。

配置数据库
-----------

项目采用 flask-sqlalchemy，支持多数据库连接，默认是使用 sqlite 的，可以在 `applications/config.py` 中配置，如果需要连接其他数据库需要可以参考：

* HOSTNAME: 指数据库的IP地址
* USERNAME：指数据库登录的用户名
* PASSWORD：指数据库登录密码
* PORT：指数据库开放的端口
* DATABASE：指需要连接的数据库名称

.. code-block:: python

    # MSSQL
    SQLALCHEMY_DATABASE_URI =  f"mssql+pymssql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=cp936"

    # mysql
    SQLALCHEMY_DATABASE_URI =  f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

    # Oracle
    SQLALCHEMY_DATABASE_URI =  f"oracle+cx_oracle://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"

    # SQLite
    SQLALCHEMY_DATABASE_URI =  "sqlite://../database.db"

    # Postgres
    SQLALCHEMY_DATABASE_URI =  f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"

.. important::

    使用不同的数据库需要安装另外的库，比如 mysql 要安装 pymysql 库（不同平台可能名称不一样），请自行查询资料而后进行配置。

添加后台菜单
------------

在 Pear Admin Flask 中，菜单的管理归属于 “权限管理” ，这样做的原因是为了使不同用户可以使用不同的访问控制。所以需要修改菜单，需要在 “权限管理” 页面编辑即可。

配置后台站内消息
-------------------

后台站内消息是异步获取的，其路由在 `applications/view/system/rights.py` 的 `message` 函数中，后续会考虑写入数据库，并添加管理函数进行统一的管理。

权限效验
------------

在开发后台管理模板的过程中会涉及到权限效验，即访问控制。Pear Admin Flask 中提供了方便的函数用于进行权限效验。详情请查看 :ref:`权限验证模块` 章节。

.. _Schema 序列化:

Schema 序列化
---------------

项目中时常会涉及到数据库的读写，在读入数据时采用 SQLAlchemy，将模型查询的数据对象转化为字典，以此方便与前端页面进行数据交换。

.. important::

    Schema 模型放在了 `applications/schemas` 文件夹中，与 `applications/models` 中的数据库模型对应（准确来说是序列化为字典的配置）。

进行序列化时，常常会用到 `applications/common/curd.py` 中的 `model_to_dicts` 函数，下面是一个常见的用法。

.. code-block:: python

    from applications.models import Dept
    from applications.common import curd
    from applications.schemas import DeptSchema

    dept = Dept.query.order_by(Dept.sort).all()
    power_data = curd.model_to_dicts(schema=DeptSchema, data=dept)  # 此处 power_data 将会是一个列表，存储了部门的数据字典

在自己撰写 Schema 模型时，推荐使用自动化类型转化：

.. code-block:: python

    from flask_marshmallow.sqla import SQLAlchemyAutoSchema
    from applications.models import 你的模型类
    class RoleOutSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = 你的模型类  # table = models.Album.__table__
            # include_relationships = True  # 输出模型对象时同时对外键，是否也一并进行处理
            include_fk = True  # 序列化阶段是否也一并返回主键
            # fields= ["id","name"] # 启动的字段列表
            # exclude = ["id","name"] # 排除字段列表

.. note::

    更多参数可以参考官方文档对其的解释，链接如下：`SQLAlchemyAutoSchema <https://marshmallow-sqlalchemy.readthedocs.io/en/latest/api_reference.html>`_


.. _与 layui 的数据格式同步:

与 layui 的数据格式同步
------------------------------

项目的前端页面基于 layui 框架，在一些数据展示页面（如：layui 动态表格）需要与 layui 框架进行快速的数据交换。比如前端会传入 limit 和 page 参数
用于限定数据展示的范围。故项目中在 SQLAlchemy 中添加了专有的查询函数。详情可以查看文件 `applications/extensions/init_sqlalchemy.py` 。
下面是对 `Query` 类的解释。

.. class:: Query(BaseQuery)

   自定义查询类，扩展了 BaseQuery 的功能，支持软删除、逻辑查询、分页和序列化。

   **示例：**

   .. code-block:: python

      # 软删除
      User.query.filter_by(id=1).soft_delete()

      # 查询所有未删除的记录
      users = User.query.logic_all()

      # 分页查询并返回 JSON 数据
      data, total, page, per_page = User.query.layui_paginate_json(UserSchema)


   .. method:: soft_delete()

      软删除当前查询结果集中的记录。

      :return: 返回更新操作影响的行数。


   .. method:: logic_all()

      查询所有未删除的记录。

      :return: 返回未删除的记录列表。


   .. method:: all_json(schema: Schema)

      将查询结果序列化为 JSON 格式。

      :param schema: Marshmallow Schema 类。
      :return: 返回序列化后的 JSON 数据。


   .. method:: layui_paginate(page=None, limit=None)

      分页查询，适用于 Layui 表格。

      **需要注意的是，如果不提供 page 和 limit 则该函数必须在视图函数中使用，该函数会自动获取 GET 请求中的 limit 和 page 参数构成查询。**

      :param page: 页码
      :param limit: 页数据个数
      :return: 返回分页对象。

      **示例：**

      .. code-block:: python

          # 查询邮件数据并分页
          mail = Mail.query.filter(mf.get_filter(Mail)).layui_paginate()
          return model_to_dicts(schema=MailOutSchema, data=mail.items)


   .. method:: layui_paginate_json(schema: Schema, page=None, limit=None)

      分页查询并通过 Marshmallow Schema 类 转化为 JSON，适用于 Layui 表格。

      :param schema: Marshmallow Schema 类。
      :param page: 页码
      :param limit: 页数据个数
      :return: 返回包含序列化数据、总数、当前页码和每页条数的元组。


   .. method:: layui_paginate_db_json(page=None, limit=None)

      分页查询并返回数据库原始数据的 JSON 格式，适用于 Layui 表格。

      :param page: 页码
      :param limit: 页数据个数
      :return: 返回包含序列化数据（列表）、总数、当前页码和每页条数的元组。

      **示例：**

      .. code-block:: python

         >> db.session.query(Gift.id, Gift.key).layui_paginate_db_json()
         ([{'id': 0, 'key': 'myTestCode'}, {'id': 1, 'key': 'DisableCode'}], 2, 1, 10)


进行字段构造
-----------------------

提炼数据时常常会用到准确匹配或者模糊匹配，又或者是进行多条件大小比较的匹配，此时可以通过字段构造来解决。项目中提供了字段构造的类位于
`applications/common/helper.py` 。详情查看 :ref:`字段构造模块` 章节。


响应合适的响应数据
-----------------------

在进行 JSON 数据响应时，应该注重响应的 JSON 格式类型，一般情况下，项目的 JSON 响应会形如：

.. code-block:: json

    {
        "code": 0,
        "msg": "请求成功",
        "data": [],
        "count": 0,
        "limit": 0
    }

其中，`data` 、 `total` 和 `limit` 字段是可选的，仅在传输数据的时候存在。项目提供了生成统一响应格式的函数，位于 `applications/common/utils/http.py` 。
详情查看 :ref:`JSON 响应正文生成模块` 章节。


发送邮件
-----------------------

程序提供了发送邮件的模块，前提是需要正确在 `applications/config.py` 中配置 SMTP 服务器。详情查看 ref:`邮件模块` 章节。

.. code-block:: python

    from flask_login import current_user
    from applications.common.utils import mail

    mail.add("test@test.com", "subject", "<h1>Hello</h1>", current_user.id)