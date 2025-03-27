from applications.extensions import db
import datetime

class TaskTemplate(db.Model):
    __tablename__ = 'task_template'
    id = db.Column(db.Integer, primary_key=True, comment='模板ID')
    creator = db.Column(db.String(50), comment='创建者')
    template_name = db.Column(db.String(60), comment='模板名称', nullable=False, unique=True)
    remark = db.Column(db.Text, comment='备注')
    sql_template = db.Column(db.Text, comment='原始SQL模板', nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment='更新时间')
    template_type = db.Column(db.String(10), comment='任务类型', nullable=False)
    scheduled_task = db.relationship('ScheduledTask', backref='task_template', cascade="all, delete-orphan")