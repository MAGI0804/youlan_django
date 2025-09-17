from django.urls import path
from . import views

urlpatterns = [
    # path('add_data/', views.add_data, name='add_data'),
    path('add_data',views.user_registration,name='add_data'),
    path('find_data',views.user_query,name='find_data'),
    path('Modify_data', views.user_modify, name='modify_data'),
    path('get_user_id', views.user_get_id, name='get_user_id'),
    path('verification_status', views.verification_status, name='verification_status'),
    path('wechat_login', views.wechat_login, name='login'),

]
