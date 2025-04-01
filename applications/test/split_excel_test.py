from datetime import datetime

from applications.services.split_excel_service import split_excel_by_column

if __name__ == '__main__':
    # 示例用法
    start_time = datetime.now()
    result = split_excel_by_column("F:\新建文件夹\pear-admin-flask\custom_reports\添润库存数据-20250331_0855.xlsx", "运营体负责人")
    end_time = datetime.now()
    print("耗时：", end_time - start_time)
    print(result)