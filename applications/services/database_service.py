from contextlib import contextmanager
from sqlalchemy import text
import re

class SQLServerExecutor:
    """专用于SQL Server的查询执行器（直接使用引擎连接）"""

    def __init__(self, engine):
        self.engine = engine  # 直接保存引擎实例

    @contextmanager
    def _scoped_connection(self):
        """自动作用域连接管理"""
        connection = self.engine.connect()
        transaction = connection.begin()  # 显式开启事务
        try:
            yield connection
            transaction.commit()  # 成功时提交
        except Exception as e:
            transaction.rollback()  # 异常时回滚
            raise
        finally:
            connection.close()  # 确保连接关闭

    def execute(self, sql: str, params: dict = None):
        """直接通过引擎连接执行原始SQL"""
        with self._scoped_connection() as connection:
            # 提取SQL中的参数名（如 `:id` → 'id'）
            expected_params = set(re.findall(r":(\w+)", sql))
            # 过滤掉多余的参数
            filtered_params = {k: v for k, v in (params or {}).items() if k in expected_params}
            # 使用text()实现参数化查询
            stmt = text(sql).bindparams(**filtered_params) if filtered_params else text(sql)
            result = connection.execute(stmt)

            # 自动判断查询类型并格式化结果
            if result.returns_rows:
                return self._format_query_result(result)
            return {"affected_rows": result.rowcount}

    def return_executed_sql(self, sql: str, params: dict = None):
        """返回实际执行的SQL（参数替换后）"""
        # 提取SQL中的参数名（如 `:id` → 'id'）
        expected_params = set(re.findall(r":(\w+)", sql))
        # 过滤掉多余的参数
        filtered_params = {k: v for k, v in (params or {}).items() if k in expected_params}
        for key, value in filtered_params.items():
            sql = re.sub(rf":{key}\b", f"'{value}'", sql)  # 替换参数为实际值
        return sql

    def _format_query_result(self, result):
        """格式化查询结果"""
        return [
            {"headers": [col[0] for col in result.cursor.description]},
            {"data": [row for row in result]}
        ]