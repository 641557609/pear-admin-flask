from applications.extensions import db
class ExecutionLog(db.Model):
    __tablename__ = 'execution_log'
    logger_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='运行日志编号')
    executed_sql =  db.Column(db.Text, comment='实际执行的SQL')
    status = db.Column(db.String(10), comment='运行结果')
    result_path = db.Column(db.String(256), comment='Excel文件存储路径')
    task_name = db.Column(db.String(60), comment='任务名称')
    run_time = db.Column(db.DateTime, comment='运行时间')
    trigger_mode = db.Column(db.String(10), comment='触发方式')
    execution_time = db.Column(db.Float, comment='执行耗时（秒）')
    error_detail = db.Column(db.Text, comment='异常堆栈信息')
    task_id = db.Column(db.Integer, db.ForeignKey('scheduled_task.task_id'), comment='任务编号')

