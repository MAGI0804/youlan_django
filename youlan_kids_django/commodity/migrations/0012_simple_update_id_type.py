from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commodity', '0011_merge_20250915_1754'),
    ]

    operations = [
        # 使用Django的标准迁移操作来修改字段类型
        # 这将处理所有底层的数据库操作，包括处理外键关系
        migrations.AlterField(
            model_name='commodity',
            name='commodity_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='商品ID'),
            preserve_default=False,
        ),
        
        # 修改CommoditySituation表的commodity_id字段
        migrations.AlterField(
            model_name='commoditysituation',
            name='commodity_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='商品ID'),
            preserve_default=False,
        ),
        
        # 注意：CommodityImage模型的外键关系会由Django自动处理
        # 当Commodity.commodity_id类型更改时，Django会相应地更新外键类型
    ]