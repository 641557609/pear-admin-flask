import os
import uuid
from flask import current_app
from sqlalchemy import desc
from applications.extensions import db
from applications.extensions.init_excel_upload import excel_files
from applications.models import AdminExcel
from applications.schemas import AdminExcelOutSchema
from applications.common.curd import model_to_dicts


def get_excel_files(page, limit):
    """获取Excel文件列表"""
    excel_files = AdminExcel.query.order_by(desc(AdminExcel.upload_time)).paginate(
        page=page, per_page=limit, error_out=False
    )
    count = AdminExcel.query.count()
    data = model_to_dicts(schema=AdminExcelOutSchema, data=excel_files.items)
    return data, count


def upload_excel_file(excel_file, mime, description=None):
    """上传Excel文件"""
    try:
        # 开始事务
        db.session.begin_nested()

        # 生成唯一文件名
        original_filename = excel_file.filename
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

        # 保存文件
        filename = excel_files.save(excel_file, name=unique_filename)
        file_url = f'/static/excel/{filename}'

        # 获取文件大小
        upload_url = current_app.config.get("UPLOADED_EXCEL_DEST", "static/excel")
        file_path = os.path.join(upload_url, filename)

        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件保存失败: {file_path}")

        size = os.path.getsize(file_path)
        # 将MIME类型转换为用户友好的描述
        friendly_mime = get_friendly_file_type(mime, original_filename)

        # 保存到数据库
        excel_record = AdminExcel(
            name=filename,
            original_name=original_filename,
            href=file_url,
            mime=friendly_mime,
            size=size,
            description=description
        )
        db.session.add(excel_record)
        db.session.commit()

        return {
            'file_url': file_url,
            'filename': filename,
            'original_name': original_filename,
            'size': size,
            'id': excel_record.id
        }

    except Exception as e:
        # 发生异常时回滚数据库事务
        db.session.rollback()

        # 如果文件已保存但数据库操作失败，删除已保存的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
                current_app.logger.info(f"已删除因数据库操作失败而保存的文件: {file_path}")
            except Exception as delete_error:
                current_app.logger.error(f"删除文件失败: {delete_error}")

        current_app.logger.error(f"文件上传失败: {str(e)}")
        raise e


def get_friendly_file_type(mime_type, filename):
    """将MIME类型转换为用户友好的文件类型描述"""

    # 优先根据文件扩展名判断
    if '.' in filename:
        extension = filename.rsplit('.', 1)[1].lower()
        extension_map = {
            'xls': 'Excel 97-2003 文件',
            'xlsx': 'Excel 文件',
            'csv': 'CSV 文件',
            'pdf': 'PDF 文档',
            'doc': 'Word 97-2003 文档',
            'docx': 'Word 文档',
            'ppt': 'PowerPoint 97-2003 演示文稿',
            'pptx': 'PowerPoint 演示文稿',
            'txt': '文本文件',
            'jpg': 'JPEG 图像',
            'jpeg': 'JPEG 图像',
            'png': 'PNG 图像',
            'gif': 'GIF 图像',
            'zip': '压缩文件',
            'rar': 'RAR 压缩文件',
            '7z': '7-Zip 压缩文件',
            'xml': 'XML 文件',
            'json': 'JSON 文件',
            'html': 'HTML 文件',
            'htm': 'HTML 文件',
            'js': 'JavaScript 文件',
            'css': 'CSS 文件',
            'py': 'Python 脚本',
            'java': 'Java 文件',
            'cpp': 'C++ 文件',
            'c': 'C 文件',
            'h': 'C/C++ 头文件',
            'php': 'PHP 文件',
            'rb': 'Ruby 文件',
            'go': 'Go 文件',
            'sql': 'SQL 文件',
            'md': 'Markdown 文件',
            'yml': 'YAML 文件',
            'yaml': 'YAML 文件',
            'ini': '配置文件',
            'conf': '配置文件',
            'cfg': '配置文件',
            'log': '日志文件',
            'bat': '批处理文件',
            'sh': 'Shell 脚本',
            'ps1': 'PowerShell 脚本'
        }

        if extension in extension_map:
            return extension_map[extension]

    # 如果扩展名无法识别，尝试根据MIME类型判断
    mime_type_map = {
        'application/vnd.ms-excel': 'Excel 97-2003 文件',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel 文件',
        'text/csv': 'CSV 文件',
        'application/pdf': 'PDF 文档',
        'application/msword': 'Word 97-2003 文档',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word 文档',
        'application/vnd.ms-powerpoint': 'PowerPoint 97-2003 演示文稿',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint 演示文稿',
        'text/plain': '文本文件',
        'image/jpeg': 'JPEG 图像',
        'image/png': 'PNG 图像',
        'image/gif': 'GIF 图像',
        'image/bmp': 'BMP 图像',
        'image/tiff': 'TIFF 图像',
        'image/svg+xml': 'SVG 图像',
        'application/zip': '压缩文件',
        'application/x-rar-compressed': 'RAR 压缩文件',
        'application/x-7z-compressed': '7-Zip 压缩文件',
        'application/x-tar': 'TAR 压缩文件',
        'application/gzip': 'GZIP 压缩文件',
        'application/x-bzip2': 'BZIP2 压缩文件',
        'text/xml': 'XML 文件',
        'application/json': 'JSON 文件',
        'text/html': 'HTML 文件',
        'text/css': 'CSS 文件',
        'application/javascript': 'JavaScript 文件',
        'application/x-python-code': 'Python 脚本',
        'text/x-java-source': 'Java 文件',
        'text/x-c': 'C 文件',
        'text/x-c++': 'C++ 文件',
        'text/x-php': 'PHP 文件',
        'application/x-ruby': 'Ruby 文件',
        'text/x-go': 'Go 文件',
        'application/sql': 'SQL 文件',
        'text/markdown': 'Markdown 文件',
        'application/x-yaml': 'YAML 文件',
        'text/x-ini': '配置文件',
        'text/plain': '日志文件',
        'application/x-msdos-program': '可执行文件',
        'application/x-sh': 'Shell 脚本',
        'application/x-powershell': 'PowerShell 脚本',
        'audio/mpeg': 'MP3 音频',
        'audio/wav': 'WAV 音频',
        'video/mp4': 'MP4 视频',
        'video/avi': 'AVI 视频',
        'video/x-msvideo': 'AVI 视频',
        'application/octet-stream': '二进制文件'
    }

    if mime_type in mime_type_map:
        return mime_type_map[mime_type]

    # 如果都无法识别，根据MIME类型的主类型返回通用描述
    if mime_type:
        main_type = mime_type.split('/')[0]
        type_descriptions = {
            'application': '应用程序文件',
            'text': '文本文件',
            'image': '图像文件',
            'audio': '音频文件',
            'video': '视频文件',
            'font': '字体文件',
            'model': '3D模型文件'
        }

        return type_descriptions.get(main_type, mime_type)

    return '未知文件类型'

