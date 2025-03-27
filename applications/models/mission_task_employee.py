from applications.extensions import db

# 创建中间表
task_employee = db.Table(
    "task_employee",  # 中间表名称
    db.Column("id", db.Integer, primary_key=True, autoincrement=True, comment='标识'),  # 主键
    db.Column("task_id", db.Integer, db.ForeignKey("scheduled_task.task_id"), comment='任务编号'),  # 属性 外键
    db.Column("job_number", db.String(20), db.ForeignKey("employees.job_number"), comment='员工编号'),  # 属性 外键
)