# import traceback
# traceback.print_exc()
import datetime

from applications.extensions import db
from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload
from applications.models import ScheduledTask, TaskTemplate, Employees
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.common.utils.http import table_api, success_api, fail_api
from applications.schemas.mission_scheduled_task import ScheduledTaskSchema
from applications.services.variable_service import VariableHandler
from applications.services.scheduler_service import job, create_scheduler_trigger
from applications.extensions.init_apscheduler import scheduler



bp = Blueprint('task', __name__, url_prefix='/task')


# 首页
@bp.get('/')
@authorize("mission:task:main")
def main():
    return render_template('mission/task/main.html')


# 表格数据
@bp.get('/data')
@authorize("mission:task:main")
def table():
    task_name = str_escape(request.args.get('task_name', type=str))
    template_name = str_escape(request.args.get('template_name', type=str))
    filters = []
    if task_name:
        filters.append(ScheduledTask.task_name.contains(task_name))
    if template_name:
        filters.append(ScheduledTask.task_template.has(TaskTemplate.template_name == template_name))
    tasks = ScheduledTask.query.options(joinedload(ScheduledTask.employees),
                                        joinedload(ScheduledTask.task_template)).filter(*filters).layui_paginate()
    return table_api(data=ScheduledTaskSchema(many=True).dump(tasks), count=tasks.total)


# 任务增加
@bp.get('/add')
@bp.get('/add/<int:id>')
@authorize("mission:task:add", log=True)
def add(id=None):
    data = []
    if id is None:
        templates = TaskTemplate.query.all()
        for template in templates:
            variables = VariableHandler.extract_variables(text=template.sql_template)
            data.append({
                'id': id,
                'template_name': template.template_name,
                'template_id': template.id,
                'template_type': template.template_type,
                'variables': list(variables)
            })
    else:
        template = TaskTemplate.query.get(id)
        variables = VariableHandler.extract_variables(text=template.sql_template)
        data.append({
            'id': id,
            'template_name': template.template_name,
            'template_id': template.id,
            'template_type': template.template_type,
            'variables': list(variables)
        })

    employees = Employees.query.filter(Employees.status==1)
    return render_template('mission/task/add.html', data=data, employees=employees)

# 任务增加
@bp.post('/save')
@authorize("mission:task:save", log=True)
def save():
    req = request.get_json(force=True)
    try:
        # 数据解析
        data_field = req['data_field']
        selected_employees = req['selected_employees']
        # 模板处理
        template_id = data_field.get('template_id', '').split('_')[-1]
        template = TaskTemplate.query.get(template_id)
        if not template:
            return fail_api(msg="模板不存在")

        # 变量处理优化
        variables = VariableHandler.extract_variables(text=template.sql_template)
        variables_config = [
            {f"variable_{i}": data_field[f"{v}_{i}"]
             for i in ["name", "type", "value"]}
            for v in variables
        ]

        # 构建任务数据
        task_data = {
            'task_name': data_field.get('task_name'),
            'file_config': {
                'file_name': data_field.get('file_name'),
                'sheet_num': data_field.get('sheet_num'),
                'title_list': data_field.get('title_list'),
                'column_name': data_field.get('column_name')
            },
            'schedule_config': {
                'trigger_mode': data_field.get('trigger_mode'),
                'time_mode': data_field.get('time_mode'),
                'picker_time': data_field.get('picker_time'),
                'weekday_list': req.get('week')
            },
            'variables_config': variables_config,
            'enable': 1,
            'template_id': template_id
        }

        # 数据库事务
        # 创建任务
        task = ScheduledTask(**task_data)

        # 批量处理接收人
        job_numbers = [emp['value'] for emp in selected_employees]
        employees = Employees.query.filter(
            Employees.job_number.in_(job_numbers)
        ).all()
        task.employees.extend(employees)

        db.session.add(task)
        db.session.flush()  # 获取task.id

        # 添加定时任务
        trigger_config = create_scheduler_trigger(task_data['schedule_config'])
        if trigger_config:
            scheduler.add_job(
                id=str(task.task_id),
                name=task.task_name,
                func=job,
                args=(task.task_id,),
                replace_existing=True,
                **trigger_config
            )

        db.session.commit()
        return success_api(msg="任务添加成功")

    except ValueError as e:
        db.session.rollback()
        return fail_api(msg=f"时间格式错误: {str(e)}")
    except Exception as e:
        db.session.rollback()
        # 记录完整错误日志
        return fail_api(msg=f"任务创建失败: {str(e)}")


# 任务删除
@bp.delete('/remove/<int:id>')
@authorize("mission:task:remove", log=True)
def remove(id):
    task = ScheduledTask.query.get(id)
    job = scheduler.get_job(str(id))
    if job:
        scheduler.remove_job(str(id))
    if not task:
        return fail_api(msg="任务不存在")

    try:
        # 删除该模板的任务
        task.employees = []
        db.session.delete(task)
        db.session.commit()
        return success_api(msg="任务删除成功")
    except Exception as e:
        return fail_api(msg=f"任务删除失败: {str(e)}")


