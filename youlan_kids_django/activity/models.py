from django.db import models

from django.db import models
from commodity.models import Commodity


def activity_image_path(instance, filename):
    # 根据活动ID创建文件夹存储图片
    if instance.id:
        return f'activities/{instance.id}/{filename}'
    # 活动ID不存在时，先使用临时文件夹
    return f'activities/temp/{filename}'


class ActivityImage(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='活动图ID')
    image = models.ImageField(upload_to=activity_image_path, verbose_name='活动图片')
    
    STATUS_CHOICES = [
        ('online', '上线'),
        ('offline', '下线'),
        ('pending', '待上线'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='上线情况')
    online_time = models.DateTimeField(null=True, blank=True, verbose_name='上线时间')
    offline_time = models.DateTimeField(null=True, blank=True, verbose_name='下线时间')
    
    # 多对多关系，一个活动可以涉及多个商品
    commodities = models.TextField(verbose_name='涉及商品编号', help_text='多个商品编号用逗号分隔', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, verbose_name='涉及类目')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'Activity_Image'
        verbose_name = '活动图'
        verbose_name_plural = '活动图'
