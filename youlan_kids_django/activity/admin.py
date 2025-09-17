from django.contrib import admin

from django.contrib import admin
from .models import ActivityImage

@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'online_time', 'offline_time', 'category', 'get_commodities', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('category', 'notes')
    date_hierarchy = 'created_at'
    
    def get_commodities(self, obj):
        # 直接返回存储的商品编号
        return obj.commodities
    get_commodities.short_description = '涉及商品编号'
