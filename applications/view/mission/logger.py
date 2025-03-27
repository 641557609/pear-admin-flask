from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.models import ExecutionLog, ScheduledTask
from applications.common.utils.http import table_api, success_api, fail_api
from applications.schemas import ExecutionLogSchema
from applications.extensions import db

bp = Blueprint('logger', __name__, url_prefix='/logger')


# 首页
@bp.get('/')
@authorize("mission:logger:main")
def main():
    return render_template('mission/logger/main.html')


# 表格数据
@bp.get('/data')
@authorize("mission:task:main")
def table():
    task_name = str_escape(request.args.get('task_name', type=str))
    start_date = str_escape(request.args.get('start_date', type=str))
    end_date = str_escape(request.args.get('end_date', type=str))
    filters = []
    if task_name:
        filters.append(ExecutionLog.task_name == task_name)
    if start_date:
        filters.append(ExecutionLog.run_time >= start_date)
    if end_date:
        new_end_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        filters.append(ExecutionLog.run_time <= new_end_date)
    logger = ExecutionLog.query.filter(*filters).layui_paginate()
    return table_api(data=ExecutionLogSchema(many=True).dump(logger), count=logger.total)

# 日志删除
@bp.delete('/remove/<int:id>')
@authorize("mission:logger:remove", log=True)
def remove(id):
    logger = ExecutionLog.query.get(id)

    if not logger:
        return fail_api(msg="记录不存在")
    try:
        db.session.delete(logger)
        db.session.commit()
        return success_api(msg="记录删除成功")
    except Exception as e:
        return fail_api(msg=f"记录删除失败: {str(e)}")


# 批量删除
@bp.delete('/batchRemove')
@authorize("mission:logger:remove", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')

    if not ids:
        return fail_api(msg="未提供删除 ID")

    for id in ids:
        if not id.isdigit():
            db.session.rollback()
            return fail_api(msg="参数提供错误")

        id = int(id)

        logger = ExecutionLog.query.filter_by(logger_id=id).first()
        if logger:
            db.session.delete(logger)
        else:
            return fail_api(msg="批量删除失败")
    db.session.commit()

    return success_api(msg="批量删除成功")

# 查看详情
@bp.get('/detail/<int:id>')
@authorize("mission:logger:detail", log=True)
def detail(id):
    logger = ExecutionLog.query.options(joinedload(ExecutionLog.scheduled_task)).get(id)
    return render_template("mission/logger/detail.html", logger=logger)