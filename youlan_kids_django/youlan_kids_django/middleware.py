from django.http import HttpResponse, JsonResponse
from django.db import DatabaseError
from django.conf import settings
from access_token.models import AccessToken
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class PathValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    # def __call__(self, request):
    #     if 'ordinary_user' in request.path:
    #         logger.warning(f'废弃路径访问: {request.path}')
    #         return JsonResponse({'error': '请使用新版API路径'}, status=410)
    #     return self.get_response(request)


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            # CORS预检请求配置
            ALLOWED_METHODS = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            ALLOWED_HEADERS = 'Content-Type, Authorization'
            MAX_AGE = 86400  # 24小时缓存

            # 统一响应头设置
            origin = request.META.get('HTTP_ORIGIN')
            
            # 统一日志记录器初始化
            # import logging
            # logger = logging.getLogger('cors')
            
            # 优先验证origin合法性
            if not origin:
                logger.warning('缺失Origin头')
                return HttpResponse(status=400, content='Missing Origin header')
            
            # 增强配置校验
            if not hasattr(settings, 'CORS_ALLOWED_ORIGINS') or not isinstance(settings.CORS_ALLOWED_ORIGINS, list):
                logger.critical('CORS配置错误：CORS_ALLOWED_ORIGINS必须为列表类型')
                return HttpResponse(
                    status=500,
                    content='Invalid CORS configuration: ALLOWED_ORIGINS required',
                    headers={'Content-Type': 'text/plain'}
                )
            
            import logging  # 统一模块导入
            logger = logging.getLogger('cors')
            allowed_origins = settings.CORS_ALLOWED_ORIGINS
            
            if origin not in allowed_origins:
                logger.error(f'非法origin: {origin}，允许列表: {allowed_origins}')
                return HttpResponse(status=403, content='Origin not allowed')
            
            # 构建预检响应头
            response = HttpResponse(
                content_type='text/plain',
                status=204,
                headers={
                    'Access-Control-Allow-Origin': origin,
                    'Access-Control-Allow-Methods': ALLOWED_METHODS,
                    'Access-Control-Allow-Headers': ALLOWED_HEADERS,
                    'Access-Control-Max-Age': str(MAX_AGE),
                    'Content-Length': '0'
                }
            )
            return response
            
            # 凭证模式处理
            if settings.CORS_ALLOW_CREDENTIALS or 'HTTP_AUTHORIZATION' in request.META:
                response['Access-Control-Allow-Credentials'] = 'true'
                # return HttpResponse(
                #         status=403,
                #         content='CORS configuration conflict: Credentials not allowed with wildcard origin',
                #         headers={'Content-Type': 'text/plain'}
                #     )

            # 统一日志记录器初始化
        
        # logger = logging.getLogger('cors')
        #     # 增强调试信息
        # logger.debug(
        #         'CORS处理详情:\n'
        #         f'请求方法: {request.method}\n'
        #         f'请求路径: {request.path}\n'
        #         f'Origin头: {origin}\n'
        #         f'设置头信息: {dict(response.items())}'
        #     )
        # return response
        
        response = self.get_response(request)
        origin = request.META.get('HTTP_ORIGIN', '')
        
        is_preflight = request.method == 'OPTIONS'
        # 统一凭证处理逻辑（与预检请求保持一致）
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            # 增强origin格式校验
            if not origin.startswith(('http://', 'https://')):
                logger.warning(f'非法origin格式: {origin}')
                return HttpResponse(status=400, content='Invalid origin protocol')
            # 同步预检请求的origin校验逻辑
            if settings.CORS_ALLOW_CREDENTIALS:
                if origin not in settings.CORS_ALLOWED_ORIGINS:
                    logger.error(f'非法origin: {origin}')
                    return HttpResponse(status=403, content='Origin not allowed')
            
            # 同步预检请求的凭证判断逻辑
            if settings.CORS_ALLOW_CREDENTIALS or 'HTTP_AUTHORIZATION' in request.META:
                response['Access-Control-Allow-Credentials'] = 'true'
                
                # 安全规范检查
                if origin == '*' and settings.CORS_ALLOW_CREDENTIALS:
                    logger.error('CORS安全违规：凭证模式使用通配符origin')
                    return HttpResponse(
                        status=403,
                        content='Invalid CORS policy: Credentials require specific origin',
                        headers={'Content-Type': 'text/plain'}
                    )
                
                if origin == '*' and settings.CORS_ALLOW_CREDENTIALS:
                    logger.warning('检测到危险配置：凭证模式不允许使用通配符origin')
                    return HttpResponse(status=403, content='Invalid CORS configuration')

            if is_preflight:
                response['Access-Control-Allow-Methods'] = ', '.join(settings.CORS_ALLOW_METHODS)
                response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOW_HEADERS)
                response['Access-Control-Max-Age'] = str(settings.CORS_MAX_AGE)
                return response
        else:
            response['Access-Control-Allow-Origin'] = ', '.join(settings.CORS_ALLOWED_ORIGINS)
        
        return response

class AccessTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/access_token/get_token',
            '/access_token/get_ips'
        ]

    def __call__(self, request):
        # 检查是否为豁免路径
        for path in self.exempt_paths:
            if request.path.startswith(path):
                return self.get_response(request)
        
        # 从GET或POST参数中获取access_token
        access_token = request.GET.get('access_token') or request.POST.get('access_token')

        # 验证token是否存在且有效
        if not access_token:
            return JsonResponse({
                'code': 401,
                'message': 'Missing access token'
            }, status=401)

        try:
            # 尝试从缓存获取token信息
            cache_key = f'token_{access_token}'
            cached_token = cache.get(cache_key)
            
            if cached_token:
                token_ip = cached_token
            else:
                # 从数据库查询有效的token
                token_obj = AccessToken.objects.get(access_token=access_token)
                token_ip = token_obj.ip_address
                # 将token信息存入缓存，过期时间设为10分钟
                cache.set(cache_key, token_ip, 600)
            
            # 获取请求IP地址（支持代理）
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR', '')
            
            # 验证IP是否与token绑定
            if token_ip != ip_address:
                logger.warning(f'IP验证失败: token绑定IP={token_ip}, 请求IP={ip_address}')
                # 清除缓存中的无效token
                cache.delete(cache_key)
                return JsonResponse({
                    'code': 401,
                    'message': 'IP address does not match token'
                }, status=401)
                
        except AccessToken.DoesNotExist:
            logger.warning(f'无效的access_token: {access_token}')
            return JsonResponse({
                'code': 401,
                'message': 'Invalid access token'
            }, status=401)
        except DatabaseError as e:
            logger.error(f'数据库错误: {str(e)}')
            return JsonResponse({
                'code': 500,
                'message': 'Database error occurred'
            }, status=500)
        except Exception as e:
            logger.error(f'中间件处理异常: {str(e)}', exc_info=True)
            return JsonResponse({
                'code': 500,
                'message': 'Middleware processing error'
            }, status=500)

        return self.get_response(request)