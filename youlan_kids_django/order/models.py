from django.db import models
from users.models import User

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('canceled', '已取消'),
        ('processing','售后中')
    ]
    
    order_id = models.CharField(max_length=20, primary_key=True, verbose_name='订单ID')
    user_id = models.IntegerField(verbose_name='用户ID', default=0)
    receiver_name = models.CharField(max_length=100, verbose_name='收货人昵称')
    receiver_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='收货人电话')
    express_company = models.CharField(max_length=50, blank=True, null=True, verbose_name='快递公司')
    express_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='快递单号', help_text='支持字母和数字组合，如SF1234567890')
    logistics_process = models.TextField(blank=True, null=True, verbose_name='物流过程信息', help_text='存储物流跟踪信息，格式为JSON字符串：[{"time": "时间", "location": "位置", "description": "描述"}]')
    province = models.CharField(max_length=50, verbose_name='收货省')
    city = models.CharField(max_length=50, verbose_name='市')
    county = models.CharField(max_length=50, verbose_name='县')
    detailed_address = models.CharField(max_length=255, verbose_name='详细地址')
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单金额')
    product_list = models.TextField(verbose_name='商品列表')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    order_time = models.DateTimeField(auto_now_add=True, verbose_name='下单时间')
    remarks = models.TextField(blank=True, null=
     True, verbose_name='备注')

    class Meta:
        db_table = 'order_data'
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'
