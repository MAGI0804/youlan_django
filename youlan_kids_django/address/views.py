from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import Address
from users.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def add_address(request):
    """
    新增用户地址
    请求参数：
        user_id: 用户ID
        province: 省
        city: 市
        county: 县/区
        detailed_address: 详细地址
        receiver_name: 收货人
        phone_number: 联系电话
        is_default: 是否为默认地址（可选，默认为False）
        remark: 备注（可选）
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        province = data.get('province')
        city = data.get('city')
        county = data.get('county')
        detailed_address = data.get('detailed_address')
        receiver_name = data.get('receiver_name')
        phone_number = data.get('phone_number')
        is_default = data.get('is_default', False)
        remark = data.get('remark', '')

        # 检查必填字段
        if not all([user_id, province, city, county, detailed_address, receiver_name, phone_number]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 验证用户是否存在
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)

        # 创建新地址
        address = Address.objects.create(
            user=user,
            province=province,
            city=city,
            county=county,
            detailed_address=detailed_address,
            receiver_name=receiver_name,
            phone_number=phone_number,
            is_default=is_default,
            remark=remark
        )

        logger.info(f'用户 {user.user_id} 新增地址成功: {address.address_id}')
        return JsonResponse({
            'success': True,
            'message': '新增地址成功',
            'address_id': address.address_id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'新增地址失败: {str(e)}')
        return JsonResponse({'error': f'新增地址失败: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_address_by_id(request):
    """
    查询单个地址
    请求参数：
        address_id: 地址ID
        user_id: 用户ID
    """
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        user_id = data.get('user_id')

        # 检查必填字段
        if not all([address_id, user_id]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 验证地址是否存在且属于该用户
        try:
            address = Address.objects.get(address_id=address_id, user__user_id=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'error': '地址不存在或不属于该用户'}, status=404)

        # 构建返回数据
        address_data = {
            'address_id': address.address_id,
            'province': address.province,
            'city': address.city,
            'county': address.county,
            'detailed_address': address.detailed_address,
            'receiver_name': address.receiver_name,
            'phone_number': address.phone_number,
            'is_default': address.is_default,
            'remark': address.remark
        }

        logger.info(f'用户 {user_id} 查询地址 {address_id} 成功')
        return JsonResponse({
            'success': True,
            'message': '查询地址成功',
            'address': address_data
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'查询地址失败: {str(e)}')
        return JsonResponse({'error': f'查询地址失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_address(request):
    """
    删除用户地址
    请求参数：
        address_id: 地址ID
        user_id: 用户ID
    """
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        user_id = data.get('user_id')

        # 检查必填字段
        if not all([address_id, user_id]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 验证地址是否存在且属于该用户
        try:
            address = Address.objects.get(address_id=address_id, user__user_id=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'error': '地址不存在或不属于该用户'}, status=404)

        # 删除地址
        address.delete()
        logger.info(f'用户 {user_id} 删除地址成功: {address_id}')
        return JsonResponse({
            'success': True,
            'message': '删除地址成功'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'删除地址失败: {str(e)}')
        return JsonResponse({'error': f'删除地址失败: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_address(request):
    """
    更新用户地址
    请求参数：
        address_id: 地址ID
        user_id: 用户ID
        province: 省（可选）
        city: 市（可选）
        county: 县/区（可选）
        detailed_address: 详细地址（可选）
        receiver_name: 收货人（可选）
        phone_number: 联系电话（可选）
        is_default: 是否为默认地址（可选）
        remark: 备注（可选）
    """
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        user_id = data.get('user_id')

        # 检查必填字段
        if not all([address_id, user_id]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 验证地址是否存在且属于该用户
        try:
            address = Address.objects.get(address_id=address_id, user__user_id=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'error': '地址不存在或不属于该用户'}, status=404)

        # 更新地址信息
        update_fields = ['province', 'city', 'county', 'detailed_address', 'receiver_name', 'phone_number', 'is_default', 'remark']
        for field in update_fields:
            if field in data:
                setattr(address, field, data[field])

        # 保存更新后的地址
        address.save()
        logger.info(f'用户 {user_id} 更新地址成功: {address_id}')
        return JsonResponse({
            'success': True,
            'message': '更新地址成功'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'更新地址失败: {str(e)}')
        return JsonResponse({'error': f'更新地址失败: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def set_default_address(request):
    """
    设置默认地址
    请求参数：
        address_id: 地址ID
        user_id: 用户ID
    """
    try:
        data = json.loads(request.body)
        address_id = data.get('address_id')
        user_id = data.get('user_id')

        # 检查必填字段
        if not all([address_id, user_id]):
            return JsonResponse({'error': '缺少必填字段'}, status=400)

        # 验证地址是否存在且属于该用户
        try:
            address = Address.objects.get(address_id=address_id, user__user_id=user_id)
        except Address.DoesNotExist:
            return JsonResponse({'error': '地址不存在或不属于该用户'}, status=404)

        # 设置该地址为默认地址，其他地址自动取消默认（在模型的save方法中实现）
        address.is_default = True
        address.save()
        
        logger.info(f'用户 {user_id} 设置默认地址成功: {address_id}')
        return JsonResponse({
            'success': True,
            'message': '设置默认地址成功'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'设置默认地址失败: {str(e)}')
        return JsonResponse({'error': f'设置默认地址失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_addresses(request):
    """
    查询用户的所有地址信息
    请求参数：
        user_id: 用户ID
    返回：
        addresses: 地址列表，包含每个地址的详细信息
    """
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')

        # 检查必填字段
        if not user_id:
            return JsonResponse({'error': '缺少用户ID'}, status=400)

        # 验证用户是否存在
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)

        # 查询用户的所有地址
        addresses = Address.objects.filter(user=user).order_by('-is_default', 'created_at')
        
        # 格式化地址数据
        address_list = []
        for addr in addresses:
            address_list.append({
                'address_id': addr.address_id,
                'province': addr.province,
                'city': addr.city,
                'county': addr.county,
                'detailed_address': addr.detailed_address,
                'receiver_name': addr.receiver_name,
                'phone_number': addr.phone_number,
                'is_default': addr.is_default,
                'remark': addr.remark,
                'created_at': addr.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': addr.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        logger.info(f'查询用户 {user_id} 地址信息成功，共 {len(address_list)} 条记录')
        return JsonResponse({
            'success': True,
            'message': '查询地址成功',
            'addresses': address_list
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': '请求数据格式错误'}, status=400)
    except Exception as e:
        logger.error(f'查询地址失败: {str(e)}')
        return JsonResponse({'error': f'查询地址失败: {str(e)}'}, status=500)
