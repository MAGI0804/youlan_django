
from django.utils import timezone
from django.http import JsonResponse
from .models import AccessToken
import secrets
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import JsonResponse
import logging
import json
# 初始化审计日志
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('audit')


@csrf_exempt
def get_token(request):
    # 获取客户端IP地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')

    # 检查该IP是否已存在token
    try:
        token_obj = AccessToken.objects.get(ip_address=ip_address)
        return JsonResponse({
            'code': 200,
            'message': 'Token already exists for this IP',
            'access_token': token_obj.access_token
        })
    except AccessToken.DoesNotExist:
        # 生成32位随机不重复token
        while True:
            access_token = secrets.token_hex(16)  # 生成32位十六进制字符串
            if not AccessToken.objects.filter(access_token=access_token).exists():
                break

        # 创建新token记录
        try:
            token_obj = AccessToken.objects.create(
                ip_address=ip_address,
                access_token=access_token,
                register_time=timezone.now()
            )
            return JsonResponse({
                'code': 201,
                'message': 'Token generated successfully',
                'access_token': token_obj.access_token
            }, status=201)
        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'Database error: {str(e)}'
            }, status=500)


@csrf_exempt
def get_ips(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'message': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        # 验证shopname参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({'code': 403, 'message': 'Invalid shopname'}, status=403)
        
        # 获取所有唯一IP地址
        ip_addresses = AccessToken.objects.values_list('ip_address', flat=True).distinct()
        
        return JsonResponse({
            'code': 200,
            'message': 'IP addresses retrieved successfully',
            'ip_addresses': list(ip_addresses)
        })
    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'code': 500, 'message': f'Server error: {str(e)}'}, status=500)

