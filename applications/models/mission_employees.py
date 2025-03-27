from applications.extensions import db

class Employees(db.Model):
    __tablename__ = 'employees'
    job_number = db.Column(db.String(20), primary_key=True, comment='员工工号')
    name = db.Column(db.String(20), comment='员工姓名')
    status = db.Column(db.Boolean, comment='员工状态')
