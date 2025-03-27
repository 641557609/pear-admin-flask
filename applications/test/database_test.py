from sqlalchemy import create_engine
from applications.services.database_service import SQLServerExecutor
import unittest
from applications import BaseConfig
from ..services.file_service import ExcelGenerator
class Test(unittest.TestCase):
    def test_database(self):

        # 初始化执行器
        executor = SQLServerExecutor(create_engine(
            BaseConfig.SQL_SERVER_URI,
            pool_size=BaseConfig.SQL_SERVER_POOL_SIZE,
            pool_recycle=BaseConfig.SQL_SERVER_POOL_RECYCLE,
            pool_timeout=BaseConfig.SQL_SERVER_POOL_TIMEOUT,
        ))

        results = {}
        # 执行SQL
        result = executor.execute("""select b.shopgroupid '运营体',b.dept_name '店铺',a.item_bh 'SKU',a.amount '数量',c.qc_time '单件质检时间'  from stor_dtl  a with(nolock)
                                        left join sys_department b with(nolock) on a.ovs_deptid = b.dept_code
                                        left join v_item_inf c on a.item_bh = c.item_bh where stor_wh_code = 'NH' and qc_dt>=:sdt and qc_dt<:edt""", params={'edt': '2025-02-01', 'sdt': '2025-02-28'})
        print(result)
        # 处理结果
        results['测试1'] = [result]
        results['测试2'] = [result]
        generator = ExcelGenerator(output_dir="custom_reports")
        try:
            file_path = generator.generate(datas=results, filename="test.xlsx", max_col_width=40)
            print(f"生成文件路径: {file_path}")
        except Exception as e:
            print(f"生成失败: {str(e)}")




