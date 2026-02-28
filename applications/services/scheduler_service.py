import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Union
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from applications.config import BaseConfig
from concurrent.futures import ThreadPoolExecutor, as_completed
from applications.models import Employees, AdminExcel,ScheduledTask
from applications.services.database_service import SQLServerExecutor
from applications.services.file_service import ExcelGenerator
from applications.services.notification_service import NotificationService
from applications.services.variable_service import VariableHandler
from applications.services.logger_service import ExecutionLogger
from applications.extensions.init_apscheduler import scheduler
from sqlalchemy import create_engine

# 配置日志
logger = logging.getLogger(__name__)


# 初始化执行器
def get_executor():
    """获取数据库执行器实例（懒加载）"""
    if not hasattr(get_executor, '_instance'):
        try:
            get_executor._instance = SQLServerExecutor(create_engine(
                BaseConfig.SQL_SERVER_URI,
                pool_size=BaseConfig.SQL_SERVER_POOL_SIZE,
                pool_recycle=BaseConfig.SQL_SERVER_POOL_RECYCLE,
                pool_timeout=BaseConfig.SQL_SERVER_POOL_TIMEOUT,
            ))
            logger.info("数据库执行器初始化成功")
        except Exception as e:
            logger.error(f"数据库执行器初始化失败: {str(e)}")
            raise
    return get_executor._instance


# 初始化文件生成器
def get_generator():
    """获取文件生成器实例（懒加载）"""
    if not hasattr(get_generator, '_instance'):
        try:
            get_generator._instance = ExcelGenerator(output_dir=BaseConfig.REPORT_OUTPUT_DIR)
            logger.info("文件生成器初始化成功")
        except Exception as e:
            logger.error(f"文件生成器初始化失败: {str(e)}")
            raise
    return get_generator._instance


# 初始化通知工具
def get_notification_service():
    """获取通知服务实例（懒加载）"""
    if not hasattr(get_notification_service, '_instance'):
        try:
            get_notification_service._instance = NotificationService()
            logger.info("通知服务初始化成功")
        except Exception as e:
            logger.error(f"通知服务初始化失败: {str(e)}")
            raise
    return get_notification_service._instance


# 初始化变量处理工具
def get_variable_handler():
    """获取变量处理工具实例（懒加载）"""
    if not hasattr(get_variable_handler, '_instance'):
        try:
            get_variable_handler._instance = VariableHandler()
            logger.info("变量处理工具初始化成功")
        except Exception as e:
            logger.error(f"变量处理工具初始化失败: {str(e)}")
            raise
    return get_variable_handler._instance


def job(task_id, **kwargs):
    """主任务执行函数"""
    start_time = datetime.now()
    logger.info(f"开始执行任务: {task_id}")

    with scheduler.app.app_context():
        logger_instance = ExecutionLogger(task_id, **kwargs)
        try:
            # 获取任务信息
            task = _get_task_with_relations(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")

            # 处理SQL模板
            executed_template = _process_sql_template(task)
            # 解析变量
            variables = _resolve_variables(task)

            # 根据模板类型执行不同逻辑
            if task.task_template.template_type == "更新语句":
                _handle_update_statement(task, executed_template, variables, logger_instance, start_time)
            elif task.task_template.template_type == "查询语句":
                _handle_query_statement(task, executed_template, variables, logger_instance, start_time)
            else:
                raise ValueError(f"未知的模板类型: {task.task_template.template_type}")

            logger.info(f"任务执行成功: {task_id}")

        except (DatabaseError, ConnectionError) as e:
            logger.error(f"数据库操作失败，任务ID: {task_id}, 错误: {str(e)}")
            logger_instance.commit(error=e)
            raise
        except FileNotFoundError as e:
            logger.error(f"文件不存在，任务ID: {task_id}, 错误: {str(e)}")
            logger_instance.commit(error=e)
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"配置错误，任务ID: {task_id}, 错误: {str(e)}")
            logger_instance.commit(error=e)
            raise
        except Exception as e:
            logger.error(f"未知错误，任务ID: {task_id}, 错误: {str(e)}")
            logger_instance.commit(error=e)
            raise


