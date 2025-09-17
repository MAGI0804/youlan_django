from django.db import models
from users.models import User
from datetime import datetime


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True, verbose_name='购物车ID')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='用户')
    # 购物车字典，格式为{商品编码: {'quantity': 数量, 'added_time': 添加时间}}
    cart_items = models.JSONField(default=dict, verbose_name='购物车商品')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'cart_cart'
        verbose_name = '购物车'
        verbose_name_plural = '购物车信息'

    def __str__(self):
        return f'用户{self.user.nickname}的购物车'
        
    def add_item(self, commodity_code, quantity=1):
        """添加商品到购物车，支持指定数量"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if commodity_code in self.cart_items:
            # 商品已存在，增加数量
            self.cart_items[commodity_code]['quantity'] += quantity
            self.cart_items[commodity_code]['added_time'] = current_time
        else:
            # 商品不存在，添加新商品
            self.cart_items[commodity_code] = {
                'quantity': quantity,
                'added_time': current_time
            }
        
    def remove_item(self, commodity_code):
        """从购物车中移除指定商品"""
        if commodity_code in self.cart_items:
            del self.cart_items[commodity_code]
            return True
        return False
        
    def update_quantity(self, commodity_code, quantity):
        """更新购物车中商品的数量"""
        if commodity_code in self.cart_items and quantity > 0:
            self.cart_items[commodity_code]['quantity'] = quantity
            self.cart_items[commodity_code]['added_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return True
        return False
        
    def get_total_items(self):
        """获取购物车中商品的总数量"""
        return sum(item['quantity'] for item in self.cart_items.values())
        
    def get_item_quantity(self, commodity_code):
        """获取购物车中指定商品的数量"""
        if commodity_code in self.cart_items:
            return self.cart_items[commodity_code]['quantity']
        return 0