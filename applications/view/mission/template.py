from flask import Blueprint, render_template, request
from sqlalchemy import and_
from applications.common.utils.rights import authorize
from applications.common.utils.validate import str_escape
from applications.common.utils.http import table_api, fail_api, success_api
from applications.schemas.mission_task_template import TaskTemplateSchema
from applications.models.mission_task_template import TaskTemplate
from applications.extensions import db
from flask_login import current_user
from applications.common.curd import get_one_by_id

bp = Blueprint('template', __name__, url_prefix='/template')


# 首页
@bp.get('/')
@authorize("mission:template:main", log=True)
def main():
    return render_template('mission/template/main.html')

# 表格数据
@bp.get('/data')
@authorize("mission:template:main", log=True)
def table():
    template_name = str_escape(request.args.get('template_name', type=str))
    creator = str_escape(request.args.get('creator', type=str))
    template_type = str_escape(request.args.get('template_type', type=str))
    filters = []
    if template_name:
        filters.append(TaskTemplate.template_name.contains(template_name))
    if creator:
        filters.append(TaskTemplate.creator.contains(creator))
    if template_type:
        filters.append(TaskTemplate.template_type.contains(template_type))
    templates = TaskTemplate.query.filter(*filters).layui_paginate()
    return table_api(data=TaskTemplateSchema(many=True).dump(templates), count=templates.total)

# 模板增加
@bp.get('/add')
@authorize("mission:template:add", log=True)
def add():
    return render_template('mission/template/add.html')

# 模板增加
@bp.post('/save')
@authorize("mission:template:add", log=True)
def save():
    req = request.get_json(force=True)

    data = {
        "template_name": str_escape(req.get("template_name")),  # 模板名称
        "template_type": str_escape(req.get("template_type")),  # 任务类型
        "sql_template": req.get("sql_template"),    # 原始sql
    }

    if not all(data.values()):
        return fail_api(msg="参数不足")

    template_type = "查询语句" if data['template_type'] == '0' else "更新语句"
    data['template_type'] = template_type
    data['remark'] = str_escape(req.get("remark", ""))   # 备注
    data['creator'] = current_user.realname

    # 参数效验
    if TaskTemplate.query.filter_by(template_name=data['template_name']).first():
        return fail_api(msg="模板名称已存在")

    template = TaskTemplate(**data)
    db.session.add(template)
    db.session.commit()
    return success_api(msg="添加模板成功")

# 模板删除
@bp.delete('/remove/<int:id>')
@authorize("mission:template:remove", log=True)
def remove(id):
    template = TaskTemplate.query.filter_by(id=id).first()

    if not template:
        return fail_api(msg="模板不存在")

    # 删除该模板的任务
    template.scheduled_task = []


    t = TaskTemplate.query.filter_by(id=id).delete()
    db.session.commit()
    if not t:
        return fail_api(msg="模板删除失败")
    return success_api(msg="模板删除成功")

# 批量删除
@bp.delete('/batchRemove')
@authorize("mission:template:remove", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')

    if not ids:
        return fail_api(msg="未提供删除 ID")

    for id in ids:

        if not id.isdigit():
            db.session.rollback()
            return fail_api(msg="参数提供错误")

        id = int(id)

        template = TaskTemplate.query.filter_by(id=id).first()
        if template:
            # 删除模板对应任务
            template.scheduled_task = []
            db.session.delete(template)
        else:
            return fail_api(msg="批量删除失败")

    db.session.commit()
    return success_api(msg="批量删除成功")

# 模板编辑
@bp.get('/edit/<int:id>')
@authorize("mission:template:edit", log=True)
def edit(id):
    template = get_one_by_id(model=TaskTemplate, id=id)
    return render_template('mission/template/edit.html', template=template)

# 更新模板
@bp.put('/update')
@authorize("mission:template:edit", log=True)
def update():
    req = request.get_json(force=True)
    id = req.get("id")

    data = {
        "template_name": str_escape(req.get("template_name")),  # 模板名称
        "template_type": str_escape(req.get("template_type")),  # 任务类型
        "sql_template": req.get("sql_template"),  # 原始sql
        "remark": str_escape(req.get("remark"))  # 备注
    }

    remark = data.get('remark')
    del data['remark']

    if not all(data.values()):
        return fail_api(msg="参数不足")

    template_type = "查询语句" if data['template_type'] == '0' else "更新语句"
    data['template_type'] = template_type
    data['remark'] = remark
    data['creator'] = current_user.realname

    # 参数效验
    if TaskTemplate.query.filter(and_(
            TaskTemplate.template_name == data['template_name'],
            TaskTemplate.id != id  # 排除自身
        )).first():
        return fail_api(msg="模板名称已存在")


    template = TaskTemplate.query.filter_by(id=id).update(data)
    db.session.commit()
    if not template:
        return fail_api(msg="更新模板失败")

    return success_api(msg="更新模板成功")