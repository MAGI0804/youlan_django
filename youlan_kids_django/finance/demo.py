import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')

# 导入Django并初始化
import django
django.setup()

from finance.models import DaikuanXlsxIndex


def import_all_xlsx_to_db(folder_path):
    """
    将指定文件夹下的所有xlsx文件（包括子文件夹中的）导入到DaikuanXlsxIndex模型中
    
    Args:
        folder_path: 要扫描的文件夹路径
    
    Returns:
        dict: 导入结果，包含成功数量和失败信息
    """
    # 字段映射：Excel中的中文列名到模型字段名
    field_mapping = {
        '账期': 'billing_period',
        '账单大类': 'billing_category',
        '业务大类': 'business_category',
        '业务小类': 'business_subcategory',
        '订单号': 'order_number',
        '子订单号': 'sub_order_number',
        '下单时间': 'order_time',
        '确认收货时间': 'delivery_time',
        '商品ID': 'product_id',
        'sku': 'sku',
        '商品名称': 'product_name',
        '数量': 'quantity',
        '单价（元）': 'unit_price',
        '订单实际金额（元）': 'actual_amount',
        '退款单号': 'refund_number',
        '退款金额（元）': 'refund_amount',
        '收/付渠道': 'payment_channel',
        '业务流水号': 'transaction_id',
        '商户订单号': 'merchant_order_number',
        '打款时间': 'payment_time',
        '打款更新时间': 'payment_update_time',
        '备注': 'remarks'
    }
    
    total_imported = 0
    failed_files = []
    
    # 遍历文件夹及其所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.xlsx'):
                file_path = os.path.join(root, file)
                try:
                    # 读取Excel文件
                    df = pd.read_excel(file_path)
                    
                    # 检查是否有必要的列
                    missing_columns = [col for col in field_mapping.keys() if col not in df.columns]
                    if missing_columns:
                        failed_files.append({file_path: f"缺少必要列: {', '.join(missing_columns)}"})
                        continue
                    
                    records_to_create = []
                    
                    # 处理每一行数据
                    for index, row in df.iterrows():
                        # 检查子订单号是否为空，为空则跳过
                        if pd.isna(row.get('子订单号')) or str(row.get('子订单号')).strip() == '':
                            # print(f"第{index+2}行数据：子订单号为空，跳过处理")
                            continue
                        
                        record_data = {}
                        
                        # 映射字段并处理数据类型
                        for excel_col, model_field in field_mapping.items():
                            value = row[excel_col]
                            
                            # 处理可能为空的情况
                            if pd.isna(value):
                                record_data[model_field] = None
                                continue
                            
                            # 处理需要清除空格并转换类型的字段
                            if excel_col == '数量':
                                # 清除空格并转换为整数
                                value_str = str(value).strip()
                                record_data[model_field] = int(float(value_str)) if value_str else 0
                            elif excel_col in ['单价（元）', '订单实际金额（元）', '退款金额（元）']:
                                # 清除空格并转换为Decimal
                                value_str = str(value).strip()
                                if value_str:
                                    try:
                                        record_data[model_field] = Decimal(value_str)
                                    except (ValueError, Decimal.InvalidOperation):
                                        record_data[model_field] = Decimal('0')
                                else:
                                    record_data[model_field] = Decimal('0')
                            elif excel_col in ['下单时间', '确认收货时间', '打款时间', '打款更新时间']:
                                # 处理日期时间类型
                                if isinstance(value, datetime):
                                    # 检查是否有时区信息，没有则添加
                                    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                                        record_data[model_field] = timezone.make_aware(value)
                                    else:
                                        record_data[model_field] = value
                                else:
                                    try:
                                        # 尝试转换字符串为日期时间
                                        dt = pd.to_datetime(value)
                                        # 检查是否有时区信息，没有则添加
                                        if isinstance(dt, datetime) and (dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None):
                                            record_data[model_field] = timezone.make_aware(dt)
                                        else:
                                            record_data[model_field] = dt
                                    except:
                                        record_data[model_field] = None
                            elif model_field == 'sku':
                                # sku字段可能为数字，需要转换为字符串
                                record_data[model_field] = str(value) if value else ''
                            else:
                                # 其他字段直接转换为字符串
                                record_data[model_field] = str(value)
                        
                        records_to_create.append(DaikuanXlsxIndex(**record_data))
                    
                    # 处理记录创建 - 允许重复子订单号的数据写入
                    created_count = 0
                    updated_count = 0
                    
                    # 每条记录单独处理，避免事务问题
                    for record in records_to_create:
                        try:
                            # 每条记录单独使用事务
                            with transaction.atomic():
                                # 不检查重复，直接保存
                                record.save()
                                created_count += 1
                        except Exception as e:
                            if 'Duplicate entry' in str(e):
                                # 遇到重复记录，根据订单实际金额决定是保留还是更新
                                try:
                                    # 查找已有记录
                                    existing_record = DaikuanXlsxIndex.objects.get(sub_order_number=record.sub_order_number)
                                    
                                    # 获取新记录和已有记录的订单实际金额
                                    new_actual_amount = getattr(record, 'actual_amount', Decimal('0'))
                                    existing_actual_amount = getattr(existing_record, 'actual_amount', Decimal('0'))
                                    
                                    # 如果新记录的订单实际金额不为0，或者新记录金额大于已有记录金额，则更新
                                    if new_actual_amount != Decimal('0') and new_actual_amount != existing_actual_amount:
                                        # 更新其他字段
                                        for field, value in record.__dict__.items():
                                            if field != 'id' and field != '_state' and field != 'sub_order_number':
                                                setattr(existing_record, field, value)
                                        existing_record.save()
                                        updated_count += 1
                                except DaikuanXlsxIndex.DoesNotExist:
                                    # 如果查找不到，说明是其他唯一性约束问题
                                    print(f"创建记录时出错: {str(e)}")
                            else:
                                # 其他错误，记录但继续处理
                                print(f"创建记录时出错: {str(e)}")
                    
                    if created_count > 0 or updated_count > 0:
                        total_imported += created_count + updated_count
                        result_msg = f"成功导入文件 {file_path} 中的 {created_count} 条新记录"
                        if updated_count > 0:
                            result_msg += f"，更新了 {updated_count} 条现有记录"
                        print(result_msg)
                    else:
                        print(f"文件 {file_path} 中没有记录被导入")
                        
                except Exception as e:
                    failed_files.append({file_path: str(e)})
                    print(f"导入文件 {file_path} 失败: {str(e)}")
    
    return {
        'total_imported': total_imported,
        'failed_files': failed_files
    }


if __name__ == '__main__':
    folder_path = r"C:\Users\易理志\Desktop\贷款数据导出列表\贷款数据导出列表"
    result = import_all_xlsx_to_db(folder_path)
    print(f"总导入记录数: {result['total_imported']}")
    if result['failed_files']:
        print("失败的文件:")
        for file_info in result['failed_files']:
            for file_path, error_msg in file_info.items():
                print(f"  - {file_path}: {error_msg}")