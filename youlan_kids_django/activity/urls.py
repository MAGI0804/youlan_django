from django.urls import path
from . import views

urlpatterns = [
    path('add_activity_img', views.add_activity_img, name='add_activity_img'),
    path('update_activity_image_relations', views.update_activity_image_relations, name='update_activity_image_relations'),
    path('activity_image_online', views.activity_image_online, name='activity_image_online'),
    path('activity_image_offline', views.activity_image_offline, name='activity_image_offline'),
    path('batch_query_activity_images', views.batch_query_activity_images, name='batch_query_activity_images'),
]