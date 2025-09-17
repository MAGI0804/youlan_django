from django.urls import path
from . import views

# 购物车API路由
urlpatterns = [
    # 添加商品到购物车
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    
    # 批量删除购物车商品
    path('batch_delete_from_cart', views.batch_delete_from_cart, name='batch_delete_from_cart'),
    
    # 查询购物车所有商品
    path('query_cart_items', views.query_cart_items, name='query_cart_items'),
    
    # 更新购物车商品数量
    path('update_cart_item_quantity', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    
    # 购物车商品数量加1
    path('increase_cart_item_quantity', views.increase_cart_item_quantity, name='increase_cart_item_quantity'),
    
    # 购物车商品数量减1（不能减到0）
    path('decrease_cart_item_quantity', views.decrease_cart_item_quantity, name='decrease_cart_item_quantity'),
    
    # 清空购物车
    path('clear_cart', views.clear_cart, name='clear_cart'),
]