# 批量删除
@bp.delete('/batchRemove')
@authorize("mission:task:remove", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')

    if not ids:
        return fail_api(msg="未提供删除 ID")

    for id in ids:
        if not id.isdigit():
            db.session.rollback()
            return fail_api(msg="参数提供错误")

        id = int(id)

        task = ScheduledTask.query.filter_by(task_id=id).first()
        # 删除该任务的接收人
        task.employees = []

        if task:
            # 删除模板对应任务
            task.SchedulerLog = []
            db.session.delete(task)
        else:
            return fail_api(msg="批量删除失败")
        if scheduler.get_job(str(id)):
            scheduler.remove_job(str(id))
    db.session.commit()

    return success_api(msg="批量删除成功")

# 任务编辑
@bp.get('/edit/<int:id>')
@authorize("mission:task:edit", log=True)
def edit(id):
    task = ScheduledTask.query.get(id)
    data = []
    templates = TaskTemplate.query.all()
    for template in templates:
        variables = VariableHandler.extract_variables(text=template.sql_template)
        data.append({
            'id': task.template_id,
            'template_name': template.template_name,
            'template_id': template.id,
            'template_type': template.template_type,
            'variables': list(variables)
        })
    employees = Employees.query.filter(Employees.status==1)

    return render_template('mission/task/edit.html', task=task, data=data, employees=employees)

# 任务更新
@bp.post('/update')
@authorize("mission:task:edit", log=True)
def update():
    req = request.get_json(force=True)
    try:
        # 数据解析
        data_field = req['data_field']
        selected_employees = req['selected_employees']
        # 获取任务对象
        task = ScheduledTask.query.get(data_field.get('task_id'))
        # 模板处理
        template = TaskTemplate.query.get(task.template_id)
        if not template:
            return fail_api(msg="模板不存在")

        # 变量处理优化
        variables = VariableHandler.extract_variables(text=template.sql_template)
        variables_config = [
            {f"variable_{i}": data_field[f"{v}_{i}"]
             for i in ["name", "type", "value"]}
            for v in variables
        ]

        # 构建任务数据
        schedule_config = {
            'trigger_mode': data_field.get('trigger_mode'),
            'time_mode': data_field.get('time_mode'),
            'picker_time': data_field.get('picker_time'),
            'weekday_list': req.get('week')
        }

        file_config = {
            'file_name': data_field.get('file_name'),
            'sheet_num': data_field.get('sheet_num'),
            'title_list': data_field.get('title_list'),
            'column_name': data_field.get('column_name')
        }
        # 更新任务
        task.task_name = data_field.get('task_name')
        task.file_config = file_config
        task.schedule_config = schedule_config
        task.variables_config = variables_config

        # 批量处理接收人
        job_numbers = [emp['value'] for emp in selected_employees]
        employees = Employees.query.filter(
            Employees.job_number.in_(job_numbers)
        ).all()
        task.employees = []
        task.employees.extend(employees)

        # 添加定时任务
        trigger_config = create_scheduler_trigger(schedule_config)
        if trigger_config:
            scheduler.add_job(
                id=str(task.task_id),
                name=task.task_name,
                func=job,
                args=(task.task_id,),
                replace_existing=True,
                **trigger_config
            )

        db.session.commit()
        return success_api(msg="任务更新成功")

    except ValueError as e:
        db.session.rollback()
        return fail_api(msg=f"时间格式错误: {str(e)}")
    except Exception as e:
        db.session.rollback()
        # 记录完整错误日志
        return fail_api(msg=f"任务更新失败: {str(e)}")

@bp.post('/run/<int:task_id>')
@authorize("mission:task:run", log=True)
def run_task(task_id):
    try:
        # 获取任务对象
        task = ScheduledTask.query.get(task_id)
        if not task:
            return fail_api(msg="任务不存在")

        # 调用调度器执行任务
        my_job = scheduler.get_job(str(task.task_id))
        if my_job:
            scheduler.run_job(id=str(task.task_id))
        else:
            job(task_id=task.task_id, trigger_mode="手动执行")

        return success_api(msg="任务已执行完毕")
    except Exception as e:
        return fail_api(msg=f"任务执行失败: {str(e)}")

# 启用任务
@bp.put('/enable')
@authorize("mission:task:edit", log=True)
def enable():
    task_id = request.get_json(force=True).get('task_id')
    if task_id:
        role = ScheduledTask.query.filter_by(task_id=task_id).update({"enable": 1})
        if role:
            db.session.commit()
            scheduler.resume_job(task_id)
            return success_api(msg="任务已开启")
        return fail_api(msg="出错啦")
    return fail_api(msg="数据错误")


# 暂停任务
@bp.put('/disable')
@authorize("mission:task:edit", log=True)
def dis_enable():
    task_id = request.get_json(force=True).get('task_id')
    if task_id:
        role = ScheduledTask.query.filter_by(task_id=task_id).update({"enable": 0})
        if role:
            db.session.commit()
            scheduler.pause_job(task_id)
            return success_api(msg="任务已暂停")
        return fail_api(msg="出错啦")
    return fail_api(msg="数据错误")