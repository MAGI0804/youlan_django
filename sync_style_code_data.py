#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同步商品数据到StyleCodeData模型
此脚本将遍历所有商品，为每个唯一的款式编码创建或更新StyleCodeData记录
"""
import os
import sys
import django
import logging
from datetime import datetime

# 获取当前脚本目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 设置Django项目路径
django_project_path = os.path.join(current_dir, 'youlan_kids_django')

# 将Django项目路径添加到Python路径
sys.path.append(django_project_path)

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')

# 初始化Django
django.setup()

# 导入Django模型
from commodity.models import Commodity, StyleCodeData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync_style_code_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def sync_style_code_data():
    """同步商品数据到StyleCodeData模型"""
    logger.info(f"开始同步商品数据到StyleCodeData模型 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 获取所有唯一的款式编码
        style_codes = Commodity.objects.values_list('style_code', flat=True).distinct()
        total_style_codes = style_codes.count()
        logger.info(f"找到 {total_style_codes} 个唯一的款式编码")
        
        # 跟踪处理结果
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 遍历每个款式编码
        for index, style_code in enumerate(style_codes, 1):
            if not style_code:
                skipped_count += 1
                continue
            
            # 获取该款式编码的第一个商品作为基准数据
            base_commodity = Commodity.objects.filter(style_code=style_code).first()
            if not base_commodity:
                logger.warning(f"款式编码 '{style_code}' 没有对应的商品数据，跳过")
                skipped_count += 1
                continue
            
            # 获取或创建StyleCodeData记录
            style_data, created = StyleCodeData.objects.get_or_create(
                style_code=style_code,
                defaults={
                    'name': base_commodity.name,
                    'image': base_commodity.image,
                    'category': base_commodity.category,
                    'category_detail': base_commodity.category_detail,
                    'price': base_commodity.price
                }
            )
            
            # 如果记录已存在，可以选择是否更新
            # 这里我们选择更新，确保数据最新
            if not created:
                # 检查是否有需要更新的字段
                needs_update = False
                if style_data.name != base_commodity.name:
                    style_data.name = base_commodity.name
                    needs_update = True
                if style_data.category != base_commodity.category:
                    style_data.category = base_commodity.category
                    needs_update = True
                if style_data.category_detail != base_commodity.category_detail:
                    style_data.category_detail = base_commodity.category_detail
                    needs_update = True
                if style_data.price != base_commodity.price:
                    style_data.price = base_commodity.price
                    needs_update = True
                # 只有当有新图片时才更新图片字段
                if base_commodity.image and not style_data.image:
                    style_data.image = base_commodity.image
                    needs_update = True
                
                # 如果需要更新，则保存
                if needs_update:
                    style_data.save()
                    updated_count += 1
                    logger.debug(f"[{index}/{total_style_codes}] 更新款式数据: {style_code}")
                else:
                    skipped_count += 1
            else:
                created_count += 1
                logger.debug(f"[{index}/{total_style_codes}] 创建款式数据: {style_code}")
            
            # 每处理100个记录打印一次进度
            if index % 100 == 0 or index == total_style_codes:
                logger.info(f"处理进度: {index}/{total_style_codes} ({index/total_style_codes*100:.1f}%)")
        
        # 输出最终统计结果
        logger.info(f"同步完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"创建记录: {created_count}")
        logger.info(f"更新记录: {updated_count}")
        logger.info(f"跳过记录: {skipped_count}")
        logger.info(f"总处理款式编码: {created_count + updated_count + skipped_count}")
        
        return {
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total': created_count + updated_count + skipped_count
        }
        
    except Exception as e:
        logger.error(f"同步过程中发生错误: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    print("=== 商品数据同步工具 ===")
    print("此工具将同步所有商品的款式数据到StyleCodeData模型")
    print("开始同步...")
    
    result = sync_style_code_data()
    
    if result['success']:
        print(f"\n同步成功!")
        print(f"创建记录: {result['created']}")
        print(f"更新记录: {result['updated']}")
        print(f"跳过记录: {result['skipped']}")
        print(f"总处理款式编码: {result['total']}")
        print("\n请运行以下命令执行数据库迁移：")
        print("docker exec -it youlan_kids_django_web_1 python manage.py migrate")
    else:
        print(f"\n同步失败!")
        print(f"错误信息: {result['error']}")