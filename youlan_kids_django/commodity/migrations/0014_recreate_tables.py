from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commodity', '0013_fix_table_name'),
    ]

    operations = [
        # 第一步：删除现有的三个表
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS `Commodity_data`, `Commodity_Situation`, `Commodity_Images`;',
            reverse_sql='',
        ),
        
        # 第二步：重新创建Commodity_data表（字符串类型主键）
        migrations.RunSQL(
            sql="""
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
            );
            """,
            reverse_sql='',
        ),
        
        # 第三步：重新创建Commodity_Situation表（字符串类型主键）
        migrations.RunSQL(
            sql="""
            CREATE TABLE `Commodity_Situation` (
                `commodity_id` VARCHAR(100) NOT NULL PRIMARY KEY,
                `status` VARCHAR(20) NOT NULL,
                `online_time` DATETIME NOT NULL,
                `offline_time` DATETIME NOT NULL,
                `sales_volume` INT UNSIGNED NOT NULL DEFAULT 0,
                `remarks` LONGTEXT NULL
            );
            """,
            reverse_sql='',
        ),
        
        # 第四步：重新创建Commodity_Images表，并添加外键约束
        migrations.RunSQL(
            sql="""
            CREATE TABLE `Commodity_Images` (
                `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                `commodity_id` VARCHAR(100) NOT NULL,
                `image` VARCHAR(100) NOT NULL,
                `is_main` TINYINT(1) NOT NULL DEFAULT 0,
                `created_at` DATETIME NOT NULL,
                INDEX `commodity_id` (`commodity_id`),
                CONSTRAINT `Commodity_Images_commodity_id_fk` FOREIGN KEY (`commodity_id`) REFERENCES `Commodity_data` (`commodity_id`) ON DELETE CASCADE
            );
            """,
            reverse_sql='',
        ),
    ]