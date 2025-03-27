.. _后端页面编写:

后端页面编写
======================

该章节将介绍如何在 Pear Admin Flask 中编写一个新后端页面，此章节将会以编写兑换码管理页面为例，编写一个兑换码管理的后台页面。

.. note::

    前端页面制作，请参考 :ref:`简单前端页面示例` 章节。

.. _项目初始化逻辑:

项目初始化逻辑
-----------------------

我们知道，一个简单的 Flask 项目是从 `app = Flask(__name__)` 开始的，而 Pear Admin Flask 的初始化的逻辑同理也是在此基础上，不过稍加复杂了一点。
下面这张图片将会揭示项目初始化的逻辑。（点击可查看大图）

|

.. image:: ../_static/Pear\ Admin\ Flask\ 启动流程图.png
   :target: ../_images/Pear\ Admin\ Flask\ 启动流程图.png
   :align: center

|

由此可以看出，我们想要添加自己的后端页面，可以在 “注册项目的视图函数”（蓝框） 的地方添加，当然，同样页面可以作为插件的方式接入以提高项目的拓展性。
下面将介绍如何在这两种方式下添加自己的后台页面。

设计数据库
-----------------------

兑换码一定是保存在数据库中的，我们现在要求改程序至少有以下几个功能：

* 可以通过 flask admin init 或者等价的命令初始化数据库
* 数据库存在统一管理的模型
* 数据库的内容方便数据转化

数据的字段可以定为：

* id -- 唯一主键
* key -- 兑换码
* content -- 具体的内容
* enable -- 是否启用
* used -- 是否使用
* create_at -- 创建时间

根据上述需求，我们可以设计出这样一个数据库 Model ：

.. code-block:: python

    import datetime
    from applications.extensions import db


    class Gift(db.Model):
        __tablename__ = 'admin_gift'
        id = db.Column(db.Integer, primary_key=True, comment="唯一ID")
        key = db.Column(db.String(50), comment="兑换码")
        content = db.Column(db.String(), comment="具体的内容")
        enable = db.Column(db.Integer, default=0, comment='是否启用')
        used = db.Column(db.Integer, default=0, comment='是否已经使用')
        create_at = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')

我们将该文件命名为 `admin_gift.py` 放置在 `applications/models/admin_gift.py` ，而后为了使程序可以调用到这个模型，
需要在 `applications/models/__init__.py` 中导入这个模型。


.. code-block:: python

    from .admin_gift import Gift

.. note::

    由于 Gift 模型是 db.Model 的子类，在使用 `flask db init` 等命令行初始化数据库时，自动对 Gift 表进行创建，前提是这个类已经被 Python 加载，
    换而言之，Python 会自动将 db.Model 的子类作为数据库的一部分，加入到数据库初始化中。


初始化数据库
-----------------------

通过上面的操作，我们已经成功将数据库中的 admin_gift 表进行创建。现在我们希望在使用 `flask admin init` 的时候，可以将我们已经定义的数据写入到数据表中。

在 `applications/common/script` 目录中，撰写了默认数据的写入脚本（也就是 Flask 启动最后加载的项目），
我们要做的是在 `applications/common/script/admin.py` 中添加自己需要的数据，我们可以对其进行修改，添加如下的代码：

.. code-block:: python

    ...
    from applications.models import Gift

    ...
    now_time = datetime.datetime.now()
    ...
    powerdata = [
        ...
        Power(
            id=60,
            name='兑换码管理',
            type='1',
            code='system:gift:main',
            url='/system/gift/',
            open_type='_iframe',
            parent_id='1',
            icon='layui-icon layui-icon layui-icon layui-icon-diamond',
            sort=8,
            create_time=now_time,
            enable=1
        ), Power(
            id=61,
            name='兑换码添加',
            type='2',
            code='system:gift:add',
            url='',
            open_type='',
            parent_id='60',
            icon='',
            sort=0,
            create_time=now_time,
            enable=1
        ), Power(
            id=62,
            name='兑换码删除',
            type='2',
            code='system:gift:remove',
            url='',
            open_type='',
            parent_id='60',
            icon='',
            sort=0,
            create_time=now_time,
            enable=1
        ), Power(
            id=63,
            name='兑换码编辑',
            type='2',
            code='system:gift:edit',
            url='',
            open_type='',
            parent_id='60',
            icon='',
            sort=0,
            create_time=now_time,
            enable=1
        ),
        ...
    ]
    giftdata = [
        Gift(
            id=0,
            key='myTestCode',
            content='8折优惠',
            enable=1,
            used=0,
            create_at=now_time
        ),
        Gift(
            id=1,
            key='DisableCode',
            content='1折优惠',
            enable=0,
            used=0,
            create_at=now_time
        )
    ]

    ...
    def add_role_power():
        admin_powers = Power.query.filter(Power.id.in_([1, 3, 4, 9, 12, 13, 17, 18, 44, 48, 60])).all()
        ...

    @admin_cli.command("init")
    def init_db():
        ...
        db.session.add_all(giftdata)
        ...

