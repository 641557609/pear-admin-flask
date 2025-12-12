from flask import Flask
from flask_uploads import configure_uploads
from flask_uploads import UploadSet, DOCUMENTS

# 创建Excel上传集
excel_files = UploadSet('excelfiles', ('xlsx', 'xls', 'csv'))

def init_excel_upload(app: Flask):
    """初始化Excel上传集"""
    configure_uploads(app, excel_files)
