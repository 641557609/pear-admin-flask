from applications.extensions import db
from datetime import datetime
from applications.models import ScheduledTask, ExecutionLog


class ExecutionLogger:
    """统一执行日志记录服务"""

    def __init__(self, task_id: int):
        self.task_id = task_id
        self.log = ExecutionLog(
            task_id=task_id,
            run_time=datetime.now(),
            status='初始化',
            trigger_mode='未知'
        )

    def _prepare_base_info(self, task: ScheduledTask):
        """准备基础任务信息"""
        self.log.task_name = task.task_name
        self.log.trigger_mode = task.schedule_config.get('trigger_mode')

    def _record_sql(self, executed_sql: str):
        """记录执行的SQL"""
        self.log.executed_sql = executed_sql[:4000]

    def _record_success(self, result_path: str = None):
        """记录成功状态"""
        self.log.status = '成功'
        if result_path:
            self.log.result_path = str(result_path)

    def _record_failure(self, error: Exception):
        """记录失败详情"""
        self.log.status = '失败'
        error_detail = f"{type(error).__name__}: {str(error)}"
        self.log.error_detail = error_detail

    def _record_execution_time(self, start_time):
        """记录任务执行时长"""
        self.log.execution_time = int((datetime.now() - start_time).total_seconds())

    def commit(self, task: ScheduledTask = None,
               executed_sql: str = None,
               result_path: str = None,
               error: Exception = None,
               start_time = None):
        """
        提交日志记录
        :param task: 关联的任务对象
        :param executed_sql: 实际执行的SQL
        :param result_path: 生成的文件路径
        :param error: 异常对象
        :param start_time: 任务开始时间
        """
        try:
            if task:
                self._prepare_base_info(task)

            if executed_sql:
                self._record_sql(executed_sql)

            if start_time:
                self._record_execution_time(start_time)

            if error:
                self._record_failure(error)
            else:
                self._record_success(result_path)

            db.session.add(self.log)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"日志提交失败: {str(e)}")


