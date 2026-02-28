from applications.extensions import db
from sqlalchemy import JSON
class ScheduledTask(db.Model):
    __tablename__ = 'scheduled_task'
    task_id = db.Column(db.Integer, primary_key=True, comment='任务ID')
    task_name = db.Column(db.String(30), comment='任务名称', nullable=False)
    file_config = db.Column(JSON, comment='文件配置', nullable=False)
    schedule_config = db.Column(JSON, comment='调度配置', nullable=False)
    variables_config = db.Column(JSON,comment='变量配置', nullable=False)
    # 任务是否开启
    enable = db.Column(db.Integer, comment='是否开启', nullable=False, default=1)
    # 关联模板
    template_id = db.Column(db.Integer, db.ForeignKey('task_template.id'), comment='模板ID', nullable=False)
    # 关联Excel模板
    excel_template_id = db.Column(db.Integer, db.ForeignKey('admin_excel.id'), comment='Excel模板ID', nullable=True)
    # 关联接收人
    employees = db.relationship("Employees", secondary="task_employee", backref="scheduled_task", lazy=True)
    # 关联日志
    execution_log = db.relationship('ExecutionLog', backref='scheduled_task', cascade="all, delete-orphan")
    # 关联Excel模板
    excel_template = db.relationship("AdminExcel", backref="scheduled_tasks", lazy=True, foreign_keys=[excel_template_id])