def delete_excel_file_by_id(_id):
    """根据ID删除Excel文件"""
    try:
        # 开始事务
        db.session.begin_nested()

        excel_record = AdminExcel.query.filter_by(id=_id).first()
        if not excel_record:
            return False

        # 先获取文件路径信息
        upload_url = current_app.config.get("UPLOADED_EXCELFILES_DEST", "static/excel")
        file_path = os.path.join(upload_url, excel_record.name)

        # 检查文件是否存在
        file_exists = os.path.exists(file_path)

        # 删除数据库记录
        AdminExcel.query.filter_by(id=_id).delete()
        db.session.commit()

        # 如果文件存在，删除物理文件
        if file_exists:
            try:
                os.remove(file_path)
                current_app.logger.info(f"成功删除文件: {file_path}")
            except Exception as delete_error:
                current_app.logger.error(f"删除物理文件失败: {delete_error}")
                # 文件删除失败，但数据库记录已删除，记录日志但不回滚
                # 可以考虑在这里记录到异常表或发送通知
        else:
            current_app.logger.warning(f"文件不存在，但数据库记录已删除: {file_path}")

        return True

    except Exception as e:
        # 发生异常时回滚数据库事务
        db.session.rollback()
        current_app.logger.error(f"文件删除失败: {str(e)}")
        return False


def get_excel_file_by_id(_id):
    """根据ID获取Excel文件信息"""
    return AdminExcel.query.filter_by(id=_id).first()


def verify_file_consistency():
    """验证数据库记录和物理文件的一致性"""
    try:
        upload_url = current_app.config.get("UPLOADED_EXCELFILES_DEST", "static/excel")

        # 获取所有数据库记录
        db_records = AdminExcel.query.all()

        inconsistencies = []

        for record in db_records:
            file_path = os.path.join(upload_url, record.name)

            if not os.path.exists(file_path):
                inconsistencies.append({
                    'type': 'missing_file',
                    'record_id': record.id,
                    'filename': record.name,
                    'original_name': record.original_name
                })
                current_app.logger.warning(f"文件不存在但数据库记录存在: {file_path}")

        # 检查是否有文件存在但没有数据库记录
        if os.path.exists(upload_url):
            for filename in os.listdir(upload_url):
                file_path = os.path.join(upload_url, filename)
                if os.path.isfile(file_path):
                    record = AdminExcel.query.filter_by(name=filename).first()
                    if not record:
                        inconsistencies.append({
                            'type': 'orphan_file',
                            'filename': filename,
                            'file_path': file_path
                        })
                        current_app.logger.warning(f"文件存在但无数据库记录: {file_path}")

        return inconsistencies

    except Exception as e:
        current_app.logger.error(f"文件一致性检查失败: {str(e)}")
        return []


def cleanup_orphan_files():
    """清理孤立的文件（有文件但无数据库记录）"""
    try:
        upload_url = current_app.config.get("UPLOADED_EXCELFILES_DEST", "static/excel")
        inconsistencies = verify_file_consistency()

        cleaned_files = []

        for item in inconsistencies:
            if item['type'] == 'orphan_file':
                try:
                    os.remove(item['file_path'])
                    cleaned_files.append(item['filename'])
                    current_app.logger.info(f"已清理孤立文件: {item['file_path']}")
                except Exception as delete_error:
                    current_app.logger.error(f"清理孤立文件失败: {delete_error}")

        return cleaned_files

    except Exception as e:
        current_app.logger.error(f"清理孤立文件失败: {str(e)}")
        return []
