from flask import Flask, Blueprint
from applications.view.file.repository import bp as repository_bp

# 创建sys
file_bp = Blueprint('file', __name__, url_prefix='/file')


def register_file_bps(app: Flask):
    # 在admin_bp下注册子蓝图
    file_bp.register_blueprint(repository_bp)
    app.register_blueprint(file_bp)