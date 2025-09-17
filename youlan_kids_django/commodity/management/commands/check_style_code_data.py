from django.core.management.base import BaseCommand
from commodity.models import StyleCodeSituation, CommoditySituation

class Command(BaseCommand):
    help = '检查StyleCodeSituation和CommoditySituation表中的数据情况'

    def handle(self, *args, **options):
        # 检查StyleCodeSituation表中的数据
        style_codes = StyleCodeSituation.objects.all()
        self.stdout.write(f'StyleCodeSituation表共有 {style_codes.count()} 条记录')
        
        # 显示前5条款式编码记录
        self.stdout.write('\n前5条款式编码记录：')
        for i, style in enumerate(style_codes[:5]):
            self.stdout.write(f'{i+1}. 款式编码: {style.style_code}, 状态: {style.get_status_display()}')
        
        # 检查CommoditySituation表中style_code字段的数据
        situations_with_style = CommoditySituation.objects.exclude(style_code='').count()
        total_situations = CommoditySituation.objects.count()
        
        self.stdout.write(f'\nCommoditySituation表共有 {total_situations} 条记录')
        self.stdout.write(f'其中包含款式编码的记录: {situations_with_style} 条')
        
        # 显示前5条有style_code的CommoditySituation记录
        self.stdout.write('\n前5条有款式编码的商品状态记录：')
        for i, situation in enumerate(CommoditySituation.objects.exclude(style_code='')[:5]):
            self.stdout.write(f'{i+1}. 商品ID: {situation.commodity_id}, 款式编码: {situation.style_code}, 状态: {situation.get_status_display()}')