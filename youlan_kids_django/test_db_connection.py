#!/usr/bin/env python3
import os
import sys
import django

# 设置Django设置模块
django_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_module)

# 加载Django设置
django.setup()

from django.db import connection

if __name__ == '__main__':
    print("正在测试数据库连接...")
    print(f"数据库配置：")
    print(f"  主机: {os.environ.get('DB_HOST', '未设置')}")
    print(f"  端口: {os.environ.get('DB_PORT', '未设置')}")
    print(f"  数据库名: {os.environ.get('DB_NAME', '未设置')}")
    print(f"  用户名: {os.environ.get('DB_USER', '未设置')}")
    
    try:
        # 尝试连接数据库
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("数据库连接成功!")
            print(f"测试结果: {result}")
            
            # 可选：查询数据库版本信息
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"数据库版本: {version[0]}")
            
        sys.exit(0)
    except Exception as e:
        print(f"数据库连接失败!")
        print(f"错误信息: {str(e)}")
        print("请检查以下事项:")
        print("1. .env文件中的数据库配置是否正确")
        print("2. 阿里云RDS实例是否允许您的IP地址访问")
        print("3. 数据库用户权限是否正确")
        print("4. 网络连接是否正常")
        sys.exit(1)