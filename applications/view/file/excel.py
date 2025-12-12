from flask import Blueprint, request, jsonify, render_template
from applications.common.utils.excel_upload import (
    get_excel_files, upload_excel_file, delete_excel_file_by_id, get_excel_file_by_id,
    verify_file_consistency, cleanup_orphan_files
)
from applications.extensions import db
from flask import current_app
from applications.common import curd
from applications.models import AdminExcel
from applications.schemas import AdminExcelOutSchema
from applications.common.utils.http import table_api, success_api, fail_api

excel_bp = Blueprint('excel', __name__, url_prefix='/excel')


@excel_bp.get('/')
def main():
    """Excel文件管理主页面"""
    return render_template('file/excel/excel.html')

@excel_bp.get('/upload')
def upload_page():
    """Excel文件上传页面"""
    return render_template('file/excel/excel_upload.html')

@excel_bp.post('/upload')
def upload_excel():
    """上传Excel文件接口"""
    try:
        if 'file' not in request.files:
            return fail_api('请选择文件')

        file = request.files['file']
        if file.filename == '':
            return fail_api('文件名为空')

        # 检查文件类型
        allowed_extensions = {'xls', 'xlsx', 'csv'}
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return fail_api('只支持xls, xlsx, csv格式的文件')

        description = request.form.get('description', '')
        upload_excel_file(file, file.content_type, description)
        return success_api('上传成功')

    except Exception as e:
        return fail_api(f'上传失败: {str(e)}')


@excel_bp.get('/list')
def get_excel_list():
    """获取Excel文件列表"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        data, count = get_excel_files(page, limit)
        return table_api(msg='获取成功', count=count, data=data, limit=limit)

    except Exception as e:
        return fail_api(f'获取列表失败: {str(e)}')


@excel_bp.delete('/delete/<int:file_id>')
def delete_excel(file_id):
    """删除Excel文件"""
    try:
        success = delete_excel_file_by_id(file_id)
        if success:
            return success_api('删除成功')
        else:
            return fail_api('文件不存在')

    except Exception as e:
        return fail_api(f'删除失败: {str(e)}')


@excel_bp.get('/detail/<int:file_id>')
def get_excel_detail(file_id):
    """获取Excel文件详情"""
    try:
        excel_file = get_excel_file_by_id(file_id)
        if not excel_file:
            return fail_api('文件不存在')

        return jsonify(success=True, data=curd.model_to_dicts(AdminExcelOutSchema, excel_file))

    except Exception as e:
        return fail_api(f'获取详情失败: {str(e)}')


# 在excel.py文件中添加批量删除接口
@excel_bp.post('/batch_delete')
def batch_delete_excel():
    """批量删除Excel文件"""
    try:
        ids = request.form.getlist('ids[]') or request.json.get('ids', [])
        if not ids:
            return fail_api('请选择要删除的文件')

        success_count = 0
        for file_id in ids:
            if delete_excel_file_by_id(file_id):
                success_count += 1

        return success_api(f'成功删除{success_count}个文件')

    except Exception as e:
        return fail_api(f'批量删除失败: {str(e)}')


@excel_bp.get('/consistency_check')
def consistency_check():
    """检查文件一致性"""
    try:
        inconsistencies = verify_file_consistency()
        return jsonify({
            'success': True,
            'data': inconsistencies,
            'count': len(inconsistencies),
            'msg': f'发现 {len(inconsistencies)} 个不一致项'
        })
    except Exception as e:
        return fail_api(f'一致性检查失败: {str(e)}')


@excel_bp.post('/cleanup_orphan_files')
def cleanup_orphan_files_endpoint():
    """清理孤立文件"""
    try:
        cleaned_files = cleanup_orphan_files()
        return success_api(f'成功清理 {len(cleaned_files)} 个孤立文件')
    except Exception as e:
        return fail_api(f'清理孤立文件失败: {str(e)}')


@excel_bp.post('/repair_inconsistencies')
def repair_inconsistencies():
    """修复不一致的文件记录"""
    try:
        inconsistencies = verify_file_consistency()
        repaired_count = 0

        for item in inconsistencies:
            if item['type'] == 'missing_file':
                # 文件不存在但数据库记录存在，删除数据库记录
                AdminExcel.query.filter_by(id=item['record_id']).delete()
                repaired_count += 1
                current_app.logger.info(f"已删除缺失文件的数据库记录: {item['record_id']}")

        db.session.commit()

        # 清理孤立文件
        cleaned_files = cleanup_orphan_files()

        return success_api(f'成功修复 {repaired_count} 个数据库记录，清理 {len(cleaned_files)} 个孤立文件')

    except Exception as e:
        db.session.rollback()
        return fail_api(f'修复不一致项失败: {str(e)}')
