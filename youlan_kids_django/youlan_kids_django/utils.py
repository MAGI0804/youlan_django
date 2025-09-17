from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from rest_framework.renderers import JSONRenderer

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # 转换为本地时区（Asia/Shanghai）
            local_time = timezone.localtime(obj)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

class CustomJSONRenderer(JSONRenderer):
    encoder_class = CustomJSONEncoder