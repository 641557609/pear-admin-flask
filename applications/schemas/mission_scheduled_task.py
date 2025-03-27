from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from applications.models import ScheduledTask
from marshmallow import fields
from applications.extensions.init_apscheduler import scheduler

class ScheduledTaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ScheduledTask
        include_relationships = True  # 输出模型对象时同时对外键，是否也一并进行处理
        include_fk = True  # 序列化阶段是否也一并返回主键
        # fields= ["id","name"] # 启动的字段列表
        exclude = ["variables_config","schedule_config","file_config"] # 排除字段列表

    # 如果需要从关联模型中提取数据，可以使用 fields.Method
    receiver = fields.Method("get_employee_names")
    template_name = fields.Method("get_template_name")
    trigger_mode = fields.Method("get_trigger_mode")
    run_time = fields.Method("get_run_time")
    enable = fields.Method("get_enable")

    def get_employee_names(self, obj):
        if obj.employees:
            return ",".join([employee.name for employee in obj.employees])
        return "未选择接收人"

    def get_template_name(self, obj):
        if obj.task_template:
            return obj.task_template.template_name
        return '出错啦'

    def get_trigger_mode(self, obj):
        if obj.schedule_config['trigger_mode'] == 'by_plan':
            return '计划触发'
        elif obj.schedule_config['trigger_mode'] == 'by_timing':
            return '定时触发'
        elif obj.schedule_config['trigger_mode'] == 'by_user':
            return '手动触发'
        else:
            return '出错啦'

    def get_run_time(self, obj):
        if obj.schedule_config['trigger_mode'] == 'by_user':
            return '--'
        job = scheduler.get_job(str(obj.task_id))
        if not job:
            return obj.schedule_config['picker_time']
        next_run_time = job.next_run_time
        if next_run_time is None:
            return '任务已暂停'
        else:
            return next_run_time.strftime('%Y-%m-%d %H:%M:%S')

    def get_enable(self, obj):
        return True if obj.enable else False