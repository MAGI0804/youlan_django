import re
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime
import os
from django.conf import settings
from django.core.files import File
from io import BytesIO

from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError, transaction
from django.urls import reverse

# 微信小程序配置
WECHAT_APP_ID = 'wxd5dcc7357bf532b1'
WECHAT_APP_SECRET = '86f3dbc4bf0c70f14edce6024fa38d08'
WECHAT_LOGIN_URL = 'https://api.weixin.qq.com/sns/jscode2session'

logger = logging.getLogger(__name__)

@csrf_exempt
def user_registration(request):
    required_headers = ['HTTP_X_PHONE', 'HTTP_X_NICKNAME', 'HTTP_X_PASSWORD']
    try:
        if not all(request.META.get(h) for h in required_headers):
            return JsonResponse({'error': '缺少必要请求头'}, status=400)
        
        if not re.match(r'^1[3-9]\d{9}$', request.META['HTTP_X_PHONE']):
            return JsonResponse({'error': '手机号格式错误'}, status=422)
            
        with transaction.atomic():
            user = User.objects.create(
                mobile=request.META['HTTP_X_PHONE'],
                nickname=request.META['HTTP_X_NICKNAME'],
                password=make_password(request.META['HTTP_X_PASSWORD'])
            )
            return JsonResponse({
                'user_id': user.user_id,
                'registration_time': user.registration_date.strftime('%Y-%m-%d %H:%M:%S')
            }, status=201)
    except IntegrityError:
        return JsonResponse({'error': '手机号已被注册'}, status=409)
    except KeyError as e:
        logger.error(f'Missing header: {e}')
        return JsonResponse({'error': '请求头不完整'}, status=400)
    except Exception as e:
        logger.exception('服务器内部错误')
        return JsonResponse({'error': '服务器内部错误'}, status=500)


# Create your views here.


@require_http_methods(["GET", "POST"])
@csrf_exempt
@transaction.atomic
def add_data(request):
    expected_path = reverse('add_data')
    if request.path != expected_path:
        logger.error(f'路径不匹配: 预期{expected_path} 实际{request.path}')
        return JsonResponse({'error': '非标准访问路径'}, status=400)
    logger.debug(f'收到请求头: {dict(request.headers)}')
    try:
        request_body = request.body.decode('utf-8')
        logger.debug(f'原始请求体: {request_body}')
        data = json.loads(request_body)
    except UnicodeDecodeError as e:
        logger.error(f'解码错误: {str(e)}')
        return JsonResponse({'error': '字符编码错误'}, status=400)
        
        # 强制字段验证
        if not all(key in data for key in ['field1', 'field2']):
            return JsonResponse({'error': '缺少必要字段'}, status=400)
            
        # 数据库事务操作
        new_record = DataModel.objects.create(**data)
        
    except json.JSONDecodeError:
        logger.error('无效的JSON格式')
        return JsonResponse({'error': '无效的请求体格式'}, status=400)
    
    except IntegrityError as e:
        logger.error(f'数据唯一性冲突: {str(e)}')
        return JsonResponse({'error': '数据已存在'}, status=409)
    except KeyError as e:
        logger.warning(f'缺少必要字段: {str(e)}')
        return JsonResponse({'error': f'缺少字段: {str(e)}'}, status=400)
    except json.JSONDecodeError:
        logger.error('无效的JSON格式')
        return JsonResponse({'error': '无效的请求体格式'}, status=400)
    except Exception as e:
        logger.exception('添加数据时发生未预期错误')
        return JsonResponse({'error': '服务器处理请求失败'}, status=500)
    return HttpResponse("数据添加页面测试成功！")


def custom_404_view(request, exception):
    return HttpResponseNotFound('自定义404页面')