def _get_task_with_relations(task_id: str):
    """获取任务及其关联信息"""
    try:
        task = ScheduledTask.query.options(selectinload(ScheduledTask.employees)).filter_by(task_id=task_id).first()
        if not task:
            logger.warning(f"任务不存在: {task_id}")
        return task
    except SQLAlchemyError as e:
        logger.error(f"数据库查询失败，任务ID: {task_id}, 错误: {str(e)}")
        raise


def _process_sql_template(task) -> str:
    """处理SQL模板"""
    sql_template = task.task_template.sql_template
    executed_template = template_handler(sql_template)
    logger.debug(f"SQL模板处理完成，任务ID: {task.task_id}")
    return executed_template


def _resolve_variables(task) -> Dict[str, Any]:
    """解析变量配置"""
    try:
        variables = get_variable_handler().resolve(task.variables_config)
        logger.debug(f"变量解析完成，任务ID: {task.task_id}")
        return variables
    except Exception as e:
        logger.error(f"变量解析失败，任务ID: {task.task_id}, 错误: {str(e)}")
        raise


def _handle_update_statement(task, executed_template: str, variables: Dict, logger_instance: ExecutionLogger,
                             start_time: datetime):
    """处理更新语句"""
    logger.info(f"开始执行更新语句，任务ID: {task.task_id}")

    results = []
    executed_sql = ""
    template_list = [t.strip() for t in executed_template.split('$$$') if t.strip()]

    for index, template in enumerate(template_list):
        try:
            result = get_executor().execute(template, variables)
            results.append(result)
            executed_sql += get_executor().return_executed_sql(template, variables)
            logger.debug(f"更新语句执行成功，模板索引: {index}, 任务ID: {task.task_id}")
        except Exception as e:
            logger.error(f"更新语句执行失败，模板索引: {index}, 任务ID: {task.task_id}, 错误: {str(e)}")
            raise

    logger_instance.commit(task=task, executed_sql=executed_sql, start_time=start_time)
    logger.info(f"更新语句执行完成，任务ID: {task.task_id}")


def _handle_query_statement(task, executed_template: str, variables: Dict, logger_instance: ExecutionLogger,
                            start_time: datetime):
    """处理查询语句"""
    logger.info(f"开始执行查询语句，任务ID: {task.task_id}")

    try:
        # 验证文件配置
        if not _validate_file_config(task.file_config):
            raise ValueError("文件配置验证失败")

        file_config = task.file_config
        sheet_num = file_config.get("sheet_num")
        title_list = file_config["title_list"].split(',') if sheet_num == "多页" else file_config["title_list"]

        # 处理模板执行
        query_results = process_template_results(
            executed_template=executed_template,
            title_list=title_list,
            sheet_num=sheet_num,
            variables=variables
        )
        # 生成和发送报告
        report_file = process_report_generation(task, query_results)
        report_path = process_report_sending(report_file)

        # 记录执行日志
        executed_sql = get_executor().return_executed_sql(executed_template, variables)
        logger_instance.commit(
            task=task,
            executed_sql=executed_sql,
            result_path=report_path[:100],
            start_time=start_time
        )

        logger.info(f"查询语句执行完成，任务ID: {task.task_id}")

    except json.JSONDecodeError as e:
        logger.error(f"文件配置格式错误，任务ID: {task.task_id}, 错误: {str(e)}")
        raise
    except KeyError as e:
        logger.error(f"缺少必要配置项，任务ID: {task.task_id}, 错误: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"配置验证失败，任务ID: {task.task_id}, 错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"查询语句执行失败，任务ID: {task.task_id}, 错误: {str(e)}")
        logger_instance.commit(task=task, error=e)
        raise


def _validate_file_config(file_config: Dict) -> bool:
    """验证文件配置的完整性"""
    required_fields = ['sheet_num', 'title_list', 'file_name']
    missing_fields = [field for field in required_fields if field not in file_config]
    if missing_fields:
        logger.error(f"文件配置缺少必要字段: {missing_fields}")
        return False
    return True


def template_handler(sql_template: str) -> str:
    """处理SQL模板中的变量占位符"""
    return re.sub(r'\{\{\s*(\w+)\s*}}', r':\1', sql_template)


