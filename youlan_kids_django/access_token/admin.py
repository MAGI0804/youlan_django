from django.contrib import admin
from .models import AccessToken

@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'access_token', 'ip_address', 'register_time')
    search_fields = ('access_token', 'ip_address')
    list_filter = ('register_time',)
    readonly_fields = ('register_time',)
