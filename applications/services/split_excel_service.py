import os
import shutil
import openpyxl


def split_excel_by_column(file_path, column_name):
    # 加载原工作簿以确定目标sheet和列索引
    wb = openpyxl.load_workbook(file_path)
    target_sheet_name = None
    col_idx = None
    for sheet in wb:
        for row in sheet.iter_rows(min_row=1, max_row=1):  # 检查表头行
            for cell in row:
                if cell.value == column_name:
                    target_sheet_name = sheet.title
                    col_idx = cell.column  # 获取列索引（从1开始）
                    break
            if target_sheet_name:
                break
        if target_sheet_name:
            break
    if not target_sheet_name:
        wb.close()
        raise ValueError(f"文件中未找到列名 '{column_name}'")
    wb.close()

    # 再次以只读模式打开，快速收集数据行信息
    wb = openpyxl.load_workbook(file_path, read_only=True)
    target_sheet = wb[target_sheet_name]

    # 收集人名及对应的数据行号（从2开始）
    person_row_indices = {}
    for row_idx, row in enumerate(target_sheet.iter_rows(min_row=2), start=2):
        person_cell = row[col_idx - 1]  # 转换为0-based索引
        person = person_cell.value
        if not person:
            continue
        if person not in person_row_indices:
            person_row_indices[person] = []
        person_row_indices[person].append(row_idx)
    wb.close()

    output = []
    original_dir = os.path.dirname(file_path)
    original_filename = os.path.basename(file_path)
    base_name = os.path.splitext(original_filename)[0]

    # 处理每个人名
    for person, row_indices in person_row_indices.items():
        # 生成唯一文件名
        safe_person = "".join(c if c.isalnum() else '_' for c in str(person))
        new_filename = f"{base_name}_{safe_person}.xlsx"
        new_filepath = os.path.join(original_dir, new_filename)

        # 复制原文件为新文件
        shutil.copyfile(file_path, new_filepath)

        # 打开新文件进行修改
        temp_wb = openpyxl.load_workbook(new_filepath)
        temp_sheet = temp_wb[target_sheet_name]

        # 收集需要删除的行号（所有数据行不在当前人名的行号列表中）
        all_data_rows = set(range(2, temp_sheet.max_row + 1))
        keep_rows = set(row_indices)
        delete_rows = sorted(all_data_rows - keep_rows, reverse=True)

        # 从后往前删除行以避免行号变化
        for row_idx in delete_rows:
            temp_sheet.delete_rows(row_idx)

        # 保存修改
        temp_wb.save(new_filepath)
        temp_wb.close()

        output.append({"接收人": person, "文件名": new_filepath})

    return output
