from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '删除并重新创建商品相关的三个表，设置正确的字段类型'

    def handle(self, *args, **options):
        # 定义需要执行的SQL语句
        sql_statements = [
            # 直接删除三个表（如果存在）
            'DROP TABLE IF EXISTS `Commodity_Images`;',
            'DROP TABLE IF EXISTS `Commodity_Situation`;',
            'DROP TABLE IF EXISTS `Commodity_data`;',
            
            # 重新创建Commodity_data表（字符串类型主键）
            '''
            CREATE TABLE `Commodity_data` (
                `commodity_id` VARCHAR(100) NOT NULL PRIMARY KEY,
                `name` VARCHAR(255) NOT NULL,
                `style_code` VARCHAR(50) NULL,
                `category` VARCHAR(100) NOT NULL,
                `category_detail` VARCHAR(100) NULL,
                `price` DOUBLE NOT NULL,
                `image` VARCHAR(100) NOT NULL,
                `promo_image` VARCHAR(100) NULL,
                `size` VARCHAR(50) NULL,
                `color` VARCHAR(50) NULL,
                `height` VARCHAR(50) NULL,
                `spec_code` VARCHAR(100) NULL,
                `color_image` VARCHAR(100) NULL,
                `created_at` DATETIME NOT NULL,
                `notes` LONGTEXT NULL
            )
            ''',
            
            # 重新创建Commodity_Situation表（字符串类型主键）
            '''
            CREATE TABLE `Commodity_Situation` (
                `commodity_id` VARCHAR(100) NOT NULL PRIMARY KEY,
                `status` VARCHAR(20) NOT NULL,
                `online_time` DATETIME NOT NULL,
                `offline_time` DATETIME NOT NULL,
                `sales_volume` INT UNSIGNED NOT NULL DEFAULT 0,
                `remarks` LONGTEXT NULL
            )
            ''',
            
            # 重新创建Commodity_Images表，并添加外键约束
            '''
            CREATE TABLE `Commodity_Images` (
                `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `commodity_id` VARCHAR(100) NOT NULL,
                `image` VARCHAR(100) NOT NULL,
                `is_main` TINYINT(1) NOT NULL DEFAULT 0,
                `created_at` DATETIME NOT NULL,
                INDEX `commodity_id` (`commodity_id`),
                CONSTRAINT `Commodity_Images_commodity_id_fk` FOREIGN KEY (`commodity_id`) REFERENCES `Commodity_data` (`commodity_id`) ON DELETE CASCADE
            )
            '''
        ]
        
        # 执行SQL语句
        with connection.cursor() as cursor:
            for sql in sql_statements:
                try:
                    self.stdout.write(f'执行SQL: {sql[:50]}...')
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(' 成功'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f' 失败: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n表删除并重新创建完成！'))