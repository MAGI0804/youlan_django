from django.db import models
from users.models import User

class Address(models.Model):
    """
    用户地址模型
    用于存储用户的收货地址信息
    """
    address_id = models.AutoField(primary_key=True, verbose_name='地址ID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='所属用户')
    province = models.CharField(max_length=50, verbose_name='省')
    city = models.CharField(max_length=50, verbose_name='市')
    county = models.CharField(max_length=50, verbose_name='县/区')
    detailed_address = models.CharField(max_length=255, verbose_name='详细地址')
    receiver_name = models.CharField(max_length=50, default='', verbose_name='收货人')
    phone_number = models.CharField(max_length=20, default='', verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认地址')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'addresses'
        verbose_name = '用户地址'
        verbose_name_plural = '用户地址管理'

    def __str__(self):
        return f'{self.user.nickname}的地址: {self.province}{self.city}{self.county}{self.detailed_address}'

    def save(self, *args, **kwargs):
        """
        重写save方法，确保一个用户只有一个默认地址
        如果当前地址被设置为默认地址，则将该用户的其他地址设置为非默认
        """
        if self.is_default:
            # 查询当前用户的其他默认地址
            Address.objects.filter(user=self.user, is_default=True).exclude(address_id=self.address_id).update(is_default=False)
        super().save(*args, **kwargs)