@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def user_query(request):
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'error': '缺少必要参数'}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)

        data = {}
        for field in User._meta.fields:
            if field.name in ['created_at', 'updated_at']:
                continue
            try:
                value = getattr(user, field.name)
                
                if value is None:
                    data[field.name] = None
                    continue
                     
                # 特殊处理头像字段，返回完整URL
                if field.name == 'user_img' and value:
                    # 获取头像的完整URL
                    avatar_url = request.build_absolute_uri(value.url)
                    data[field.name] = avatar_url
                elif isinstance(value, datetime):
                    data[field.name] = value.astimezone().isoformat() if value else None
                elif value is None:
                    data[field.name] = None
                elif isinstance(value, (int, float, str, bool)):
                    data[field.name] = value
                else:
                    try:
                        data[field.name] = str(value)
                    except Exception as e:
                        data[field.name] = None
                    
            except Exception as e:
                logger.error(f'字段序列化异常 | 字段:{field.name} | 类型:{type(value)} | 错误:{str(e)}')
                data[field.name] = 'N/A'
                
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f'用户查询异常: {str(e)}')
        return JsonResponse({'error': '服务器处理请求失败'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def user_modify(request):   #修改信息   
    try:
        # 处理multipart/form-data请求
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 从表单中获取user_id
            user_id = request.POST.get('user_id')
            if not user_id:
                return JsonResponse({'error': '缺少user_id参数'}, status=400)
            
            try:
                user_id = int(user_id)
            except ValueError:
                return JsonResponse({'error': 'user_id格式错误'}, status=400)
            
            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'error': '用户不存在'}, status=404)
            
            # 处理普通字段更新
            for field in request.POST:
                if field != 'user_id' and field != 'mobile' and hasattr(user, field):
                    setattr(user, field, request.POST[field])
            
            # 处理头像上传
            if 'user_img' in request.FILES:
                # 确保media/user_avatars目录存在
                import os
                avatar_dir = os.path.join(settings.MEDIA_ROOT, 'user_avatars')
                if not os.path.exists(avatar_dir):
                    os.makedirs(avatar_dir)
                
                # 保存新头像
                user.user_img = request.FILES['user_img']
            
            user.save()
            
            # 构建并返回完整的头像URL
            response_data = {
                'message': '用户信息更新成功'
            }
            
            if user.user_img:
                # 获取头像的完整URL
                avatar_url = request.build_absolute_uri(user.user_img.url)
                response_data['avatar_url'] = avatar_url
            
            return JsonResponse(response_data, status=200)
        
        # 处理普通JSON请求
        else:
            try:
                modify_data = json.loads(request.body.decode('utf-8'))
                try:
                    user_id = modify_data['user_id']
                    if user_id != int(user_id):
                        return JsonResponse({'error': 'user_id格式错误'}, status=400)
                    try:
                        user = User.objects.get(user_id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({'error': '用户不存在'}, status=404)    
                except KeyError:
                    return JsonResponse({'error': '缺少user_id参数'}, status=400)

                if 'mobile' in modify_data:
                    return JsonResponse({'error': '禁止修改手机号'}, status=403)

                for field, value in modify_data.items():
                    if hasattr(user, field) and field != 'mobile':
                        setattr(user, field, value)
                user.save()
                return JsonResponse({'message': '用户信息更新成功'}, status=200)

            except UnicodeDecodeError:
                return JsonResponse({'error': '字符编码错误'}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({'error': '无效的JSON格式'}, status=400)
            except Exception as e:
                logger.error(f'用户信息修改失败: {str(e)}')
                return JsonResponse({'error': '服务器处理失败'}, status=500)
    except Exception as e:
        logger.error(f'接口异常: {str(e)}')
        return JsonResponse({'error': '服务器错误'}, status=500)


def user_get_id(request):
    mobile = request.GET.get('mobile')
    if not mobile:
        return JsonResponse({'error': '缺少mobile参数'}, status=400)
    
    try:
        user = User.objects.get(mobile=mobile)
        return JsonResponse({'user_id': user.user_id})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        logger.error(f'查询用户ID失败: {str(e)}')
        return JsonResponse({'error': '服务器内部错误'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verification_status(request):
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        mobile = data.get('mobile')
        password = data.get('password')
        
        # 验证必填字段
        if not all([mobile, password]):
            return JsonResponse({
                'error': '缺少必要参数',
                'required': ['mobile', 'password']
            }, status=400)
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'error': '手机号格式错误'
            }, status=400)
        
        # 检查用户是否存在
        max_retries = 3  # 增加重试次数
        retry_count = 0
        user = None
        while retry_count < max_retries:
            try:
                logger.debug(f'开始查询用户(尝试{retry_count+1}/{max_retries}): mobile={mobile}')
                # 检查数据库连接状态
                from django.db import connection
                if not connection.is_usable():
                    logger.warning('数据库连接不可用，尝试重新连接')
                    connection.close()
                    connection.connect()
                user = User.objects.get(mobile=mobile)
                logger.debug(f'用户查询成功: user_id={user.user_id}')
                break
            except User.DoesNotExist:
                logger.info(f'手机号未注册: {mobile}')
                return JsonResponse({
                    'error': '手机号未注册'
                }, status=404)
            except User.MultipleObjectsReturned:
                logger.error(f'手机号{mobile}存在多个账户记录，导致查询异常')
                return JsonResponse({
                    'error': '系统错误：该手机号存在重复账户'
                }, status=500)
            except Exception as e:
                retry_count += 1
                logger.error(f'用户查询异常(尝试{retry_count}/{max_retries}): {str(e)}', exc_info=True)
                if retry_count >= max_retries:
                    return JsonResponse({
                        'error': '用户信息查询失败，请稍后重试'
                    }, status=500)
                # 指数退避策略：0.5s, 1s, 2s...
                import time
                sleep_time = 0.5 * (2 **(retry_count - 1))
                logger.debug(f'等待{sleep_time}秒后重试...')
                time.sleep(sleep_time)
        
        # 确保用户对象已正确获取
        if user is None:
            logger.error('所有重试均失败，用户对象未获取')
            return JsonResponse({
                'error': '系统繁忙，请稍后再试'
            }, status=503)
        
        # 验证密码
        try:
            logger.debug(f'开始密码验证: user_id={user.user_id}')
            if not check_password(password, user.password):
                logger.warning(f'密码验证失败: user_id={user.user_id}')
                return JsonResponse({
                    'error': '账号存在但密码错误'
                }, status=401)
            logger.debug(f'密码验证成功: user_id={user.user_id}')
        except Exception as e:
            logger.error(f'密码验证异常: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': '密码验证过程失败'
            }, status=500)
        
        # 验证成功
        try:
            response_data = {
                'success': True,
                'message': '登录状态验证成功',
                'user_id': user.user_id
            }
            logger.debug(f'生成成功响应: {response_data}')
            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.error(f'响应生成异常: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': '系统响应生成失败'
            }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'登录状态验证异常: {str(e)}')
        return JsonResponse({'error': '服务器内部错误'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def wechat_login(request):
    """
    微信小程序一键登录
    请求参数: {"code": "微信小程序登录code"}
    返回: {"token": {"refresh": "刷新令牌", "access": "访问令牌"}, "user_id": "用户ID"}
    """
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        code = data.get('code')
        
        if not code:
            return JsonResponse({'error': '缺少code参数'}, status=400)
        
        # 调用微信API获取openid和session_key
        params = {
            'appid': WECHAT_APP_ID,
            'secret': WECHAT_APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        url = f'{WECHAT_LOGIN_URL}?{urllib.parse.urlencode(params)}'
        
        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read().decode())
            
            # 检查是否返回错误
            if 'errcode' in result:
                logger.error(f'微信登录失败: {result}')
                return JsonResponse({
                    'error': f'微信登录失败: {result.get("errmsg", "未知错误")}'
                }, status=400)
            
            openid = result.get('openid')
            session_key = result.get('session_key')
            
            if not openid:
                logger.error('微信返回数据中没有openid')
                return JsonResponse({'error': '微信登录失败，未获取到openid'}, status=400)
            
            # 获取用户信息
            user_info = data.get('userInfo', {})
            logger.warning(f'微信登录用户信息: {user_info}')  # 使用warning级别确保日志被记录
            
            # 检查userInfo是否为空或格式不正确
            if not user_info:
                logger.warning('用户信息为空，使用默认昵称')
                nickname = f'微信用户_{openid[:8]}'
            else:
                # 尝试获取nickName，考虑可能的大小写问题
                nickname = user_info.get('nickName') or user_info.get('nickname') or f'微信用户_{openid[:8]}'
                logger.warning(f'解析得到的昵称: {nickname}')
                
                # 检查昵称是否有乱码
                try:
                    nickname.encode('utf-8').decode('utf-8')
                except UnicodeDecodeError:
                    logger.error(f'昵称存在编码问题: {nickname}')
                    nickname = f'微信用户_{openid[:8]}'
            
            avatar_url = user_info.get('avatarUrl', '') or user_info.get('avatar_url', '')
            logger.warning(f'解析得到的头像URL: {avatar_url}')
        
        # 查询或创建用户
        with transaction.atomic():
            try:
                user = User.objects.get(openid=openid)
                logger.info(f'用户已存在: {user.user_id}')
                # 用户已存在时，不更新用户信息，直接使用数据库中的信息
            except User.DoesNotExist:
                # 创建新用户
                user = User.objects.create(
                    openid=openid,
                    nickname=nickname,
                    default_receiver='',  # 提供默认值避免非空错误
                    province='',
                    city='',
                    county='',
                    detailed_address='',
                    # 微信登录无需密码
                )
                logger.info(f'创建新用户: {user.user_id}')
                
                # 如果提供了头像URL，则下载并保存头像
                if avatar_url:
                    try:
                        # 确保media/user_avatars目录存在
                        import os
                        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'user_avatars')
                        if not os.path.exists(avatar_dir):
                            os.makedirs(avatar_dir)
                        
                        with urllib.request.urlopen(avatar_url) as img_response:
                            img_data = img_response.read()
                            
                            img_name = f'{openid}_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpg'
                            user.user_img.save(img_name, File(BytesIO(img_data)))
                    except Exception as e:
                        logger.error(f'下载或保存头像失败: {str(e)}')
        
        # 生成令牌
        tokens = user.generate_tokens()
        
        # 准备响应数据
        response_data = {
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': tokens,
                'user_id': user.user_id
            }
        }
        
        # 如果有头像，返回完整的头像URL
        if user.user_img:
            avatar_url = request.build_absolute_uri(user.user_img.url)
            response_data['data']['avatar_url'] = avatar_url
        
        return JsonResponse(response_data)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'微信登录异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': f'服务器内部错误: {str(e)}'}, status=500)
