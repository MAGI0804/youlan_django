import random
from dataclasses import field
import re
from datetime import datetime
import secrets
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from  .models import Order
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
import logging
import json
from django.db import transaction
from django.urls import reverse
from order.demo import get_kdniao_logistics
from django.http import JsonResponse
import json
import logging
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta

# 初始化审计日志
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('audit')


@csrf_exempt
@require_http_methods(['POST'])
def add_order(request):  #新增订单
    try:
        # 解析请求体数据
        data = json.loads(request.body)

        # 验证必填参数
        required_fields = ['receiver_name', 'province', 'city', 'county', 'detailed_address', 'order_amount', 'product_list', 'user_id']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'status': 'error', 'message': f'缺少必填参数: {field}'}, status=400)

        # 验证product_list是否为列表
        if not isinstance(data.get('product_list'), list):
            return JsonResponse({'status': 'error', 'message': 'product_list必须是列表类型'}, status=400)

        # 生成order_id: Y+YYYYMMDD+8位随机数字

        current_date = datetime.now().strftime('%Y%m%d')
        max_retries = 5
        retry_count = 0
        order = None
        while retry_count < max_retries:
            try:
                random_num = ''.join(secrets.choice('0123456789') for _ in range(8))
                order_id = f'Y{current_date}{random_num}'
                
                # 检查order_id是否已存在
                if not Order.objects.filter(order_id=order_id).exists():
                    # 创建订单，包含新增字段
                    order = Order(
                        order_id=order_id,
                        user_id=data['user_id'],
                        receiver_name=data['receiver_name'],
                        receiver_phone=data.get('receiver_phone', ''),
                        province=data['province'],
                        city=data['city'],
                        county=data['county'],
                        detailed_address=data['detailed_address'],
                        order_amount=data['order_amount'],
                        product_list=json.dumps(data['product_list']),  # 将列表转换为JSON字符串存储
                        express_company=data.get('express_company', ''),
                        express_number=data.get('express_number', '')
                    )
                    order.save()
                    break
            except IntegrityError:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception("生成订单号失败，重试次数过多")

        return JsonResponse({
            'status': 'success',
            'message': '订单创建成功',
            'order_id': order_id,
            'data': {
                'order_id': order_id,
                'user_id': data['user_id'],
                'receiver_name': data['receiver_name'],
                'receiver_phone': data.get('receiver_phone', ''),
                'express_company': data.get('express_company', ''),
                'express_number': data.get('express_number', '')
            }
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式不是有效的JSON'}, status=400)
    except Exception as e:
        logger.error(f'创建订单失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': f'服务器内部错误: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def query_order_data(request):  # 查询订单信息
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        order_id = data.get('order_id')
        user_id = data.get('user_id')

        # 检查必要参数
        if not order_id:
            return JsonResponse({'status': 'error', 'message': '缺少order_id参数'}, status=400)

        # 构建查询条件
        query_kwargs = {'order_id': order_id}
        if user_id:
            query_kwargs['user_id'] = user_id

        # 查询订单
        try:
            order = Order.objects.get(**query_kwargs)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

        # 解析商品列表
        try:
            product_list = json.loads(order.product_list)
        except json.JSONDecodeError:
            product_list = []

        # 转换下单时间为UTC+8并格式化
        order_time_cn = order.order_time + timedelta(hours=8)
        formatted_time = order_time_cn.strftime('%Y-%m-%d %H:%M:%S')

        # 返回订单信息（不含物流更新和物流信息返回）
        return JsonResponse({
            'status': 'success',
            'message': '查询订单信息成功',
            'data': {
                'order_id': order.order_id,
                'user_id': order.user_id,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone or '',
                'province': order.province,
                'city': order.city,
                'county': order.county,
                'detailed_address': order.detailed_address,
                'order_amount': float(order.order_amount),
                'product_list': product_list,
                'status': order.status,
                'order_time': formatted_time,
                'express_company': order.express_company or '',
                'express_number': order.express_number or ''
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式错误'}, status=400)
    except Exception as e:
        logger.error(f'查询订单信息失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def change_receiving_data(request):  # 修改收货信息
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        order_id = data.get('order_id')
        receiver_name = data.get('receiver_name')
        receiver_phone = data.get('receiver_phone')
        province = data.get('province')
        city = data.get('city')
        county = data.get('county')
        detailed_address = data.get('detailed_address')

        # 验证必要参数
        if not order_id:
            return JsonResponse({'status': 'error', 'message': '缺少order_id参数'}, status=400)

        # 检查地址字段是否部分提供
        address_fields = [province, city, county, detailed_address]
        has_address = any(field is not None for field in address_fields)
        all_address = all(field is not None for field in address_fields)

        if has_address and not all_address:
            return JsonResponse({
                'status': 'error',
                'message': '地址字段(province, city, county, detailed_address)必须同时提供'
            }, status=400)

        # 验证是否有可修改的字段
        if receiver_name is None and receiver_phone is None and not has_address:
            return JsonResponse({
                'status': 'error',
                'message': '至少需要提供receiver_name、receiver_phone或地址字段'
            }, status=400)

        # 查询订单
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

        # 更新字段
        updated_fields = {}
        if receiver_name is not None:
            order.receiver_name = receiver_name
            updated_fields['receiver_name'] = receiver_name
        if receiver_phone is not None:
            order.receiver_phone = receiver_phone
            updated_fields['receiver_phone'] = receiver_phone
        if has_address:
            order.province = province
            order.city = city
            order.county = county
            order.detailed_address = detailed_address
            updated_fields.update({
                'province': province,
                'city': city,
                'county': county,
                'detailed_address': detailed_address
            })

        order.save()
        return JsonResponse({
            'status': 'success', 
            'message': '收货信息更新成功',
            'order_id': order_id,
            'updated_fields': updated_fields
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式错误'}, status=400)
    except Exception as e:
        logger.error(f'修改收货信息失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def update_express_info(request):  # 修改订单物流信息
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        order_id = data.get('order_id')
        express_company = data.get('express_company')
        express_number = data.get('express_number')
        logistics_process = data.get('logistics_process')

        # 验证必要参数
        if not order_id:
            return JsonResponse({'status': 'error', 'message': '缺少必要参数order_id'}, status=400)

        # 验证是否提供了至少一个物流信息字段
        if express_company is None and express_number is None and logistics_process is None:
            return JsonResponse({'status': 'error', 'message': '至少需要提供express_company、express_number或logistics_process'}, status=400)

        # 查询订单
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

        # 更新物流信息
        updated_fields = {}
        if express_company is not None:
            order.express_company = express_company
            updated_fields['express_company'] = express_company
        if express_number is not None:
            order.express_number = express_number
            updated_fields['express_number'] = express_number
        if logistics_process is not None:
            # 验证logistics_process是否为有效的JSON字符串或列表
            if isinstance(logistics_process, (dict, list)):
                order.logistics_process = json.dumps(logistics_process)
            else:
                # 假设已经是JSON字符串，直接存储
                order.logistics_process = logistics_process
            updated_fields['logistics_process'] = logistics_process
        order.save()

        # 记录物流信息变更日志
        audit_logger.info(f'订单物流信息变更: order_id={order_id}, 更新字段={updated_fields}')

        # 解析商品列表用于返回
        try:
            product_list = json.loads(order.product_list)
        except json.JSONDecodeError:
            product_list = []

        # 转换下单时间为UTC+8并格式化
        order_time_cn = order.order_time + timedelta(hours=8)
        formatted_time = order_time_cn.strftime('%Y-%m-%d %H:%M:%S')

        # 返回更新后的订单信息，包含物流信息
        return JsonResponse({
            'status': 'success',
            'message': '物流信息更新成功',
            'data': {
                'order_id': order.order_id,
                'status': order.status,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone or '',
                'province': order.province,
                'city': order.city,
                'county': order.county,
                'detailed_address': order.detailed_address,
                'order_amount': float(order.order_amount),
                'product_list': product_list,
                'order_time': formatted_time,
                'express_company': order.express_company or '',
                'express_number': order.express_number or ''
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式错误'}, status=400)
    except Exception as e:
        logger.error(f'修改订单物流信息失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def sync_logistics_info(request):  # 同步物流信息
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        order_id = data.get('order_id')
        express_company = data.get('express_company')
        express_number = data.get('express_number')

        # 验证必要参数
        if not order_id:
            return JsonResponse({'status': 'error', 'message': '缺少必要参数order_id'}, status=400)

        # 查询订单
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

        # 检查订单状态，只有shipped和delivered状态才更新物流信息
        if order.status not in ['shipped', 'delivered']:
            return JsonResponse({'status': 'error', 'message': '只有已发货和已送达状态的订单才支持同步物流信息'}, status=400)

        # 从订单中获取物流信息
        express_company = order.express_company
        express_number = order.express_number

        # 检查是否有物流单号
        if not express_number:
            return JsonResponse({'status': 'error', 'message': '订单没有物流单号，无法同步物流信息'}, status=400)



        # 实际物流信息查询逻辑 - 使用快递鸟API
        logistics_process = []
        try:
            # 直接调用快递鸟API查询真实物流信息
            result = get_kdniao_logistics(express_number)
            if result.get('success'):
                logistics_process = result['data']['logistics_info']
            else:
                logger.error(f'调用快递鸟API失败: {result.get("message", "未知错误")}')
        except Exception as e:
            logger.error(f'调用物流API异常: {str(e)}')
            # 如果API调用失败，返回空列表

        # 更新订单的物流信息
        order.express_company = express_company
        order.express_number = express_number
        order.logistics_process = json.dumps(logistics_process)
        order.save()

        # 记录物流信息同步日志
        audit_logger.info(f'订单物流信息同步: order_id={order_id}, express_company={express_company}, express_number={express_number}')

        # 返回物流信息（只包含订单号和物流相关信息）
        return JsonResponse({
            'status': 'success', 
            'message': '物流信息同步成功',
            'data': {
                'order_id': order.order_id,
                'express_company': order.express_company or '',
                'express_number': order.express_number or '',
                'logistics_process': logistics_process
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式错误'}, status=400)
    except Exception as e:
        logger.error(f'同步物流信息失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def change_status(request):  # 修改订单状态
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        # 允许同时更新物流信息
        express_company = data.get('express_company')
        express_number = data.get('express_number')
        logistics_process = data.get('logistics_process')

        # 验证必要参数
        if not order_id or status is None:
            return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)

        # 验证订单状态是否合法
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if status not in valid_statuses:
            return JsonResponse({'status': 'error', 'message': '无效的订单状态'}, status=400)

        # 查询订单
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '订单不存在'}, status=404)

        # 记录旧状态
        old_status = order.status
        
        # 更新订单状态和物流信息
        order.status = status
        updated_express_info = {}
        if express_company is not None:
            order.express_company = express_company
            updated_express_info['express_company'] = express_company
        if express_number is not None:
            order.express_number = express_number
            updated_express_info['express_number'] = express_number
        if logistics_process is not None:
            # 验证logistics_process是否为有效的JSON字符串或列表
            if isinstance(logistics_process, (dict, list)):
                order.logistics_process = json.dumps(logistics_process)
            else:
                # 假设已经是JSON字符串，直接存储
                order.logistics_process = logistics_process
            updated_express_info['logistics_process'] = logistics_process
        order.save()

        # 记录状态变更日志
        audit_logger.info(f'订单状态变更: order_id={order_id}, 旧状态={old_status}, 新状态={status}')

        # 解析商品列表用于返回
        try:
            product_list = json.loads(order.product_list)
        except json.JSONDecodeError:
            product_list = []

        # 转换下单时间为UTC+8并格式化
        order_time_cn = order.order_time + timedelta(hours=8)
        formatted_time = order_time_cn.strftime('%Y-%m-%d %H:%M:%S')

        # 返回更新后的订单信息，包含新增字段
        return JsonResponse({
            'status': 'success',
            'message': '订单状态更新成功',
            'data': {
                'order_id': order.order_id,
                'status': order.status,
                'old_status': old_status,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone or '',
                'province': order.province,
                'city': order.city,
                'county': order.county,
                'detailed_address': order.detailed_address,
                'order_amount': float(order.order_amount),
                'product_list': product_list,
                'order_time': formatted_time,
                'express_company': order.express_company or '',
                'express_number': order.express_number or '',
                'logistics_process': []  # 批量查询时不返回实际物流信息
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '请求体格式错误'}, status=400)
    except Exception as e:
        logger.error(f'修改订单状态失败: {str(e)}')
        return JsonResponse({'status': 'error', 'message': '服务器内部错误'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def orders_query(request):
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        
        # 验证shopname参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({
                'status': 'error', 
                'message': '无效的店铺名称'
            }, status=400)
        
        # 获取并验证user_id参数
        user_id = data.get('user_id')
        
        # 获取并验证订单状态参数
        order_status = data.get('status')
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        
        # 验证分页参数
        try:
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 20))
            
            # 确保页码为正整数
            if page < 1:
                page = 1
            # 限制最大每页数量为50
            if page_size > 50:
                page_size = 50
            elif page_size < 1:
                page_size = 20
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error', 
                'message': 'page和page_size必须为整数'
            }, status=400)
        
        # 处理日期范围参数
        begin_time = data.get('begin_time')
        end_time = data.get('end_time')
        begin_utc = None
        end_utc = None
        
        # 验证日期格式
        def validate_date(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
        
        begin_date = validate_date(begin_time) if begin_time else None
        end_date = validate_date(end_time) if end_time else None
        
        if (begin_time and not begin_date) or (end_time and not end_date):
            return JsonResponse({
                'status': 'error', 
                'message': '日期格式必须为YYYY-MM-DD'
            }, status=400)
        
        # 转换为UTC时间范围
        if begin_date:
            begin_utc = begin_date - timedelta(hours=8)
        if end_date:
            end_utc = end_date + timedelta(days=1) - timedelta(hours=8)
        
        # 构建查询集
        queryset = Order.objects.all()
        
        # 应用user_id过滤（如果提供）
        if user_id:
            try:
                user_id = int(user_id)
                queryset = queryset.filter(user_id=user_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error', 
                    'message': 'user_id必须为整数'
                }, status=400)
        
        # 应用订单状态过滤（如果提供且有效）
        if order_status:
            if order_status not in valid_statuses:
                return JsonResponse({
                    'status': 'error', 
                    'message': f"订单状态必须是以下值之一: {', '.join(valid_statuses)}"
                }, status=400)
            queryset = queryset.filter(status=order_status)
        
        # 应用日期过滤
        if begin_utc and end_utc:
            queryset = queryset.filter(order_time__range=(begin_utc, end_utc))
        elif begin_utc:
            queryset = queryset.filter(order_time__gte=begin_utc)
        elif end_utc:
            queryset = queryset.filter(order_time__lt=end_utc)
        
        # 计算查询偏移量
        offset = (page - 1) * page_size
        
        # 查询订单数据并分页
        orders = queryset.order_by('-order_time')[offset:offset+page_size]
        
        # 处理订单数据
        result = []
        for order in orders:
            # 转换下单时间为UTC+8并格式化
            order_time_cn = order.order_time + timedelta(hours=8)
            formatted_time = order_time_cn.strftime('%Y-%m-%d %H:%M:%S')
            
            # 解析商品列表
            try:
                product_list = json.loads(order.product_list)
            except json.JSONDecodeError:
                product_list = []
            
            result.append({
                'order_id': order.order_id,
                'user_id': order.user_id,
                'product_list': product_list,
                'order_amount': float(order.order_amount),
                'status': order.status,
                'order_time': formatted_time,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone or '',
                'express_company': order.express_company or '',
                'express_number': order.express_number or '',
                'logistics_process': []  # 批量查询时不返回实际物流信息
            })
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'page': page,
            'page_size': page_size,
            'total': queryset.count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error', 
            'message': '请求体格式不是有效的JSON'
        }, status=400)
    except Exception as e:
        logger.error(f'批量查询订单失败: {str(e)}')
        return JsonResponse({
            'status': 'error', 
            'message': f'服务器内部错误: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def batch_orders_query(request):
    """批量查询订单，要求必须提供user_id参数"""
    try:
        # 解析请求体数据
        data = json.loads(request.body)
        
        # 验证shopname参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({
                'status': 'error', 
                'message': '无效的店铺名称'
            }, status=400)
        
        # 获取并验证user_id参数（必填）
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({
                'status': 'error', 
                'message': 'user_id为必填参数'
            }, status=400)
        
        # 获取并验证订单状态参数
        order_status = data.get('status')
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        
        # 验证分页参数
        try:
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 20))
            
            # 确保页码为正整数
            if page < 1:
                page = 1
            # 限制最大每页数量为50
            if page_size > 50:
                page_size = 50
            elif page_size < 1:
                page_size = 20
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error', 
                'message': 'page和page_size必须为整数'
            }, status=400)
        
        # 处理日期范围参数
        begin_time = data.get('begin_time')
        end_time = data.get('end_time')
        begin_utc = None
        end_utc = None
        
        # 验证日期格式
        def validate_date(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return None
        
        begin_date = validate_date(begin_time) if begin_time else None
        end_date = validate_date(end_time) if end_time else None
        
        if (begin_time and not begin_date) or (end_time and not end_date):
            return JsonResponse({
                'status': 'error', 
                'message': '日期格式必须为YYYY-MM-DD'
            }, status=400)
        
        # 转换为UTC时间范围
        if begin_date:
            begin_utc = begin_date - timedelta(hours=8)
        if end_date:
            end_utc = end_date + timedelta(days=1) - timedelta(hours=8)
        
        # 构建查询集
        queryset = Order.objects.all()
        
        # 应用user_id过滤（必填）
        try:
            user_id = int(user_id)
            queryset = queryset.filter(user_id=user_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error', 
                'message': 'user_id必须为整数'
            }, status=400)
        
        # 应用订单状态过滤（如果提供且有效）
        if order_status:
            if order_status not in valid_statuses:
                return JsonResponse({
                    'status': 'error', 
                    'message': f"订单状态必须是以下值之一: {', '.join(valid_statuses)}"
                }, status=400)
            queryset = queryset.filter(status=order_status)
        
        # 应用日期过滤
        if begin_utc and end_utc:
            queryset = queryset.filter(order_time__range=(begin_utc, end_utc))
        elif begin_utc:
            queryset = queryset.filter(order_time__gte=begin_utc)
        elif end_utc:
            queryset = queryset.filter(order_time__lt=end_utc)
        
        # 计算查询偏移量
        offset = (page - 1) * page_size
        
        # 查询订单数据并分页
        orders = queryset.order_by('-order_time')[offset:offset+page_size]
        
        # 处理订单数据
        result = []
        for order in orders:
            # 转换下单时间为UTC+8并格式化
            order_time_cn = order.order_time + timedelta(hours=8)
            formatted_time = order_time_cn.strftime('%Y-%m-%d %H:%M:%S')
            
            # 解析商品列表
            try:
                product_list = json.loads(order.product_list)
            except json.JSONDecodeError:
                product_list = []
            
            result.append({
                'order_id': order.order_id,
                'user_id': order.user_id,
                'product_list': product_list,
                'order_amount': float(order.order_amount),
                'status': order.status,
                'order_time': formatted_time,
                'receiver_name': order.receiver_name,
                'receiver_phone': order.receiver_phone or '',
                'express_company': order.express_company or '',
                'express_number': order.express_number or '',
                'logistics_process': json.loads(order.logistics_process) if order.logistics_process else []
            })
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'page': page,
            'page_size': page_size,
            'total': queryset.count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error', 
            'message': '请求体格式不是有效的JSON'
        }, status=400)
    except Exception as e:
        logger.error(f'批量查询订单失败: {str(e)}')
        return JsonResponse({
            'status': 'error', 
            'message': f'服务器内部错误: {str(e)}'
        }, status=500)

