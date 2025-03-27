from applications.extensions.init_apscheduler import scheduler

# @scheduler.task('interval', id='test', seconds=2, name='test')
# def test():
#     with scheduler.app.app_context():
#         print(scheduler.app.name)