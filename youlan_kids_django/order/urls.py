from django.urls import path
from . import views

urlpatterns = [
    path('add_order', views.add_order, name='add_order'),
    path('query_order_data', views.query_order_data, name='query_order_data'),
    path('change_receiving_data', views.change_receiving_data, name='change_receiving_data'),
    path('change_status', views.change_status, name='change_status'),
    path('orders_query', views.orders_query, name='orders_query'),
    path('batch_orders_query', views.batch_orders_query, name='batch_orders_query'),
    path('update_express_info', views.update_express_info, name='update_express_info'),
    path('sync_logistics_info', views.sync_logistics_info, name='sync_logistics_info'),
]
