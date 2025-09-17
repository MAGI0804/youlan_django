import json
import re
import time
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password,check_password
from django.db import IntegrityError, connection
from django.views.decorators.http import require_http_methods
import logging
from .models import OperationUser,CustomerServiceUser
logger = logging.getLogger(__name__)


@csrf_exempt
def add_service_user(request):  #注册运营用户
    # 生成唯一请求ID用于追踪
    request_id = str(uuid.uuid4())
    logger.info(f'add_service_user request received, request_id={request_id}')
    if request.method != 'POST':
        logger.warning(f'add_service_user received non-POST request, request_id={request_id}')
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 检查数据库连接
            if not connection.is_usable():
                logger.warning(f'Database connection not usable, reconnecting... request_id={request_id}')
                connection.close()
                connection.connect()

            # 解析请求体JSON数据
            data = json.loads(request.body)
            nickname = data.get('nickname')
            mobile = data.get('mobile')
            password = data.get('password')
            # 添加幂等性校验token
            logger.debug(f'add_service_user parameters: nickname={nickname}, mobile={mobile}, request_id={request_id}')

            # 验证必填字段
            if not all([nickname, mobile, password]):
                logger.warning(f'Missing required fields in add_service_user, request_id={request_id}')
                return JsonResponse({
                    'error': 'Missing required fields',
                    'required': ['nickname', 'mobile', 'password']
                }, status=400)
            
            # 检查手机号是否已存在
            if CustomerServiceUser.objects.filter(mobile=mobile).exists():
                logger.warning(f'Mobile number already exists: {mobile}, request_id={request_id}')
                return JsonResponse({
                    'error': 'Mobile number already exists'
                }, status=400)
            
            # 密码哈希处理
            hashed_password = make_password(password)
            
            # 创建客服用户，保存请求token用于幂等性校验
            user = CustomerServiceUser(
                nickname=nickname,
                mobile=mobile,
                password=hashed_password,

            )
            user.save()
            logger.info(f'Customer service user created successfully: {user.user_id}, request_id={request_id}')
            
            return JsonResponse({
                'success': True,
                'message': 'Customer service user created successfully',
                'user_id': user.user_id
            }, status=201)
            
        except json.JSONDecodeError:
            logger.error(f'Invalid JSON format in add_service_user request, request_id={request_id}')
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except IntegrityError as e:
            logger.error(f'Integrity error in add_service_user: {str(e)}, request_id={request_id}')
            return JsonResponse({
                'error': 'Mobile number or nickname already exists'
            }, status=400)
        except Exception as e:
            retry_count += 1
            logger.error(f'Attempt {retry_count} failed in add_service_user: {str(e)}, request_id={request_id}', exc_info=True)
            if retry_count >= max_retries:
                return JsonResponse({
                    'error': 'Server error occurred after multiple attempts'
                }, status=500)
            # 指数退避重试
            sleep_time = 0.5 * (2 **(retry_count - 1))
            logger.debug(f'Retrying add_service_user after {sleep_time} seconds, request_id={request_id}')
            time.sleep(sleep_time)

