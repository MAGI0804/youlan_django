from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
import os
import hashlib
import time
from django.db.models import Count


def generate_unique_filename(instance, filename):
    """生成基于文件内容的唯一文件名，确保相同内容的文件只存储一次"""
    try:
        # 首先尝试直接读取文件内容（这是最可靠的方法）
        if hasattr(instance.image, 'file'):
            # 如果是内存中的文件，直接读取内容
            content = instance.image.file.read()
            file_hash = hashlib.md5(content).hexdigest()
            # 重置文件指针，以便后续操作
            instance.image.file.seek(0)
        elif hasattr(instance.image, 'path') and os.path.exists(instance.image.path):
            with open(instance.image.path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
        else:
            # 如果无法获取文件内容，检查是否有已知的文件路径
            # 这是为了处理tests.py中通过临时文件上传的情况
            if hasattr(instance, '_temp_image_path') and os.path.exists(instance._temp_image_path):
                with open(instance._temp_image_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
            else:
                # 最后的 fallback，使用原始文件名和时间戳
                file_hash = hashlib.md5(f"{filename}{time.time()}".encode()).hexdigest()
                print(f"警告：无法获取文件内容，使用时间戳生成哈希: {file_hash}")
            
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        # 使用哈希值作为文件名，保留扩展名
        return f'{file_hash}{ext.lower()}'
    except Exception as e:
        print(f"生成唯一文件名失败: {str(e)}")
        return filename

def commodity_image_path(instance, filename):
    # 使用款式编码创建文件夹
    if instance.style_code:
        # 确保文件夹名称安全
        safe_style_code = ''.join(c for c in instance.style_code if c.isalnum() or c in ['_', '-'])
        # 生成唯一文件名，确保相同内容的图片只存储一次
        unique_filename = generate_unique_filename(instance, filename)
        return f'commodities/{safe_style_code}/{unique_filename}'
    # 款式编码不存在时，使用临时文件夹
    return f'commodities/temp/{filename}'

def commodity_multiple_images_path(instance, filename):
    # 为多图片上传创建路径，使用款式编码
    if instance.commodity.style_code:
        # 确保文件夹名称安全
        safe_style_code = ''.join(c for c in instance.commodity.style_code if c.isalnum() or c in ['_', '-'])
        # 生成唯一文件名，确保相同内容的图片只存储一次
        unique_filename = generate_unique_filename(instance.commodity, filename)
        return f'commodities/{safe_style_code}/images/{unique_filename}'
    # 款式编码不存在时，使用临时文件夹
    return f'commodities/temp/images/{filename}'

def commodity_color_image_path(instance, filename):
    # 使用颜色创建文件夹
    if instance.color:
        # 确保文件夹名称安全
        safe_color = ''.join(c for c in instance.color if c.isalnum() or c in ['_', '-'])
        # 生成唯一文件名，确保相同内容的图片只存储一次
        unique_filename = generate_unique_filename(instance, filename)
        return f'commodities/colors/{safe_color}/{unique_filename}'
    # 颜色不存在时，使用临时文件夹
    return f'commodities/temp/colors/{filename}'

def commodity_promo_image_path(instance, filename):
    # 使用款式编码创建推广图文件夹
    if instance.style_code:
        # 确保文件夹名称安全
        safe_style_code = ''.join(c for c in instance.style_code if c.isalnum() or c in ['_', '-'])
        # 生成唯一文件名，确保相同内容的图片只存储一次
        unique_filename = generate_unique_filename(instance, filename)
        return f'commodities/{safe_style_code}/promo/{unique_filename}'
    # 款式编码不存在时，使用临时文件夹
    return f'commodities/temp/promo/{filename}'

class Commodity(models.Model):
    commodity_id = models.CharField(max_length=100, primary_key=True, verbose_name='商品ID')
    name = models.CharField(max_length=255, verbose_name='商品名称')
    style_code = models.CharField(max_length=50, blank=True, verbose_name='款式编码')
    category = models.CharField(max_length=100, verbose_name='商品类目')
    # 商品分类（更详细的分类）
    category_detail = models.CharField(max_length=100, blank=True, verbose_name='商品分类')
    price = models.FloatField(verbose_name='商品价格')
    image = models.ImageField(upload_to=commodity_image_path, verbose_name='商品主图')
    # 使用款式编码组织推广图
    promo_image = models.ImageField(upload_to=commodity_promo_image_path, blank=True, verbose_name='推广图')  # 对应style_code
    size = models.CharField(max_length=50, blank=True, verbose_name='商品尺码')
    # 颜色分类
    color = models.CharField(max_length=50, blank=True, verbose_name='颜色')
    # 身高范围
    height = models.CharField(max_length=50, blank=True, verbose_name='身高范围')
    # 规格编码
    spec_code = models.CharField(max_length=100, blank=True, verbose_name='规格编码')
    # 颜色对应图片，使用颜色组织
    color_image = models.ImageField(upload_to=commodity_color_image_path, blank=True, verbose_name='颜色对应图片')  # 对应color
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    notes = models.TextField(blank=True, verbose_name='备注')

    class Meta:
        db_table = 'Commodity_data'
        verbose_name = '商品数据'
        verbose_name_plural = '商品数据'


class CommodityImage(models.Model):
    commodity = models.ForeignKey(Commodity, related_name='images', on_delete=models.CASCADE, verbose_name='关联商品')
    image = models.ImageField(upload_to=commodity_multiple_images_path, verbose_name='商品图片')
    is_main = models.BooleanField(default=False, verbose_name='是否为主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        db_table = 'Commodity_Images'
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'


class CommoditySituation(models.Model):
    STATUS_CHOICES = [
        ('online', '上线'),
        ('offline', '下线'), 
        ('pending', '待上线'),
    ]

    # 修改为CharField以匹配Commodity模型的commodity_id字段
    commodity_id = models.CharField(max_length=100, primary_key=True, verbose_name='商品ID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='商品情况')
    # 不使用外键关联，而是通过commodity_id字段手动关联
    online_time = models.DateTimeField(auto_now_add=True, verbose_name='上线时间')
    offline_time = models.DateTimeField(auto_now_add=True, verbose_name='下架时间')
    sales_volume = models.PositiveIntegerField(default=0, verbose_name='销量')
    remarks = models.TextField(blank=True, verbose_name='备注')
    # 新增style_code字段，用于从Commodity模型同步
    style_code = models.CharField(max_length=50, blank=True, verbose_name='款式编码')

    class Meta:
        db_table = 'Commodity_Situation'
        verbose_name = '商品状态'
        verbose_name_plural = '商品状态'


class StyleCodeSituation(models.Model):
    STATUS_CHOICES = [
        ('online', '上线'),
        ('offline', '下线'), 
        ('pending', '待上线'),
    ]

    style_code = models.CharField(max_length=50, primary_key=True, verbose_name='款式编码')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='款式状态')
    online_time = models.DateTimeField(auto_now_add=True, verbose_name='上线时间')
    offline_time = models.DateTimeField(null=True, blank=True, verbose_name='下架时间')
    sync_data_count = models.PositiveIntegerField(default=0, verbose_name='同步数据量')

    class Meta:
        db_table = 'StyleCode_Situation'
        verbose_name = '款式状态'
        verbose_name_plural = '款式状态'

    def __str__(self):
        return f'{self.style_code} - {self.get_status_display()}'

# 信号处理函数：当Commodity模型添加记录时，自动创建对应的CommodityImage和CommoditySituation记录
@receiver(post_save, sender=Commodity)
def create_related_records(sender, instance, created, **kwargs):
    if created:
        # 自动创建CommoditySituation记录，默认状态为'待上线'
        CommoditySituation.objects.get_or_create(
            commodity_id=instance.commodity_id,
            defaults={
                'status': 'pending',
                'sales_volume': 0,
                'remarks': f'自动创建于{instance.created_at}',
                'style_code': instance.style_code  # 从Commodity模型同步style_code字段
            }
        )
        
        # 处理StyleCodeSituation记录：自动提取商品模型中的style_code并去重
        if instance.style_code:
            # 获取或创建StyleCodeSituation记录
            style_situation, created = StyleCodeSituation.objects.get_or_create(
                style_code=instance.style_code,
                defaults={
                    'status': 'online',  # 默认设置为上线状态
                    'sync_data_count': 1
                }
            )
            
            # 如果记录已存在，更新同步数据量
            if not created:
                # 计算该款式编码的商品数量
                style_code_count = Commodity.objects.filter(style_code=instance.style_code).count()
                # 更新同步数据量
                style_situation.sync_data_count = style_code_count
                style_situation.save()
        
        # 如果Commodity有主图，处理CommodityImage记录
        if hasattr(instance, 'image') and instance.image:
            # 实现基于style_code的图片重用逻辑：相同款式代码只保留一张图片
            if instance.style_code:
                safe_style_code = ''.join(c for c in instance.style_code if c.isalnum() or c in ['_', '-'])
                style_dir = os.path.join('commodities', safe_style_code)
                full_style_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', style_dir)
                
                # 检查是否已经存在该款式的图片记录
                existing_image_record = CommodityImage.objects.filter(
                    commodity__style_code=instance.style_code,
                    is_main=True
                ).first()
                
                if existing_image_record:
                    # 如果存在相同款式的图片记录，直接重用该图片
                    print(f"为商品 {instance.commodity_id} 重用了款式 {instance.style_code} 已有的图片")
                    CommodityImage.objects.create(
                        commodity=instance,
                        image=existing_image_record.image,
                        is_main=True
                    )
                    # 同时更新Commodity的image字段指向已存在的图片
                    instance.image = existing_image_record.image
                    instance.save(update_fields=['image'])
                else:
                    # 如果是该款式的第一个商品，创建新的图片记录
                    CommodityImage.objects.create(
                        commodity=instance,
                        image=instance.image,
                        is_main=True
                    )
                    print(f"为款式 {instance.style_code} 创建了第一张主图记录")
                    
                    # 确保文件夹内只有一张图片，清理可能存在的多余图片
                    if os.path.exists(full_style_dir):
                        files = [f for f in os.listdir(full_style_dir) if os.path.isfile(os.path.join(full_style_dir, f))]
                        if len(files) > 1:
                            # 保留第一张图片，删除其余图片
                            main_image_name = os.path.basename(instance.image.name)
                            for filename in files:
                                if filename != main_image_name:
                                    try:
                                        os.remove(os.path.join(full_style_dir, filename))
                                        print(f"清理款式 {instance.style_code} 文件夹中的多余图片: {filename}")
                                    except Exception as e:
                                        print(f"删除文件 {filename} 失败: {str(e)}")
            else:
                # 无款式代码时创建常规图片记录
                CommodityImage.objects.create(
                    commodity=instance,
                    image=instance.image,
                    is_main=True
                )
                print(f"为无款式代码的商品 {instance.commodity_id} 创建了主图记录")


