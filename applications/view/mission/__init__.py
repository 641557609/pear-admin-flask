from flask import Flask, Blueprint
from applications.view.mission.task import bp as task_bp
from applications.view.mission.template import bp as template_bp
from applications.view.mission.logger import bp as logger_bp
# 创建sys
mission_bp = Blueprint('mission', __name__, url_prefix='/mission')


def register_mission_bps(app: Flask):
    # 在admin_bp下注册子蓝图
    mission_bp.register_blueprint(task_bp)
    mission_bp.register_blueprint(template_bp)
    mission_bp.register_blueprint(logger_bp)
    app.register_blueprint(mission_bp)