@csrf_exempt
def add_operation_user(request):  #注册客服用户
    # 生成唯一请求ID用于追踪
    request_id = str(uuid.uuid4())
    logger.info(f'add_operation_user request received, request_id={request_id}')
    if request.method != 'POST':
        logger.warning(f'add_operation_user received non-POST request, request_id={request_id}')
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 检查数据库连接
            if not connection.is_usable():
                logger.warning(f'Database connection not usable, reconnecting... request_id={request_id}')
                connection.close()
                connection.connect()

            # 解析请求体JSON数据
            data = json.loads(request.body)
            nickname = data.get('nickname')
            mobile = data.get('mobile')
            password = data.get('password')
            level = data.get('level')
            # 添加幂等性校验token
            logger.debug(f'add_operation_user parameters: nickname={nickname}, mobile={mobile}, level={level}, request_id={request_id}')

            # 验证必填字段
            if not all([nickname, mobile, password, level]):
                logger.warning(f'Missing required fields in add_operation_user, request_id={request_id}')
                return JsonResponse({
                    'error': 'Missing required fields',
                    'required': ['nickname', 'mobile', 'password', 'level']
                }, status=400)
            
            # 检查手机号是否已存在
            if OperationUser.objects.filter(mobile=mobile).exists():
                logger.warning(f'Mobile number already exists: {mobile}, request_id={request_id}')
                return JsonResponse({
                    'error': 'Mobile number already exists'
                }, status=400)
            
            # 密码哈希处理
            hashed_password = make_password(password)
            
            # 创建运营用户，保存请求token用于幂等性校验
            user = OperationUser(
                nickname=nickname,
                mobile=mobile,
                password=hashed_password,
                level=level,

            )
            user.save()
            logger.info(f'Operation user created successfully: {user.user_id}, request_id={request_id}')
            
            return JsonResponse({
                'success': True,
                'message': 'Operation user created successfully',
                'user_id': user.user_id
            }, status=201)
            
        except json.JSONDecodeError:
            logger.error(f'Invalid JSON format in add_operation_user request, request_id={request_id}')
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except IntegrityError as e:
            logger.error(f'Integrity error in add_operation_user: {str(e)}, request_id={request_id}')
            return JsonResponse({
                'error': 'Mobile number or nickname already exists'
            }, status=400)
        except Exception as e:
            retry_count += 1
            logger.error(f'Attempt {retry_count} failed in add_operation_user: {str(e)}, request_id={request_id}', exc_info=True)
            if retry_count >= max_retries:
                return JsonResponse({
                    'error': 'Server error occurred after multiple attempts'
                }, status=500)
            # 指数退避重试
            sleep_time = 0.5 * (2** (retry_count - 1))
            logger.debug(f'Retrying add_operation_user after {sleep_time} seconds, request_id={request_id}')
            time.sleep(sleep_time)

@csrf_exempt
@require_http_methods(["POST"])
def verification_status(request):   #验证登录结果
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        mobile = data.get('mobile')
        password = data.get('password')
        object_num = data.get('object_num')
        
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
        if object_num == '1':
            User = OperationUser
        elif object_num == '2':
            User = CustomerServiceUser
        else:
            return JsonResponse({
                'error': 'object_num参数错误'
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
                'user_id': user.user_id,
                'nickname': user.nickname
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
@require_http_methods(["POST"])   #修改密码
def change_password(request):
    request_id = str(uuid.uuid4())
    logger.info(f'change_password request received, request_id={request_id}')
    if request.method != 'POST':
        logger.warning(f'change_password received non-POST request, request_id={request_id}')
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            if not connection.is_usable():
                logger.warning(f'Database connection not usable, reconnecting... request_id={request_id}')
                connection.close()
                connection.connect()

            data = json.loads(request.body)
            object_num = data.get('object_num')
            mobile = data.get('mobile')
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if not all([object_num, mobile, old_password, new_password]):
                return JsonResponse({'error': 'Missing required fields', 'required': ['object_num', 'mobile', 'old_password', 'new_password']}, status=400)
            
            if object_num not in [1, 2]:
                return JsonResponse({'error': 'object_num must be 1 or 2'}, status=400)
            
            if not re.match(r'^1[3-9]\d{9}$', mobile):
                return JsonResponse({'error': 'Invalid mobile format'}, status=400)
            
            Model = OperationUser if object_num == 1 else CustomerServiceUser
            
            try:
                user = Model.objects.get(mobile=mobile)
            except Model.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            if not check_password(old_password, user.password):
                return JsonResponse({'error': 'Old password is incorrect'}, status=400)
            
            user.password = make_password(new_password)
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Password updated successfully'}, status=200)
            
        except json.JSONDecodeError:
            logger.error(f'Invalid JSON format, request_id={request_id}')
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            retry_count += 1
            logger.error(f'Attempt {retry_count} failed: {str(e)}, request_id={request_id}', exc_info=True)
            if retry_count >= max_retries:
                return JsonResponse({'error': 'Server error after multiple attempts'}, status=500)
            sleep_time = 0.5 * (2 **(retry_count -1))
            time.sleep(sleep_time)


