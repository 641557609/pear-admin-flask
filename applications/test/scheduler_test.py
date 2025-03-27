from applications.services.scheduler_service import create_scheduler_trigger
import unittest

class Test(unittest.TestCase):
    def test_create_scheduler_trigger(self):
        scheduler_config = {
            'trigger_mode': "by_timing",
            'time_mode': None,
            'picker_time': "2025-06-01 06:00:00",
            'weekday_list': None
        }
        print(create_scheduler_trigger(scheduler_config))
        scheduler_config = {
            'trigger_mode': "by_plan",
            'time_mode': "every_hour",
            'picker_time': "06:00:00",
            'weekday_list': None
        }
        print(create_scheduler_trigger(scheduler_config))
        scheduler_config = {
            'trigger_mode': "by_plan",
            'time_mode': "every_day",
            'picker_time': "06:00:00",
            'weekday_list': None
        }
        print(create_scheduler_trigger(scheduler_config))
        scheduler_config = {
            'trigger_mode': "by_plan",
            'time_mode': "every_week",
            'picker_time': "06:00:00",
            'weekday_list': ['0','1','2','3','4','5','6']
        }
        print(create_scheduler_trigger(scheduler_config))
        scheduler_config = {
            'trigger_mode': "by_plan",
            'time_mode': "every_month",
            'picker_time': "06-01 06:00:00",
            'weekday_list': None
        }
        print(create_scheduler_trigger(scheduler_config))


