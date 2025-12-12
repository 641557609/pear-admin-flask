from applications.extensions import db
from datetime import datetime


class AdminExcel(db.Model):
    """Excel文件管理模型"""
    __tablename__ = 'admin_excel'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='ID')
    name = db.Column(db.String(255), comment='文件名')
    original_name = db.Column(db.String(255), comment='原始文件名')
    href = db.Column(db.String(255), comment='文件路径')
    mime = db.Column(db.String(255), comment='文件类型')
    size = db.Column(db.Integer, comment='文件大小')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')
    description = db.Column(db.String(500), comment='文件描述')
    status = db.Column(db.Integer, default=1, comment='状态：0-禁用，1-启用')

    def __repr__(self):
        return f'<AdminExcel {self.name}>'