# 用于生成Excel并存储的模块
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime
from typing import Dict, List
from pathlib import Path


class ExcelGenerator:
    # 样式配置（可扩展）
    # 表头样式
    HEADER_STYLE = {
        'fill': PatternFill(start_color="C7E4B3", fill_type="solid"),
        'font': Font(bold=True, size=9, name='微软雅黑'),
        'alignment': Alignment(horizontal="center", vertical="center")
    }
    # 内容样式
    DATA_STYLE = {
        'font': Font(size=9, name='微软雅黑'),
        'alignment': Alignment(horizontal="center", vertical="justify")
    }

    def __init__(self, output_dir: str = "static/upload"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
            self,
            datas: Dict[str, List[List[Dict[str, list]]]],
            filename: str = None,
            max_col_width: int = 60
    ) -> Path:
        """
        生成Excel文件核心方法

        参数:
        results: {
            "Sheet1": [
                {"headers": ["ID", "Name"]},
                {"data": [(1, "Alice"), (2, "Bob")]}
            ]
        }
        filename: 指定文件名（自动添加时间戳）
        max_col_width: 最大列宽限制
        """
        wb = Workbook()
        self._remove_default_sheet(wb)

        for sheet_name, content in datas.items():
            ws = self._create_worksheet(wb, sheet_name)
            self._process_sheet_content(ws, content, max_col_width)

        return self._save_workbook(wb, filename)

    def _create_worksheet(self, wb: Workbook, title: str):
        """创建并激活工作表"""
        ws = wb.create_sheet(title=title)
        wb.active = ws
        return ws

    def _process_sheet_content(
            self,
            ws,
            content: List[List[Dict[str, list]]],
            max_col_width: int
    ):
        """处理单个工作表内容"""


        # 分离header和data
        for section_list in content:
            header_data = None
            all_data = []
            for section in section_list:
                if 'headers' in section:
                    header_data = section['headers']
                elif 'data' in section:
                    all_data.extend(section['data'])

            if header_data:
                self._write_headers(ws, header_data)
            if all_data:
                self._write_data(ws, all_data)
                self._auto_adjust_columns(ws, max_col_width)

    def _write_headers(self, ws, headers: list):
        """写入表头并应用样式"""
        ws.append(headers)
        for cell in ws[ws.max_row]:
            for style_type, style in self.HEADER_STYLE.items():
                setattr(cell, style_type, style)

    def _write_data(self, ws, data: list):
        """批量写入数据行"""
        for row in data:
            ws.append(list(row))
            self._apply_data_style(ws)

    def _apply_data_style(self, ws):
        """应用数据行样式"""
        for cell in ws[ws.max_row]:
            for style_type, style in self.DATA_STYLE.items():
                setattr(cell, style_type, style)

    def _auto_adjust_columns(self, ws, max_width: int):
        """智能列宽调整（带最大宽度限制）"""
        for col in ws.columns:
            max_length = 0
            column = get_column_letter(col[0].column)

            for cell in col:
                cell_value = self._format_cell_value(cell.value)
                max_length = max(max_length, len(str(cell_value)))

            adjusted_width = min(max_length + 7, max_width)
            ws.column_dimensions[column].width = adjusted_width

    def _format_cell_value(self, value):
        """格式化特殊数据类型"""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value

    def _save_workbook(self, wb: Workbook, filename: str = None) -> Path:
        """保存文件并返回路径对象"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        file_path = self.output_dir / filename
        wb.save(file_path)
        return file_path

    @staticmethod
    def _remove_default_sheet(wb: Workbook):
        """移除默认的空白Sheet"""
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']



