from django.db import models

class AccessToken(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='自增ID')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    access_token = models.CharField(max_length=100, unique=True, verbose_name='访问令牌')
    register_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        db_table = 'access_token'
        verbose_name = '访问令牌'
        verbose_name_plural = '访问令牌'

    def __str__(self):
        return f'{self.access_token} ({self.ip_address})'