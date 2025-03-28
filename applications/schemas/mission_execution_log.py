from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from applications.models import ExecutionLog
from marshmallow import fields

class ExecutionLogSchema(SQLAlchemyAutoSchema):
    run_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = ExecutionLog
        include_relationships = True  # 输出模型对象时同时对外键，是否也一并进行处理
        include_fk = True  # 序列化阶段是否也一并返回主键
        # fields= ["id","name"] # 启动的字段列表
        # exclude =               # 排除字段列表
    task_name = fields.Method("get_task_name")
    trigger_mode = fields.Method("get_trigger_mode")

    def get_task_name(self, obj):
        if obj.task_id:
            return obj.scheduled_task.task_name
        return None

    def get_trigger_mode(self, obj):
        if obj.trigger_mode == 'by_plan':
            return '计划触发'
        elif obj.trigger_mode == 'by_timing':
            return '定时触发'
        elif obj.trigger_mode == 'by_user':
            return '手动触发'
        else:
            return obj.trigger_mode
