from marshmallow import Schema, fields


class AdminExcelOutSchema(Schema):
    """Excel文件输出Schema"""
    id = fields.Integer()
    name = fields.Str()
    original_name = fields.Str()
    href = fields.Str()
    mime = fields.Str()
    size = fields.Integer()
    upload_time = fields.DateTime()
    description = fields.Str()
    status = fields.Integer()


class AdminExcelInSchema(Schema):
    """Excel文件输入Schema"""
    name = fields.Str(required=True)
    original_name = fields.Str(required=True)
    href = fields.Str(required=True)
    mime = fields.Str(required=True)
    size = fields.Integer(required=True)
    description = fields.Str()
    status = fields.Integer()