def process_template_results(executed_template: str, title_list: Union[str, List[str]], sheet_num: str,
                             variables: Dict[str, Any]) -> Dict[str, List]:
    """处理执行模板并返回分页结果"""
    template_list = [t.strip() for t in executed_template.split('$$$') if t.strip()]
    query_results = {}

    for index, template in enumerate(template_list):
        try:
            result = get_executor().execute(template, variables)
            if sheet_num == "多页":
                query_results[title_list[index]] = [result]
            else:
                query_results.setdefault(title_list, []).append(result)
            logger.debug(f"模板执行成功，索引: {index}, 模板: {template[:50]}...")
        except Exception as e:
            logger.error(f"模板执行失败，索引: {index}, 模板: {template}, 错误: {str(e)}")
            raise e
    return query_results


def send_report_with_retry(file_path: str, receivers: List[str],
                           max_retries: int = BaseConfig.NOTIFICATION_RETRIES) -> Dict:
    """带重试机制的文件发送"""
    logger.info(f"开始发送文件: {file_path}, 接收人: {receivers}")

    for attempt in range(max_retries):
        try:
            send_result = get_notification_service().send_report(
                file_path=Path(file_path),
                receivers=receivers,
                channel="teenrun"
            )
            if send_result["success"] or send_result.get('message') == '推送完成':
                logger.info(f"文件发送成功: {file_path}, 接收人: {receivers}")
                return send_result
            logger.warning(f"发送失败，第{attempt + 1}次重试: {send_result.get('message', '未知错误')}")
        except Exception as e:
            logger.error(f"发送异常，第{attempt + 1}次重试，文件: {file_path}, 错误: {str(e)}")
            continue

    logger.error(f"文件发送失败，超过最大重试次数: {file_path}")
    return {"success": False, "message": "发送失败，超过最大重试次数"}


def process_report_generation(task, query_results: Dict) -> Dict[str, Path]:
    """处理文件生成逻辑，直接从数据库查询结果进行拆分"""
    file_config = task.file_config
    report_files = {}
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    try:
        # 检查是否需要分拆
        column_name = file_config.get("column_name")

        if column_name is not None:
            # 直接从数据库查询结果进行拆分
            split_files = process_direct_split_generation(query_results, column_name, file_config, timestamp)
            report_files.update(split_files)
            logger.info(f"直接分拆完成，共生成 {len(split_files)} 个分拆文件")

        main_file_name = f"{file_config.get('file_name', '未指定文件名')}-{timestamp}.xlsx"

        # 检查是否使用Excel模板
        use_excel_template = file_config.get('use_excel_template', False)
        excel_template_id = file_config.get('excel_template_id')

        if use_excel_template and excel_template_id:
            # 获取Excel模板路径
            excel_template = AdminExcel.query.get(excel_template_id)
            if excel_template and excel_template.href:
                # 使用模板生成文件
                main_report_path = get_generator().generate(
                    datas=query_results,
                    filename=main_file_name,
                    max_col_width=40,
                    template_path=excel_template.href
                )
                logger.info(f"使用模板生成主报告文件成功: {main_report_path}")
            else:
                # 模板不存在，使用普通生成
                main_report_path = get_generator().generate(datas=query_results, filename=main_file_name,
                                                            max_col_width=40)
                logger.warning(f"Excel模板不存在，使用普通方式生成文件: {main_report_path}")
        else:
            # 不使用模板，普通生成
            main_report_path = get_generator().generate(datas=query_results, filename=main_file_name, max_col_width=40)
            logger.info(f"主报告文件生成成功: {main_report_path}")
        report_files.update({emp.job_number: main_report_path for emp in task.employees})

        return report_files

    except Exception as e:
        logger.error(f"文件生成失败: {str(e)}")
        raise


