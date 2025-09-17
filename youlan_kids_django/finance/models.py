from django.db import models

from django.db import models


class DaikuanXlsxIndex(models.Model):
    # 自动添加的index（自增主键）
    id = models.AutoField(primary_key=True, verbose_name='索引ID')
    
    # 账期
    billing_period = models.CharField(max_length=20, verbose_name='账期')
    # 账单大类
    billing_category = models.CharField(max_length=50, verbose_name='账单大类')
    # 业务大类
    business_category = models.CharField(max_length=50, verbose_name='业务大类')
    # 业务小类
    business_subcategory = models.CharField(max_length=50, verbose_name='业务小类')
    # 订单号
    order_number = models.CharField(max_length=100, verbose_name='订单号')
    # 子订单号（作为主键）
    sub_order_number = models.CharField(max_length=100, unique=False, verbose_name='子订单号')
    # 下单时间
    order_time = models.DateTimeField(blank=True, null=True, verbose_name='下单时间')
    # 确认收货时间
    delivery_time = models.DateTimeField(blank=True, null=True, verbose_name='确认收货时间')
    # 商品ID
    product_id = models.CharField(max_length=50, verbose_name='商品ID')
    # sku
    sku = models.CharField(max_length=100, blank=True, null=True, verbose_name='sku')
    # 商品名称
    product_name = models.CharField(max_length=255, verbose_name='商品名称')
    # 数量
    quantity = models.IntegerField(verbose_name='数量')
    # 单价（元）
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价（元）')
    # 订单实际金额（元）
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单实际金额（元）')
    # 退款单号
    refund_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='退款单号')
    # 退款金额（元）
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='退款金额（元）')
    # 收/付渠道
    payment_channel = models.CharField(max_length=50, blank=True, null=True, verbose_name='收/付渠道')
    # 业务流水号
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='业务流水号')
    # 商户订单号
    merchant_order_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='商户订单号')
    # 打款时间
    payment_time = models.DateTimeField(blank=True, null=True, verbose_name='打款时间')
    # 打款更新时间
    payment_update_time = models.DateTimeField(blank=True, null=True, verbose_name='打款更新时间')
    # 备注
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'daikuan_xlsx_index'
        verbose_name = '贷款Excel索引'
        verbose_name_plural = '贷款Excel索引管理'
