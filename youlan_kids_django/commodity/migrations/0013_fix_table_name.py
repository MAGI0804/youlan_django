from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commodity', '0012_simple_update_id_type'),
    ]

    operations = [
        # 使用AlterModelTable明确告诉Django正确的表名
        migrations.AlterModelTable(
            name='commoditysituation',
            table='Commodity_Situation',
        ),
        migrations.AlterModelTable(
            name='commodity',
            table='Commodity_data',
        ),
        migrations.AlterModelTable(
            name='commodityimage',
            table='Commodity_Images',
        ),
    ]