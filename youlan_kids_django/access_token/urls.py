from django.urls import path
from . import views

urlpatterns = [
    path('get_token', views.get_token, name='get_token'),
    path('get_ips', views.get_ips, name='get_ips'),
]
