from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('ordinary_user/', include('users.urls')),
    path('commodity/', include('commodity.urls')),
    path('order/', include('order.urls')),
    path('access_token/', include('access_token.urls')),
    path('OperationUser/', include('OperationUser.urls')),
    path('activity/', include('activity.urls')),
    path('address/', include('address.urls')),
    path('cart/', include('cart.urls')),

]

handler404 = 'users.views.custom_404_view'

# 为静态文件添加URL配置（不限于DEBUG模式）
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 为媒体文件添加URL配置（不限于DEBUG模式）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)