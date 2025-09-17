import random
import string
from django.db import models

class CustomerServiceUser(models.Model):
    user_id = models.CharField(max_length=6, primary_key=True, unique=True)
    nickname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            while True:
                user_id = ''.join(random.choices(string.digits, k=6))
                if not CustomerServiceUser.objects.filter(user_id=user_id).exists() and not OperationUser.objects.filter(user_id=user_id).exists():
                    self.user_id = user_id
                    break
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'Customer_service_user'

class OperationUser(models.Model):
    user_id = models.CharField(max_length=6, primary_key=True, unique=True)
    nickname = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    level = models.IntegerField()
    
    def save(self, *args, **kwargs):
        if not self.user_id:
            while True:
                user_id = ''.join(random.choices(string.digits, k=6))
                if not CustomerServiceUser.objects.filter(user_id=user_id).exists() and not OperationUser.objects.filter(user_id=user_id).exists():
                    self.user_id = user_id
                    break
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'Operation_user'