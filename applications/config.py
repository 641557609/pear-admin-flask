import logging
from datetime import timedelta

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class BaseConfig:
    # 超级管理员账号
    SUPERADMIN = 'admin'

    # 系统名称
    SYSTEM_NAME = '管理系统'

    # 主题面板的链接列表配置
    SYSTEM_PANEL_LINKS = [

    ]

    # 上传图片目标文件夹
    UPLOADED_PHOTOS_DEST = 'static/upload/'
    UPLOADED_FILES_ALLOW = ['gif', 'jpg', 'jpeg', 'png', 'webp']
    UPLOADS_AUTOSERVE = True

    # 上传Excel文件目标文件夹
    UPLOADED_EXCELFILES_DEST   = 'static/excel/'
    UPLOADED_EXCELFILES_ALLOW   = ['xlsx', 'xls', 'csv']

    # 生成文件保存路径
    REPORT_OUTPUT_DIR = "custom_reports"

    # JSON 配置
    JSON_AS_ASCII = False

    # 配置多个数据库连接的连接串写法示例
    # HOSTNAME: 指数据库的IP地址、USERNAME：指数据库登录的用户名、PASSWORD：指数据库登录密码、PORT：指数据库开放的端口、DATABASE：指需要连接的数据库名称
    # MSSQL:    f"mssql+pymssql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=cp936"
    # MySQL:    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
    # Oracle:   f"oracle+cx_oracle://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"
    # SQLite    "sqlite:/// database.db"
    # Postgres f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"
    # Oracle的第二种连接方式
    # dsnStr = cx_Oracle.makedsn({HOSTNAME}, 1521, service_name='orcl')
    # connect_str = "oracle://%s:%s@%s" % ('{USERNAME}', ' {PASSWORD}', dsnStr)

    #  在SQLALCHEMY_BINDS 中设置：'{数据库连接别名}': '{连接串}'
    # 最后在models的数据模型class中，在__tablename__前设置        __bind_key__ = '{数据库连接别名}'  即可，表示该数据模型不使用默认的数据库连接，改用“SQLALCHEMY_BINDS”中设置的其他数据库连接
    #  SQLALCHEMY_BINDS = {
    #    'testMySQL': 'mysql+pymysql://test:123456@192.168.1.1:3306/test?charset=utf8',
    #    'testMsSQL': 'mssql+pymssql://test:123456@192.168.1.1:1433/test?charset=cp936',
    #    'testOracle': 'oracle+cx_oracle://test:123456@192.168.1.1:1521/test',
    #    'testSQLite': 'sqlite:///database.db
    # }

    # mysql 配置
    MYSQL_USERNAME = "root"
    MYSQL_PASSWORD = "123456"
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_DATABASE = "PearAdminFlask2"
    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

    # sqlserver 配置
    SQL_SERVER_HOST = '192.168.1.2'  # ip地址
    SQL_SERVER_DATABASE = 'hxlh'  # 数据库名
    SQL_SERVER_USERNAME= 'user_fufangpeng'  # 用户名
    SQL_SERVER_PASSWORD = 'Teenrun0124#*!'  # 密码
    SQL_SERVER_URI = f'mssql+pyodbc://{SQL_SERVER_USERNAME}:{SQL_SERVER_PASSWORD}@{SQL_SERVER_HOST}/{SQL_SERVER_DATABASE}?driver=ODBC+Driver+13+for+SQL+Server'
    SQL_SERVER_POOL_SIZE = 3  # 连接池大小
    SQL_SERVER_POOL_RECYCLE = 18000  # 连接回收时间（秒）
    SQL_SERVER_POOL_TIMEOUT = 10  # 获取连接超时时间
    # 默认日志等级
    # LOG_LEVEL = logging.WARN
    # 调试日志等级
    LOG_LEVEL = logging.DEBUG



    """
    flask-mail配置
    """
    # 发信设置
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = '123@qq.com'
    MAIL_PASSWORD = 'XXXXX'  # 生成的授权码
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # 插件配置，填写插件的文件名名称，默认不启用插件。
    PLUGIN_ENABLE_FOLDERS = []

    # Session 设置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SESSION_TYPE = "filesystem"  # 默认使用文件系统来保存会话
    SESSION_PERMANENT = False  # 会话是否持久化
    SESSION_USE_SIGNER = True  # 是否对发送到浏览器上 session 的 cookie 值进行加密

    SECRET_KEY = "pear-system-flask"

    """
    通知服务配置
    """

    # 发送接口
    TEENRUN_API_URL = "http://erp.winworld.top:9000/erp"
    NOTIFICATION_RETRIES = 1    #重试次数

    """
    Flask_Apscheduler的配置
    """
    # 使用数据库存储定时任务（默认是存储在内存中）
    SCHEDULER_JOBSTORES = {'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
    # 设置时区，时区不一致会导致定时任务的时间错误
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    # 一定要开启API功能，这样才可以用api的方式去查看和修改定时任务
    SCHEDULER_API_ENABLED = True
    # api前缀（默认是/scheduler）
    SCHEDULER_API_PREFIX = '/scheduler'
    # 配置允许执行定时任务的主机名
    SCHEDULER_ALLOWED_HOSTS = ['*']
    # auth验证。默认是关闭的，
    # SCHEDULER_AUTH = HTTPBasicAuth()
    # 设置定时任务的执行器（默认是最大执行数量为10的线程池）
    SCHEDULER_EXECUTORS = {'default': {'type': 'threadpool', 'max_workers': 10}}
    # 另外flask-apscheduler内有日志记录器。name为apscheduler.scheduler和apscheduler.executors.default。如果需要保存日志，则需要对此日志记录器进行配置
    JSONIFY_PRETTYPRINT_REGULAR = False
