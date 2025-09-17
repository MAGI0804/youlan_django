import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')

# 导入Django并初始化
import django
django.setup()

# 导入我们的导入函数
from finance.demo import import_all_xlsx_to_db


if __name__ == '__main__':
    # 设置要导入的文件夹路径
    folder_path = r"C:\Users\易理志\Desktop\贷款数据导出列表\贷款数据导出列表"
    
    print(f"开始导入文件夹 '{folder_path}' 中的所有Excel文件...")
    
    # 调用导入函数
    result = import_all_xlsx_to_db(folder_path)
    
    # 打印导入结果
    print(f"\n导入完成！")
    print(f"总导入记录数: {result['total_imported']}")
    
    if result['failed_files']:
        print("\n失败的文件:")
        for file_info in result['failed_files']:
            for file_path, error_msg in file_info.items():
                print(f"  - {file_path}: {error_msg}")
    else:
        print("所有文件都成功导入！")