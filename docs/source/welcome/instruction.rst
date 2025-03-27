.. _welcome:

项目介绍
=================

.. note::
    该章节将会介绍 Pear Admin Flask 项目的一些基本信息，以及介绍在开发时需要使用到的工具链、文档。此项目是一个 Web 开发项目，前后端一体，
    在 layui 界面库的基础上进行二次封装以及开发。

.. important::
    项目经过几次大型修改之后，为了同步项目 Pear Admin Layui ，部分（特别是前端页面的）代码改动较大，若要从旧版本进行迁移，
    请根据文档的 :ref:`migration` 章节进行迁移与改变。如存在问题请在仓库中提交 issue 并标明分支，
    然后提供详尽的复现方法，感谢各位！
    **另外，对于 Pear Admin Layui 中未实现但是在 Pear Admin Flask 中实现的内容或者存在的部分问题，请参阅** :ref:`update` **章节。**

.. raw:: html

    <div align="center">
    <br/>
    <br/>
      <h1 align="center">
        Pear Admin Flask
      </h1>
      <h4 align="center">
        开 箱 即 用 的 Flask 快 速 开 发 平 台
      </h4>

    <p align="center">
        <a href="#">
            <img src="https://img.shields.io/badge/pear%20admin%20flask-2.0.0-green" alt="Pear Admin Layui Version">
        </a>
        <a href="#">
            <img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python Version">
        </a>
          <a href="#">
            <img src="https://img.shields.io/badge/Mysql-5.3.2+-green.svg" alt="Mysql Version">
        </a>
    </p>
    </div>

    <div align="center">
      <img  width="92%" style="border-radius:10px;margin-top:20px;margin-bottom:20px;box-shadow: 2px 0 6px gray;" src="../_static/feature.png" />
    </div>

项目简介
---------------

Pear Admin Flask 基于 Flask 的后台管理系统，拥抱应用广泛的python语言，通过使用本系统，即可快速构建你的功能业务
项目旨在为 python 开发者提供一个后台管理系统的模板，可以快速构建信息管理系统。

项目使用 flask-sqlalchemy + 权限验证 + marshmallow 序列化与数据验证，以此方式集成了若干不同的功能。

内置功能
----------

- **用户管理**：用户是系统操作者，该功能主要完成系统用户配置。
- **权限管理**：配置系统菜单，操作权限，按钮权限标识等。
- **角色管理**：角色菜单权限分配。
- **操作日志**：系统正常操作日志记录和查询；系统异常信息日志记录和查询。
- **登录日志**：系统登录日志记录查询包含登录异常。
- **服务监控**：监视当前系统 CPU、内存、磁盘、Python 版本、运行时长等相关信息。
- **文件上传**：图片上传示例。

项目分支说明
---------------

.. warning::
    Pear Admin Flask 不仅仅只提供一种对于 Pear Admin 后端的实现方式，所以提供了不同的分支版本，不同分支版本各有其优劣，并且由不同的开发者维护

.. list-table::
   :header-rows: 1

   * - 分支名称
     - 特点
   * - `master <https://gitee.com/pear-admin/pear-admin-flask/tree/master/>`_
     - 功能齐全，处于开发阶段，代码量较大。
   * - `main <https://gitee.com/pear-admin/pear-admin-flask/tree/main/>`_
     - 功能精简，代码量小，处于开发阶段，易于维护。
   * - `mini <https://gitee.com/pear-admin/pear-admin-flask/tree/mini/>`_
     - 不再更新，是最初版本的镜像

版本支持情况
---------------

经过测试，此项目的（master分支）运行要求是 ``>= Python 3.8`` ，推荐使用 ``Python 3.11``。

.. tip::
    由于 Flask 中使用的 Werkzeug 模块更新，Flask 官方并未进行更新，所以可能会出现 ImportError 。
    截止至 2025 年 1 月 26 日，若使用项目中 **requirements.txt** 不会出现该错误。

此类情况的出现可以通过正确安装 **requirements.txt** 中的模块（以及其对应版本）解决。


目录架构
--------------

应用结构
~~~~~~~~~~

.. code-block:: bash

    Pear Admin Flask (master)
    ├─applications  # 项目核心模块
    │  ├─common  # 公共模块（初始化数据库、公用函数）
    │  ├─extensions  # 注册项目插件
    │  ├─schemas  # 序列化模型
    │  ├─models  # 数据库模型
    │  ├─views  # 视图部分
    │  ├─config.py  # 项目配置
    │  └─__init__.py  # 项目初始化入口
    ├─docs  # 文档说明
    ├─static  # 静态资源文件
    ├─templates  # 静态模板文件
    └─app.py  # 程序入口

资源结构
~~~~~~~~~~

.. code-block:: bash

    Pear Admin Flask (master)
    ├─static    # 项目设定的 Flask 资源文件夹
    │  ├─admin    # pear admin flask 的后端资源文件（与 pear admin layui 同步）
    │  ├─index    # pear admin flask 的前端资源文件
    │  └─upload     # 用户上传保存目录
    └─templates # 项目设定的 Flask 模板文件夹
      ├─admin   # pear admin flask 的后端管理页面模板
      │  ├─admin_log    # 日志页面
      │  ├─common       # 基本模板页面（头部模板与页脚模板）
      │  ├─console      # 系统监控页面模板
      │  ├─dept         # 部门管理页面模板
      │  ├─dict         # 数据自动页面模板
      │  ├─mail         # 邮件管理页面模板
      │  ├─photo        # 图片上传页面模板
      │  ├─power        # 权限（菜单）管理页面模板
      │  ├─role         # 角色管理页面模板
      │  ├─task         # 任务设置页面模板
      │  └─user         # 用户管理页面模板
      ├─errors  # 错误页面模板
      └─index   # 主页模板

开发资源
-------------

由于项目依赖多个开源项目，而此开发文档并不会全进行涉足，所以提供如下的链接共大家开发参考：

* 前端页面设计可以参考 `layui 原生态 · 开源 极简模块化 Web UI 组件库 <https://layui.dev/>`_ 。
* 后端 Flask 学习可以参考官方的 `Flask 开发文档 <https://flask.palletsprojects.com/zh-cn/stable/>`_ 。
* Pear Admin 框架的源码可以查看 `Pear Admin 开源仓库 <https://gitee.com/pear-admin/pear-admin-layui>`_ 。
* 开发时可以选择 `PyCharm <https://www.jetbrains.com/pycharm/>`_ 作为集成开发环境 。