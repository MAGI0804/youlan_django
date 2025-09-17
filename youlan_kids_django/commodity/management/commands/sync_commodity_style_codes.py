from django.core.management.base import BaseCommand
from commodity.models import Commodity, CommoditySituation
import logging

logger = logging.getLogger('django')

class Command(BaseCommand):
    help = '将商品的style_code同步到CommoditySituation记录中'

    def handle(self, *args, **options):
        try:
            # 获取所有商品记录
            commodities = Commodity.objects.all()
            total_commodities = commodities.count()
            updated_count = 0
            
            self.stdout.write(f'开始同步 {total_commodities} 个商品的style_code到CommoditySituation...')
            
            for commodity in commodities:
                try:
                    # 查找对应的CommoditySituation记录
                    situation = CommoditySituation.objects.get(commodity_id=commodity.commodity_id)
                    
                    # 如果style_code不一致，则更新
                    if situation.style_code != commodity.style_code:
                        situation.style_code = commodity.style_code
                        situation.save()
                        updated_count += 1
                        
                        if updated_count % 100 == 0:
                            self.stdout.write(f'已同步 {updated_count} 条记录...')
                except CommoditySituation.DoesNotExist:
                    # 如果没有对应的CommoditySituation记录，创建一个
                    CommoditySituation.objects.create(
                        commodity_id=commodity.commodity_id,
                        style_code=commodity.style_code,
                        status='pending'
                    )
                    updated_count += 1
                except Exception as e:
                    logger.error(f'同步商品 {commodity.commodity_id} 的style_code失败: {str(e)}')
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'成功同步 {updated_count} 条记录'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'同步失败: {str(e)}'))
            logger.error(f'sync_commodity_style_codes命令执行失败: {str(e)}', exc_info=True)