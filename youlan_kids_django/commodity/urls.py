from django.urls import path
from . import views

urlpatterns = [
    path('get_all_categories', views.get_all_categories, name='get_all_categories'),
    path('search_style_codes', views.search_style_codes, name='search_style_codes'),
    path('add_goods',views.add_goods),
    path('delete_goods',views.delete_goods),
    path('search_commodity_data', views.search_commodity_data, name='search_commodity_data'),
    path('goods_query', views.goods_query, name='goods_query'),
    path('change_commodity_data',views.change_commodity_data),
    path('change_commodity_status_online',views.change_commodity_status_online),
    path('change_commodity_status_offline',views.change_commodity_status_offline),
    path('get_commodity_status',views.get_commodity_status),
    path('search_products_by_name', views.search_products_by_name, name='search_products_by_name'),
    path('batch_get_products_by_ids', views.batch_get_products_by_ids, name='batch_get_products_by_ids'),
    # 新增style_code上下线路由
    path('style-code/status/online', views.change_style_code_status_online, name='change_style_code_status_online'),
    path('style-code/status/offline', views.change_style_code_status_offline, name='change_style_code_status_offline'),
    # 根据style_code查询具体商品
    path('style-code/commodities', views.get_commodities_by_style_code, name='get_commodities_by_style_code'),
]
