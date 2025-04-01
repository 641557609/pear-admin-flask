import re
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import selectinload
from applications.config import BaseConfig
from applications.models import Employees
from applications.models import ScheduledTask
from applications.services.database_service import SQLServerExecutor
from applications.services.file_service import ExcelGenerator
from applications.services.notification_service import NotificationService
from applications.services.variable_service import VariableHandler
from applications.services.split_excel_service import split_excel_by_column
from applications.services.logger_service import ExecutionLogger
from applications.extensions.init_apscheduler import scheduler
from sqlalchemy import create_engine


# 初始化执行器
executor = SQLServerExecutor(create_engine(
            BaseConfig.SQL_SERVER_URI,
            pool_size=BaseConfig.SQL_SERVER_POOL_SIZE,
            pool_recycle=BaseConfig.SQL_SERVER_POOL_RECYCLE,
            pool_timeout=BaseConfig.SQL_SERVER_POOL_TIMEOUT,
        ))
# 初始化文件生成器
generator = ExcelGenerator(output_dir=BaseConfig.REPORT_OUTPUT_DIR)
# 初始化通知工具
notification_service = NotificationService()
# 初始化变量处理工具
variable_handler = VariableHandler()


def job(task_id, **kwargs):
    start_time = datetime.now()
    with scheduler.app.app_context():
        logger = ExecutionLogger(task_id, **kwargs)
        try:
            task = ScheduledTask.query.options(selectinload(ScheduledTask.employees)).filter_by(task_id=task_id).first()
            task_template = task.task_template
            # 获取原始SQL
            sql_template = task_template.sql_template
            # 替换
            executed_template = template_handler(sql_template)
            # 获取变量
            variables = variable_handler.resolve(task.variables_config)
            # 更新语句
            if task_template.template_type == "更新语句":
                # 结果字典
                results = []
                executed_sql = ""
                for index, template in enumerate(executed_template.split('$$$')):
                    template = template.strip()
                    # 执行查询
                    result = executor.execute(template, variables)
                    results.append(result)
                    executed_sql += executor.return_executed_sql(template, variables)
                # 记录更新日志
                logger.commit(task=task, executed_sql=executed_sql, start_time=start_time)
            # 查询语句
            # 主逻辑
            if task_template.template_type == "查询语句":
                try:
                    file_config = task.file_config
                    # 处理模板执行
                    sheet_num = file_config.get("sheet_num")
                    title_list = file_config["title_list"].split(',') if sheet_num == "多页" else file_config["title_list"]

                    query_results = process_template_results(
                        executed_template=executed_template,
                        title_list=title_list,
                        sheet_num=sheet_num,
                        variables=variables
                    )

                    # 处理报告生成和发送

                    # 生成文件
                    report_path = process_report_generation(task, query_results)
                    process_report_sending(task, report_path)

                    # 存储执行的sql
                    executed_sql = executor.return_executed_sql(executed_template, variables)
                    # 记录日志
                    logger.commit(
                        task=task,
                        executed_sql=executed_sql,
                        result_path=str(report_path),
                        start_time=start_time
                    )
                except json.JSONDecodeError:
                    print("文件配置格式错误")
                except KeyError as e:
                    print(f"缺少必要配置项: {str(e)}")
                except ValueError as e:
                    print(f"配置验证失败: {str(e)}")
                except Exception as e:
                    logger.commit(task=task, error=e)
                    raise
        except Exception as e:
                logger.commit(error=e)  # 捕获未处理的异常
                raise

def template_handler(sql_template: str) -> str :
    return re.sub(r'\{\{\s*(\w+)\s*}}', r':\1', sql_template)


def process_template_results(executed_template, title_list, sheet_num, variables):
    """处理执行模板并返回分页结果"""
    template_list = [t.strip() for t in executed_template.split('$$$') if t.strip()]

    query_results = {}
    for index, template in enumerate(template_list):
        try:
            result = executor.execute(template, variables)
            if sheet_num == "多页":
                query_results[title_list[index]] = [result]
            else:
                query_results.setdefault(title_list, []).append(result)
        except Exception as e:
            print(f"执行模板失败: {template}\n错误信息: {str(e)}")
            raise
    return query_results


