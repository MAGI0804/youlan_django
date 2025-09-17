from django.contrib import admin
from .models import Cart
from django.utils.html import format_html


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_cart_items_count', 'get_total_quantity', 'created_at', 'updated_at')
    search_fields = ('user__nickname', 'user__mobile')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
    ordering = ('-updated_at',)
    list_per_page = 20
    
    def get_cart_items_count(self, obj):
        """获取购物车中商品的种类数量"""
        return len(obj.cart_items)
    get_cart_items_count.short_description = '商品种类'
    
    def get_total_quantity(self, obj):
        """获取购物车中商品的总数量"""
        return obj.get_total_items()
    get_total_quantity.short_description = '商品总数'
    
    # 在详情页面优化购物车商品的显示
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # 可以在这里自定义表单字段的显示方式
        return form
        
    def cart_items_display(self, obj):
        """优化购物车商品在详情页的显示"""
        if not obj.cart_items:
            return "空购物车"
        
        items_html = []
        for code, details in obj.cart_items.items():
            items_html.append(f"<div>商品编码: {code}, 数量: {details.get('quantity', 1)}, 添加时间: {details.get('added_time', '未知')}</div>")
        
        return format_html('<br>'.join(items_html))
    cart_items_display.short_description = '购物车商品详情'
    cart_items_display.allow_tags = True

    # 添加详情页显示
    readonly_fields = ('cart_items_display',)