def process_direct_split_generation(query_results: Dict, column_name: str, file_config: Dict, timestamp: str) -> Dict[
    str, Path]:
    """直接从数据库查询结果进行拆分和文件生成（多线程版本）"""
    split_files = {}

    # 获取所有接收人列表
    all_receivers = set()

    # 第一阶段：收集所有接收人信息
    for sheet_name, data_list in query_results.items():
        for data in data_list:
            if data and len(data) > 0:
                # 数据结构：data 包含 headers 和 data 两个部分
                headers = data[0].get('headers', [])
                rows_data = data[1].get('data', [])

                # 找到列名对应的索引
                if column_name in headers:
                    column_index = headers.index(column_name)
                    # 遍历数据行，提取接收人信息
                    for row in rows_data:
                        if len(row) > column_index:
                            receiver = str(row[column_index] or "").strip()
                            if receiver:
                                all_receivers.add(receiver)
                else:
                    logger.warning(f"在工作表 {sheet_name} 中未找到列名: {column_name}")
    if not all_receivers:
        logger.warning(f"未找到有效的接收人信息，列名: {column_name}")
        return split_files

    # 检查是否使用Excel模板
    use_excel_template = file_config.get('use_excel_template', False)
    excel_template_id = file_config.get('excel_template_id')
    template_path = None

    if use_excel_template and excel_template_id:
        # 获取Excel模板路径
        excel_template = AdminExcel.query.get(excel_template_id)
        if excel_template and excel_template.href:
            template_path = excel_template.href
        else:
            logger.warning(f"Excel模板不存在，ID: {excel_template_id}")
    else:
        logger.info("未配置Excel模板，将使用普通方式生成文件")

    # 第二阶段：为每个接收人生成单独的文件（多线程处理）
    def generate_receiver_file(receiver):
        """为单个接收人生成文件的函数"""
        try:
            receiver_data = {}

            # 为每个接收人筛选数据
            for sheet_name, data_list in query_results.items():
                receiver_data[sheet_name] = []

                for data in data_list:
                    if data and len(data) > 0:
                        headers = data[0].get('headers', [])
                        rows_data = data[1].get('data', [])

                        # 找到列名对应的索引
                        if column_name in headers:
                            column_index = headers.index(column_name)

                            filtered_rows = []
                            # 筛选该接收人的数据行
                            for row in rows_data:
                                if len(row) > column_index and str(row[column_index] or "").strip() == receiver:
                                    filtered_rows.append(row)

                            receiver_data[sheet_name].append([data[0], {'data': filtered_rows}])

            # 生成文件
            safe_receiver = "".join(c if c.isalnum() else '_' for c in receiver)
            file_name = f"{file_config.get('file_name', '未指定文件名')}-{safe_receiver}-{timestamp}.xlsx"
            # 使用模板或普通方式生成文件
            if template_path:
                file_path = get_generator().generate(
                    datas=receiver_data,
                    filename=file_name,
                    max_col_width=40,
                    template_path=template_path
                )
            else:
                file_path = get_generator().generate(datas=receiver_data, filename=file_name, max_col_width=40)
            logger.debug(f"直接分拆文件生成成功: {file_path} -> {receiver}")
            return receiver, file_path

        except Exception as e:
            logger.error(f"接收人 {receiver} 的文件生成失败: {str(e)}")
            return receiver, None

    # 使用线程池并行处理文件生成
    max_workers = min(len(all_receivers), 8)  # 限制最大线程数为8或接收人数量
    logger.info(f"开始使用 {max_workers} 个线程并行生成 {len(all_receivers)} 个文件")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_receiver = {executor.submit(generate_receiver_file, receiver): receiver for receiver in all_receivers}

        # 收集结果
        success_count = 0
        fail_count = 0

        for future in as_completed(future_to_receiver):
            receiver = future_to_receiver[future]
            try:
                result_receiver, file_path = future.result()
                if file_path:
                    split_files[result_receiver] = file_path
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                logger.error(f"接收人 {receiver} 的文件生成线程异常: {str(e)}")
                fail_count += 1

    logger.info(f"文件生成完成: 成功 {success_count} 个, 失败 {fail_count} 个, 总计 {len(all_receivers)} 个")
    receiver_names = list(split_files.keys())
    employees = Employees.query.filter(Employees.name.in_(receiver_names)).all()
    emp_mapping = {emp.name: emp.job_number for emp in employees}
    # 将split_files中的接收人映射为员工对象
    for receiver_name in receiver_names:
        if receiver_name in emp_mapping:
            split_files.update({emp_mapping[receiver_name]: split_files.pop(receiver_name)})
    return split_files



def process_report_sending(report_files: Dict[str, Path]) -> str:
    """处理所有文件的发送逻辑"""
    # 找出相同路径的键并拼接
    path_to_keys = {}
    for key, path in report_files.items():
        path_str = str(path)
        if path_str not in path_to_keys:
            path_to_keys[path_str] = []
        path_to_keys[path_str].append(key)
    report_path = ''
    for file_path, receivers in path_to_keys.items():
        report_path += str(file_path) + ','
        send_report_with_retry(str(file_path), receivers)
    return report_path

# 处理调度时间
def create_scheduler_trigger(schedule_config: Dict):
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