def send_report_with_retry(file_path, receivers, max_retries=BaseConfig.NOTIFICATION_RETRIES):
    """带重试机制的文件发送"""
    for attempt in range(max_retries):
        try:
            send_result = notification_service.send_report(
                file_path=Path(file_path),
                receivers=receivers,
                channel="teenrun"
            )
            if send_result["success"] or send_result.get('message') == '推送完成':
                return send_result
            print(f"发送失败，第{attempt + 1}次重试: {send_result.get('message', '未知错误')}")
        except Exception as e:
            print(f"发送异常: {str(e)}")


def process_report_generation(task, query_results):
    """处理文件生成逻辑"""
    file_config = task.file_config

    # 生成主报告文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    file_name = f"{file_config.get('file_name','未指定文件名')}-{timestamp}.xlsx"

    try:
        report_path = generator.generate(datas=query_results, filename=file_name, max_col_width=40)
        print(f"生成主文件: {report_path}")
        return report_path
    except Exception as e:
        print(f"文件生成失败: {str(e)}")
        raise



def process_report_sending(task, report_path):
    """处理文件发送逻辑"""
    file_config = task.file_config

    # 发送主报告
    main_receivers = [emp.job_number for emp in task.employees]
    main_send_result = send_report_with_retry(report_path, main_receivers)
    handle_send_result(main_send_result)

    # 处理分拆文件
    column_name = file_config.get("column_name")
    if column_name is not None:
        try:
            # 发送拆分报告
            split_results = split_excel_by_column(report_path, column_name=column_name)
            process_split_files(split_results)
        except Exception as e:
            print(f"文件分拆失败: {str(e)}")


def handle_send_result(send_result):
    """统一处理发送结果"""
    if send_result["success"]:
        print(f"发送成功:{', '.join(send_result['success_receivers'])}")
    else:
        print(f"最终发送失败: {send_result.get('message', '未知错误')}")
        print(f"失败接收人: {', '.join(send_result.get('failed_receivers'))}")


def process_split_files(split_results):
    """处理分拆后的文件"""
    # 批量获取所有接收人信息
    receiver_names = [r["接收人"] for r in split_results]
    employees = Employees.query.filter(Employees.name.in_(receiver_names)).all()
    emp_mapping = {emp.name: emp for emp in employees}

    for result in split_results:
        receiver_name = result["接收人"]
        emp = emp_mapping.get(receiver_name)
        if emp:
            send_result = send_report_with_retry(result["文件名"], [emp.job_number])
            handle_send_result(send_result)
        else:
            print(f"找不到对应员工: {receiver_name}")

# 处理调度时间
def create_scheduler_trigger(schedule_config):
    """创建定时任务触发器配置"""
    trigger_mode = schedule_config.get('trigger_mode')
    time_mode = schedule_config.get('time_mode')

    if trigger_mode == 'by_timing':
        run_date = datetime.fromisoformat(schedule_config.get('picker_time'))
        return {
            'trigger': 'date',
            'run_date': run_date
        }

    if trigger_mode == 'by_plan':
        if time_mode == 'every_hour':
            exec_time = datetime.strptime(
                schedule_config.get('picker_time'),
                '%H:%M:%S'
            ).time()
            return {
                'trigger': 'interval',
                'hours': exec_time.hour,
                'minutes': exec_time.minute,
                'seconds': exec_time.second
            }

        elif time_mode == 'every_day':
            exec_time = datetime.strptime(
                schedule_config.get('picker_time'),
                '%H:%M:%S'
            ).time()
            return {
                'trigger': 'cron',
                'hour': exec_time.hour,
                'minute': exec_time.minute,
                'second': exec_time.second
            }

        elif time_mode == 'every_week':
            exec_time = datetime.strptime(
                schedule_config.get('picker_time'),
                '%H:%M:%S'
            ).time()
            return {
                'trigger': 'cron',
                'day_of_week': ','.join(schedule_config.get('weekday_list', [])),
                'hour': exec_time.hour,
                'minute': exec_time.minute,
                'second': exec_time.second
            }

        elif time_mode == 'every_month':
            exec_date = datetime.strptime(
                schedule_config.get('picker_time'),
                '%d日%H:%M:%S'
            )
            return {
                'trigger': 'cron',
                'day': exec_date.day,
                'hour': exec_date.hour,
                'minute': exec_date.minute,
                'second': exec_date.second
            }

    # 默认返回None表示无需定时
    return None




