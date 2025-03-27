import datetime
import re
from applications.services.database_service import SQLServerExecutor
from sqlalchemy import create_engine
from applications import BaseConfig



# 变量处理器
class VariableHandler:
    def __init__(self):
        self.executor = SQLServerExecutor(create_engine(
            BaseConfig.SQL_SERVER_URI,
            pool_size=BaseConfig.SQL_SERVER_POOL_SIZE,
            pool_recycle=BaseConfig.SQL_SERVER_POOL_RECYCLE,
            pool_timeout=BaseConfig.SQL_SERVER_POOL_TIMEOUT,
        ))

    @staticmethod
    def extract_variables(text: str):
        # 正则表达式匹配 {{ 变量名 }} 中的变量名（支持变量名中含字母、数字、下划线、点号）
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\}\}'
        matches = re.findall(pattern, text)
        return set(matches)  # 自动去重


    def resolve(self, variables_config:list) -> dict:
        variables = dict()
        # 获取当前时间
        now = datetime.datetime.now()

        # 计算各个选项对应的时间

        # 计算本月1号和本月末
        current_year, current_month = now.year, now.month
        month_start, month_end = self.get_first_and_last_day_of_month(current_year, current_month)

        # 上月1号和月末
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1
        last_month_start, last_month_end = self.get_first_and_last_day_of_month(last_year, last_month)

        # 下月1号和月末
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        next_month_start, next_month_end = self.get_first_and_last_day_of_month(next_year, next_month)

        # 去年年份
        last_year = now.year - 1

        # 获取去年今月月初和月末
        last_year_month_start, last_year_month_end = self.get_first_and_last_day_of_month(last_year, now.month)

        # 获取去年今天
        last_year_today = datetime.date(last_year, now.month, now.day)

        # 获取去年上月月初和月末
        if now.month == 1:
            last_year_last_month_start, last_year_last_month_end = self.get_first_and_last_day_of_month(last_year - 1, 12)
        else:
            last_year_last_month_start, last_year_last_month_end = self.get_first_and_last_day_of_month(last_year, now.month - 1)

        date_dict = {"MonthStart": month_start, "MonthEnd": month_end, "LastMonthStart": last_month_start,
                  "LastMonthEnd": last_month_end, "NextMonthStart": next_month_start, "NextMonthEnd": next_month_end,
                  "LastYearToday": last_year_today, "LastYearMonthStart": last_year_month_start,
                  "LastYearMonthEnd": last_year_month_end, "LastYearLastMonthStart": last_year_last_month_start,
                  "LastYearLastMonthEnd": last_year_last_month_end}

        for variable in variables_config:
            if variable["variable_type"] == 'timestamp':
                variables[variable["variable_name"]] = str(date_dict.get(variable["variable_value"]))
            elif variable["variable_type"] == 'fixed':
                variables[variable["variable_name"]] = str(variable["variable_value"])
            elif variable["variable_type"] == 'sql':
                result = self.executor.execute(sql=variable["variable_value"])
                variables[variable["variable_name"]] = str(result[1]["data"][0])
        return variables

    def get_first_and_last_day_of_month(self, year, month):
        """
        返回指定年份和月份的第一天和最后一天
        """
        first_day = datetime.date(year, month, 1)
        if month == 12:
            # 如果是12月，则下一年1月为下月
            last_day_of_next_month = datetime.date(year + 1, 1, 1)
        else:
            # 否则，当前月+1为下月
            last_day_of_next_month = datetime.date(year, month + 1, 1)
        last_day = last_day_of_next_month - datetime.timedelta(days=1)
        return first_day, last_day