这样就可以将数据库内容写入了。

.. note::

    powerdata 中添加了对兑换码的操作权限，可以先去“权限管理”中添加，而后再从数据中抄取。
    或者忽略初始化时对 powerdata 的添加，在初始化之后，手动在权限管理中添加。

使用 Schema 序列化
---------------------------

与前端交互大多用的是 JSON 格式的数据，这就涉及到将数据库查询的结果对象（Query）转化为 JSON 这一步骤。
我们可以使用 flask_marshmallow 中的 SQLAlchemyAutoSchema 将数据库查询对象转换为 JSON 格式。

创建文件 `applications/schemas/admin_gift.py` ，并继承 SQLAlchemyAutoSchema ，更改其中的目标模型为我们创建的 Gift 模型。

.. code-block:: python

    from flask_marshmallow.sqla import SQLAlchemyAutoSchema
    from applications.models import Gift


    class GiftSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = Gift  # table = models.Album.__table__
            include_fk = True  # 序列化阶段是否也一并返回主键

.. note::

    更多序列化参数可以参考 :ref:`Schema 序列化` 章节。

随后，在 `applications/schemas/__init__.py` 引用，

.. code-block:: python

    ...
    from .admin_gift import GiftSchema

这一步不是必须的，但是应通过这一步的引用，可以在蓝图页面中，方便的使用 `from applications.schemas import *` 的方式导入。

编写后端视图函数
-----------------------

注册蓝图
~~~~~~~~~~~~~~

接着我们需要设计后端的数据增删改查部分的视图函数，创建文件 `applications/view/system/gift.py` ，并写上基本的蓝图初始化逻辑：

.. code-block:: python

    from flask import Blueprint

    bp = Blueprint('gift', __name__, url_prefix='/gift')

根据流程图，我们需要在 `applications/view/system/__init__.py` 中，注册 `gift.py` 的蓝图：

.. code-block::

    ...
    from applications.view.system.gift import bp as gift_bp
    ...

    def register_system_bps(app: Flask):
        ...
        system_bp.register_blueprint(gift_bp)
        ...


.. _编写数据获取路由:

编写数据获取路由
~~~~~~~~~~~~~~~~~~~~

.. important::

    因为目标是让前端 layui 的动态表格获取数据，而根据 layui 的文档，表格将会提供 limit 和 page 两个查询参数来进行分页查询，所以要对 limit 和 page 进行处理。

现在开始编写数据获取路由，路由是以 JSON 格式响应数据库中 `admin_gift` 的数据，下面提供一种实现方法：

.. code-block:: python

    from flask import Blueprint

    from applications.models import Gift
    from applications.schemas import GiftSchema
    from applications.extensions import db

    from applications.common.utils.http import table_api
    from applications.common.utils.rights import authorize

    bp = Blueprint('gift', __name__, url_prefix='/gift')


    @bp.get('/data')
    @authorize("system:gift:main")
    def data():

        query = db.session.query(Gift).layui_paginate()

        return table_api(
            data=GiftSchema(many=True).dump(query),
            count=query.total,
            limit=query.per_page
        )

可以发现，在没有搜索的情况下，正确处理前端的分页查询，实际上只有简单 5 行代码就可以完成（自动处理了 limit 和 page 参数），
另外，也可以采用已经封装好的 `layui_paginate_json` 方法：

.. code-block:: python

    ...
    @bp.get('/data')
    @authorize("system:gift:main")
    def data():

        data, total, page, limit = db.session.query(Gift).layui_paginate_json(GiftSchema)

        return table_api(
            data=data,
            count=total,
            limit=limit
        )

`layui_paginate_json` 函数完成了分页、解析与转化，适用于一些比较简单数据转化场景。

.. warning::

    对于任何形式的后台管理员路由，切记不要忘记添加 `authorize` 装饰函数对请求效验权限！！！！！！

.. note::

    对于 layui_paginate 方法定义，可以查看 :ref:`与 layui 的数据格式同步` 章节。

访问路由 `/system/gift/data` 可以获得如下数据：

