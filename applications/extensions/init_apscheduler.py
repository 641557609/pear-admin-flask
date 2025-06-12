from flask import Flask
from flask_apscheduler import APScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
scheduler = APScheduler()

def init_scheduler(app: Flask):
    scheduler.init_app(app)
    from applications.tasks import update_employees
    from applications.tasks import clean_file
    scheduler.start()
    # 添加调度器事件
    # scheduler.add_listener(任务函数名, 事件类型)
    # scheduler.add_listener(update_employees, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)