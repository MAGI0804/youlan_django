from django.core.management.base import BaseCommand
from commodity.models import Commodity, StyleCodeSituation
from django.utils import timezone

class Command(BaseCommand):
    help = '同步所有款式编码数据到StyleCodeSituation模型'

    def handle(self, *args, **options):
        # 获取所有去重后的款式编码
        unique_style_codes = Commodity.objects.values_list('style_code', flat=True).distinct().exclude(style_code='')
        
        # 计数器
        created_count = 0
        updated_count = 0
        
        # 遍历所有款式编码
        for style_code in unique_style_codes:
            # 计算该款式编码的商品数量
            style_code_count = Commodity.objects.filter(style_code=style_code).count()
            
            # 获取或创建StyleCodeSituation记录
            style_situation, created = StyleCodeSituation.objects.get_or_create(
                style_code=style_code,
                defaults={
                    'status': 'online',
                    'sync_data_count': style_code_count,
                    'online_time': timezone.now()
                }
            )
            
            # 如果记录已存在，更新同步数据量
            if not created:
                style_situation.sync_data_count = style_code_count
                style_situation.save()
                updated_count += 1
            else:
                created_count += 1
        
        # 输出同步结果
        self.stdout.write(self.style.SUCCESS(f'成功同步 {created_count} 个新款式编码和更新 {updated_count} 个已有款式编码'))