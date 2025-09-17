from django.urls import path
from . import views

urlpatterns = [
    path('add_service_user', views.add_service_user, name='add_service_user'),
    path('add_operation_user', views.add_operation_user, name='add_operation_user'),
    path('verification_status', views.verification_status, name='verification_status'),
    path('change_password', views.change_password, name='change_password'),
]
