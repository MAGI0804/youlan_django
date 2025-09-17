from django.db import models
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import re


class UserManager(BaseUserManager):
    def create_user(self, openid=None, mobile=None, nickname=None, password=None, **extra_fields):
        if not openid and not mobile:
            raise ValueError('必须提供openid或手机号')
        if mobile and not re.match(r'^1[3-9]\d{9}$', mobile):
            raise ValueError('手机号格式错误')
        if not nickname:
            nickname = f'微信用户_{openid[:8]}' if openid else f'手机用户_{mobile[-4:]}'

        user = self.model(
            openid=openid,
            mobile=mobile,
            nickname=nickname,
            **extra_fields
        )
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    openid = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='微信openid')
    user_img = models.ImageField(upload_to='user_avatars/', blank=True, null=True, verbose_name='用户头像')
    mobile = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^1[3-9]\d{9}$')],
        verbose_name='手机号'
    )
    nickname = models.CharField(max_length=100, blank=False, null=False, verbose_name='用户昵称')
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name='密码')
    default_receiver = models.CharField(max_length=100, blank=True, null=True, verbose_name='默认收货人昵称')
    province = models.CharField(max_length=50, blank=True, null=True, verbose_name='默认收货省')
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='市')
    county = models.CharField(max_length=50, blank=True, null=True, verbose_name='县')
    detailed_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='默认详细地址')
    membership_level = models.IntegerField(default=0, verbose_name='用户等级')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    total_spending = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='消费金额累计')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')

    # Django认证系统必需字段
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否为管理员')

    # 指定认证系统使用的字段
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    # 用户管理器
    objects = UserManager()

    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户信息'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def generate_tokens(self):
        # 使用PyJWT直接生成令牌
        now = datetime.utcnow()
        access_payload = {
            'exp': now + timedelta(minutes=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds() // 60),
            'iat': now,
            'sub': str(self.user_id),
            'user_id': str(self.user_id)
        }
        refresh_payload = {
            'exp': now + timedelta(days=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].days),
            'iat': now,
            'sub': str(self.user_id),
            'user_id': str(self.user_id)
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        return {
            'refresh': refresh_token,
            'access': access_token,
        }