.. code-block:: json

    {
      "code": 0,
      "count": 2,
      "data": [
        {
          "content": "8折优惠",
          "create_at": "2025-01-28T19:10:48.607165",
          "enable": 1,
          "id": 0,
          "key": "myTestCode",
          "used": 0
        },
        {
          "content": "1折优惠",
          "create_at": "2025-01-28T19:10:48.607165",
          "enable": 0,
          "id": 1,
          "key": "DisableCode",
          "used": 0
        }
      ],
      "limit": 10,
      "msg": ""
    }

随后，我们加入查询：

.. code-block:: python

    ...
    @bp.get('/data')
    @authorize("system:gift:main")
    def data():
        key = request.args.get('key', type=str)

        mf = ModelFilter()
        if key:
            mf.vague('key', key)  # 模糊查询

        data, total, page, limit = db.session.query(Gift).filter(mf.get_filter(Gift)).layui_paginate_json(GiftSchema)

        return table_api(
            data=data,
            count=total,
            limit=limit
        )

.. _编写启用与禁用视图函数:

编写启用与禁用视图函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

启用与禁用的基本思路是通过 ID 筛选到合适的记录行并设置其 enable 为 1 或者 0。在设计数据库时，我们有意将表示启用禁用字段设置为 `enable` 以此可以使用项目已经封装好的函数。

.. code-block:: python

    from applications.common.curd import enable_status, disable_status

    @bp.put('/enable')
    @authorize("system:gift:edit")
    def enable_api():
        data = request.get_json(force=True)

        if enable_status(Gift, data.get('id')):
            return success_api(msg="启用成功")

        return success_api(msg="启用失败")


    @bp.put('/disable')
    @authorize("system:gift:edit")
    def disable_api():
        req_json = request.get_json(force=True)

        if disable_status(Gift, req_json.get('id')):
            return success_api(msg="禁用成功")

        return success_api(msg="禁用失败")

.. note::

    对于上述的 `enable_status` `disable_status` 函数，可以参考文档 :ref:`简单增删改查模块` 章节。

数据的修改经历如下步骤：获取目标兑换码 ID、获取对应修改的新数据、应用修改，而数据的添加仅没有“获取目标兑换码 ID”这一步骤。

我们先来撰写添加这一部分的视图函数，

编写删除视图函数
~~~~~~~~~~~~~~~~~~~~~~~~~~

删除的视图函数，实则和启用禁用是一样的，这里直接给出代码：

.. code-block:: python

    @bp.delete('/remove/<int:_id>')
    @authorize("system:gift:remove")
    def remove_api(_id):

        if delete_one_by_id(Gift, _id):
            return success_api(msg="删除成功")

        return success_api(msg="删除失败")


你会注意到，由于 `curd` 模块的封装，使编写路由变的简洁。

.. _编写增加视图函数:

编写增加视图函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

添加视图函数经历下面几个步骤：获取参数、效验参数、写入数据库。

.. code-block:: python

    @bp.post('/save')
    @authorize("system:gift:add", log=True)
    def save():
        req_json = request.get_json(force=True)

        data = {
            'key': req_json.get('key'),
            'content': req_json.get('content'),
            'enable': req_json.get('enable'),
            'used': 0
        }

        # 效验参数
        if not all(list(data.keys())):
            return fail_api(msg="参数不全")

        if not data['enable'].isdigit():
            return fail_api(msg="参数 enable 错误")

        try:
            db.session.add(Gift(**data))
            db.session.commit()
            return success_api(msg="添加成功")
        except Exception as e:
            return fail_api(msg="添加失败")

.. important::

    效验参数是必不可少的，要尽可能一切不相信用户的输入。

.. _编写修改视图函数:

编写修改视图函数
~~~~~~~~~~~~~~~~~~~~~~~~

修改视图函数的编写就照葫芦画瓢即可，代码如下：

.. code-block:: python

    @bp.post('/update')
    @authorize("system:gift:edit", log=True)
    def update():
        req_json = request.get_json(force=True)

        _id = req_json.get('id')

        data = {
            'key': req_json.get('key'),
            'content': req_json.get('content'),
            'enable': req_json.get('enable'),
            'used': 0
        }

        # 效验参数
        if not all(list(data.keys())):
            return fail_api(msg="参数不全")

        if not data['enable'].isdigit():
            return fail_api(msg="参数 enable 错误")

        try:
            db.session.query(Gift).filter(Gift.id == _id).update(data)
            db.session.commit()
            return success_api(msg="编辑成功")
        except Exception as e:
            return fail_api(msg="编辑失败")

.. note::

    插件方式接入项目，请查看 :ref:`以插件的方式接入项目` 章节。

