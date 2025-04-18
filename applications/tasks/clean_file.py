from applications.extensions.init_apscheduler import scheduler
import os
import datetime
from calendar import monthrange

# @scheduler.task('interval', id='clean_file', name='clean_file', days='7')
def clean_file():
    report_folder = 'pear_admin_flask/../../../custom_reports'
    # 计算三个月前的精确日期（自然月）
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    # 处理跨年情况
    if month <= 0:
        year -= 1
        month += 12

    # 获取目标月份的最后一天
    _, last_day = monthrange(year, month)
    day = min(now.day, last_day)  # 处理月末边界情况

    # 生成三个月前的日期对象
    three_months_ago = datetime.datetime(year, month, day)

    print(f"正在清理 {report_folder} 中早于 {three_months_ago} 创建的文件...")

    # 遍历文件夹
    deleted_count = 0

    for root, dirs, files in os.walk(report_folder):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                # 获取文件创建时间（Windows 系统）
                ctime = os.path.getctime(file_path)
                ctime_date = datetime.datetime.fromtimestamp(ctime)

                # 判断是否过期
                if ctime_date >= three_months_ago:
                    continue
                if os.path.exists(file_path):
                    print(f"[待删除] {file_path} （创建时间：{ctime_date}）")
                    os.remove(file_path)
                    print(f"已删除：{file_path}（创建时间：{ctime_date}）")
                    deleted_count += 1

            except Exception as e:
                print(f"处理文件 {file_path} 时出错：{str(e)}")

    print(f"清理完成，共删除 {deleted_count} 个文件")
