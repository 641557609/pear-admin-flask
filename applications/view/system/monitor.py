import os
import re
import sys
import time
import psutil
import platform

from datetime import datetime

from flask import Blueprint, render_template

from applications.common.utils.http import table_api, success_api
from applications.common.utils.rights import authorize
from applications.common.utils.cache import cache_auto_internal


bp = Blueprint('adminMonitor', __name__, url_prefix='/monitor')


def get_disk_partitions_list():
    disk_partitions_list = []
    # 判断是否在容器中
    if not os.path.exists('/.dockerenv'):
        disk_partitions = psutil.disk_partitions()
        for i in disk_partitions:
            try:
                a = psutil.disk_usage(i.device)
            except PermissionError:
                continue

            disk_partitions_dict = {
                'device': i.device,
                'fstype': i.fstype,
                'total': a.total,
                'used': a.used,
                'free': a.free,
                'percent': a.percent
            }
            disk_partitions_list.append(disk_partitions_dict)
    else:
        try:
            usage = psutil.disk_usage('/')
        except PermissionError:
            pass

        disk_partitions_list.append({
            'device': '/',  # 设备名称（根文件系统）
            'fstype': psutil.disk_partitions()[0].fstype,  # 文件系统类型
            'total': usage.total,  # 总容量（字节）
            'used': usage.used,  # 已用空间（字节）
            'free': usage.free,  # 可用空间（字节）
            'percent': usage.percent  # 使用百分比
        })

    return disk_partitions_list

def get_basic_info():
    # 主机名称
    hostname = platform.node()
    # 系统版本
    system_version = platform.platform()
    # Python 版本
    python_version = platform.python_version()

    # 开机时间
    boot_time = datetime.fromtimestamp(psutil.boot_time()).replace(microsecond=0)
    up_time = datetime.now().replace(microsecond=0) - boot_time
    up_time_list = re.split(r':', str(up_time))
    up_time_format = "{} 小时 {} 分钟 {} 秒".format(up_time_list[0], up_time_list[1], up_time_list[2])
    up_time_format = up_time_format.replace("days,", "天")

    return {
        'hostname': hostname,
        'system_version': system_version,
        'python_version': python_version,
        'boot_time': boot_time,
        'up_time_format': up_time_format
    }

# 系统监控
@bp.get('/')
@authorize("system:monitor:main")
def main():


    # 当前时间
    time_now = time.strftime('%H:%M:%S ', time.localtime(time.time()))
    return render_template(
        'system/monitor.html',
        time_now=time_now,
        **get_basic_info()
    )


# 图表 api
@bp.get('/polling')
@authorize("system:monitor:main")
def ajax_polling():
    # 获取 CPU 核心数
    cpu_count = cache_auto_internal('cpu_count', lambda: psutil.cpu_count(), expired=999999999)

    # 获取 CPU 使用率
    cpus_percent = cache_auto_internal('cpus_percent',
                                       lambda: psutil.cpu_percent(interval=1, percpu=False),
                                       expired=5)

    # 每个 CPU 的使用率
    cpu_percent_per_core = cache_auto_internal('cpu_percent_per_core',
                                               lambda: list(enumerate(psutil.cpu_percent(interval=1, percpu=True))),
                                               expired=5)

    # 获取空闲率、等待率
    cpu_times_percent = cache_auto_internal('cpu_times_percent',
                                            lambda: psutil.cpu_times_percent(interval=1, percpu=False),
                                            expired=5)

    # 内存信息
    memory_information = cache_auto_internal('memory_information',
                                             psutil.virtual_memory,
                                             expired=5)

    # 硬盘信息
    disk_partitions_list = cache_auto_internal('disk_partitions_list',
                                               get_disk_partitions_list,
                                               expired=5)

    # 系统信息
    basic_info = cache_auto_internal('basic_info',
                                     get_basic_info,
                                     expired=5)

    memory_usage = memory_information.percent
    memory_used = memory_information.used
    memory_total = memory_information.total
    memory_free = memory_information.free

    cpu_idle_percent = cpu_times_percent.idle
    if hasattr(cpu_times_percent, 'iowait'):
        cpu_wait_percent = cpu_times_percent.iowait
    else:
        cpu_wait_percent = "-"

    return table_api(msg="请求成功",
                     count=0,
                     data={
                         'cpu_count': cpu_count,
                         'cpus_percent': cpus_percent,
                         'cpu_idle_percent': cpu_idle_percent,
                         'cpu_wait_percent': cpu_wait_percent,
                         'cpu_percent_per_core': cpu_percent_per_core,
                         'memory_used': memory_used,
                         'memory_total': memory_total,
                         'memory_free': memory_free,
                         'memory_usage': memory_usage,
                         'disk_partitions_list': disk_partitions_list,
                         'time_now': time.strftime('%H:%M:%S', time.localtime(time.time())),
                         'basic_info': basic_info
                     })


# 关闭程序
@bp.get('/kill')
@authorize("system:monitor:main")
def kill():
    # 注：若是多 worker 则不生效
    # return success_api(msg="关闭命令已发送，请修改代码以生效。")
    for proc in psutil.process_iter():
        if proc.pid == os.getpid():
            proc.kill()
    sys.exit(1)
