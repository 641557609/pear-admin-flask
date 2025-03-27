import unittest
from datetime import datetime
from ..services.file_service import ExcelGenerator

class Test(unittest.TestCase):
    def test_init(self):
        generator = ExcelGenerator(output_dir="custom_reports")
        # 准备数据
        sample_data = {
            "Sales": [[
                {"headers": ["Date", "Amount"]},
                {"data": [
                    (datetime(2023, 1, 1), 1000),
                    (datetime(2023, 1, 2), 2000)
                ]}],[
                {"headers": ["Date", "Amount"]},
                {"data": [
                    (datetime(2023, 1, 1), 1000),
                    (datetime(2023, 1, 2), 2000)
                ]}],[
                {"headers": ["ID", "Name"]},
                {"data": [
                    (1, "Alice"), (2, "Bob")
                ]}]
            ],
            "Users": [
                [{"headers": ["ID", "Name"]},
                {"data": [(1, "Alice"), (2, "Bob")]}]
            ]
        }
        # 生成文件
        try:
            report_path = generator.generate(datas=sample_data, filename="monthly_report.xlsx", max_col_width=40)
            print(f"生成文件路径: {report_path}")
        except Exception as e:
            print(f"生成失败: {str(e)}")
    def test_ge(self):
        variables = []
        print([
        {f"variable_{i}": f"{v}_{i}" for i in ["name", "type", "value"]}
        for v in variables
    ])