from django.urls import path
from . import views

urlpatterns = [
    # 新增地址
    path('add_address', views.add_address, name='add_address'),
    # 删除地址
    path('delete_address', views.delete_address, name='delete_address'),
    # 更新地址
    path('update_address', views.update_address, name='update_address'),
    # 设置默认地址
    path('set_default_address', views.set_default_address, name='set_default_address'),
    # 查询地址列表
    path('get_addresses', views.get_addresses, name='get_addresses'),
    # 查询单个地址
    path('get_address_by_id', views.get_address_by_id, name='get_address_by_id'),
]