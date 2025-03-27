from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from applications.models import TaskTemplate
from marshmallow import fields

class TaskTemplateSchema(SQLAlchemyAutoSchema):
    # 显式覆盖 created_at 字段，自定义日期格式
    update_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    class Meta:
        model = TaskTemplate
        # include_relationships = True  # 输出模型对象时同时对外键，是否也一并进行处理
        include_fk = True  # 序列化阶段是否也一并返回主键
        # fields= ["id","name"] # 启动的字段列表
        # exclude = ["variables_config"] # 排除字段列表