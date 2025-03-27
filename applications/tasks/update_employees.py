from applications.extensions import db
from applications.models import Employees
from sqlalchemy.orm import load_only
from applications.extensions.init_apscheduler import scheduler
from applications.services.scheduler_service import executor
import traceback
# traceback.print_exc()

@scheduler.task('cron', id='update_employees', name='update_employees', day='28')
def update_employees():
    with scheduler.app.app_context():
        try:
            # 从另一数据库获取在职人员信息
            sql = """SELECT Name, JobNum, status 
                     FROM sys_user 
                     WHERE status = '1' 
                     AND ISNULL(jobNum, '') != ''"""
            result = executor.execute(sql=sql)
            # 构建当前在职人员字典 {工号: 人员信息}
            current_employees = {row[1]:{"name": row[0],"status": int(row[2])} for row in result[1]["data"]}
            current_job_numbers = set(current_employees.keys())

            # 获取现有员工信息 {工号: 员工对象}
            existing_employees = {e.job_number: e for e in Employees.query.options(
                load_only(Employees.job_number, Employees.status)
            ).all()}

            # 批量更新状态
            # 1. 更新当前在职人员状态为1
            if current_job_numbers:
                # 分批处理避免SQL语句过长
                batch_size = 1000
                current_job_list = list(current_job_numbers)
                for i in range(0, len(current_job_list), batch_size):
                    batch = current_job_list[i:i + batch_size]
                    Employees.query.filter(Employees.job_number.in_(batch)).update(
                        {"status": 1},
                        synchronize_session=False
                    )

            # 2. 更新离职人员状态为0
            existing_job_numbers = set(existing_employees.keys())
            if existing_job_numbers - current_job_numbers:
                # 分批处理
                batch_size = 1000
                obsolete_job_list = list(existing_job_numbers - current_job_numbers)
                for i in range(0, len(obsolete_job_list), batch_size):
                    batch = obsolete_job_list[i:i + batch_size]
                    Employees.query.filter(Employees.job_number.in_(batch)).update(
                        {"status": 0},
                        synchronize_session=False
                    )

            # 3. 批量插入新员工
            new_job_numbers = current_job_numbers - existing_job_numbers
            if new_job_numbers:
                new_employees = [
                    Employees(
                        name=current_employees[job_num]["name"],
                        job_number=job_num,
                        status=current_employees[job_num]["status"]
                    )
                    for job_num in new_job_numbers
                ]
                db.session.bulk_save_objects(new_employees)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"发生错误：{e}")
            traceback.print_exc()
            # 建议添加更完善的错误处理（如日志记录）