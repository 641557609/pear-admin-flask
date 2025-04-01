import datetime
from flask import send_from_directory
import os
from flask import Blueprint, render_template, current_app,request
from applications.common.utils.rights import authorize
from applications.common.utils.http import table_api

bp = Blueprint('repository', __name__, url_prefix='/repository')

@bp.get('/')
@authorize("mission:file:main")
def main():
    return render_template('file/repository/main.html')

# 添加下载路由
@bp.get('/download/<filename>')
@authorize("mission:file:download")
def download_file(filename):
    directory = os.path.join(current_app.root_path, 'custom_reports')
    return send_from_directory(directory, filename, as_attachment=True)


@bp.get('/data')
@authorize("mission:file:main")
def table_data():
    file_name = request.args.get('file_name', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    files = []
    dir_path = os.path.join(current_app.root_path, 'custom_reports')

    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)
        if os.path.isfile(path):
            stat = os.stat(path)
            file_ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
            file_data = {
                "name": filename,
                "size": stat.st_size,
                "ctime": datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            }
            # 添加过滤条件（以下是新增逻辑）
            # 文件名过滤（大小写不敏感）
            if file_name and file_name.lower() not in filename.lower():
                continue

            # 日期范围过滤
            if start_date and end_date:
                file_date = file_ctime.date()
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                if not (start <= file_date <= end):
                    continue

            files.append(file_data)


    return table_api(data=files, count=len(files), limit=20)