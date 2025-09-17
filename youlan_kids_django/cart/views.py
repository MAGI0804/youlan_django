from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
from users.models import User
from .models import Cart
import logging
# 配置日志
logger = logging.getLogger('django')

@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """
    添加商品到购物车
    请求体参数: user_id, commodity_code, quantity(可选，默认1)
    """
    try:
        user_id = request.data.get('user_id')
        commodity_code = request.data.get('commodity_code')
        quantity = request.data.get('quantity', 1)
        
        # 验证参数
        if not user_id or not commodity_code:
            return Response({
                'code': 400,
                'message': '参数错误：user_id和commodity_code不能为空'
            }, status=400)
        
        # 验证数量参数
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("数量必须为正整数")
        except ValueError:
            return Response({
                'code': 400,
                'message': '参数错误：quantity必须为正整数'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取或创建购物车
        cart, created = Cart.objects.get_or_create(user=user)
        
        # 确保商品编码是字符串类型（防止不同类型的相同编码被视为不同商品）
        commodity_code_str = str(commodity_code)
        
        # 使用模型方法添加商品到购物车
        cart.add_item(commodity_code_str, quantity)
        cart.save()
        
        # 确保使用相同的字符串类型获取商品数量
        current_quantity = cart.get_item_quantity(commodity_code_str)
        
        return Response({
            'code': 200,
            'message': '商品添加到购物车成功',
            'data': {
                'commodity_code': commodity_code,
                'quantity': current_quantity,
                'total_items': cart.get_total_items()
            }
        })
        
    except Exception as e:
        logger.error(f'添加商品到购物车失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'添加商品到购物车失败: {str(e)}'
        }, status=500)


@api_view(['DELETE', 'POST'])
@permission_classes([AllowAny])
def batch_delete_from_cart(request):
    """
    批量删除购物车商品
    请求体参数: user_id, commodity_codes (字符串列表)
    """
    try:
        user_id = request.data.get('user_id')
        commodity_codes = request.data.get('commodity_codes', [])
        
        # 记录接收到的参数，用于调试
        logger.info(f'批量删除购物车商品请求 - user_id: {user_id}, commodity_codes: {commodity_codes}, 类型: {type(commodity_codes)}')
        
        # 验证参数
        if not user_id:
            return Response({
                'code': 400,
                'message': '参数错误：user_id不能为空'
            }, status=400)
        
        if not isinstance(commodity_codes, list):
            return Response({
                'code': 400,
                'message': '参数错误：commodity_codes必须是列表格式'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取购物车
        cart = get_object_or_404(Cart, user=user)
        
        # 记录原始购物车内容
        logger.info(f'删除前购物车内容 - user_id: {user_id}, cart_items: {cart.cart_items}')
        
        # 批量删除商品
        deleted_count = 0  # 记录实际删除的商品数量
        not_exist_codes = []  # 记录购物车中不存在的商品编码
        
        for code in commodity_codes:
            # 确保code是字符串类型
            code_str = str(code)
            if code_str in cart.cart_items:
                logger.info(f'删除商品: {code_str}')
                success = cart.remove_item(code_str)
                if success:
                    deleted_count += 1
            else:
                logger.info(f'商品不在购物车中: {code_str}')
                not_exist_codes.append(code_str)
        
        # 保存购物车更改
        cart.save()
        
        # 根据删除情况返回不同的响应信息
        if deleted_count == 0:
            return Response({
                'code': 200,
                'message': '没有删除任何商品（所有指定的商品编码在购物车中不存在）',
                'deleted_count': deleted_count,
                'not_exist_codes': not_exist_codes,
                'remaining_items_count': len(cart.cart_items),
                'total_quantity': cart.get_total_items()
            })
        elif deleted_count < len(commodity_codes):
            return Response({
                'code': 200,
                'message': f'部分商品从购物车删除成功，成功删除{deleted_count}个商品',
                'deleted_count': deleted_count,
                'not_exist_codes': not_exist_codes,
                'remaining_items_count': len(cart.cart_items),
                'total_quantity': cart.get_total_items()
            })
        else:
            return Response({
                'code': 200,
                'message': f'所有{deleted_count}个商品从购物车删除成功',
                'deleted_count': deleted_count,
                'remaining_items_count': len(cart.cart_items),
                'total_quantity': cart.get_total_items()
            })
        
    except Exception as e:
        logger.error(f'删除购物车商品失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'删除购物车商品失败: {str(e)}'
        }, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def query_cart_items(request):
    """
    根据user_id查询购物车所有商品
    GET请求: user_id(查询参数)
    POST请求: user_id(请求体参数)
    返回：包含商品编码、数量和添加时间的商品列表，按添加时间倒序排列
    """
    # 同时支持GET和POST方法获取user_id
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
    else:  # POST
        user_id = request.data.get('user_id')
    try:
        
        # 验证参数
        if not user_id:
            return Response({
                'code': 400,
                'message': '参数错误：user_id不能为空'
            }, status=400)
        
        # 获取用户
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            logger.error(f'查询购物车商品失败: 用户ID {user_id} 不存在')
            return Response({
                'code': 404,
                'message': f'用户ID {user_id} 不存在'
            }, status=404)
        
        # 获取购物车，如果不存在则返回空列表
        try:
            cart = Cart.objects.get(user=user)
            
            # 按添加时间倒序排列商品
            sorted_items = sorted(
                cart.cart_items.items(),
                key=lambda x: datetime.strptime(x[1]['added_time'], '%Y-%m-%d %H:%M:%S'),
                reverse=True
            )
            
            # 构建包含数量信息的商品列表
            cart_items_list = []
            for item in sorted_items:
                code, details = item
                cart_items_list.append({
                    'commodity_code': code,
                    'quantity': details['quantity'],
                    'added_time': details['added_time']
                })
            
            # 计算总商品数量和总数量
            items_count = len(cart_items_list)
            total_quantity = cart.get_total_items()
            
        except Cart.DoesNotExist:
            cart_items_list = []
            items_count = 0
            total_quantity = 0
        
        return Response({
            'code': 200,
            'message': '查询成功',
            'data': {
                'cart_items': cart_items_list,
                'items_count': items_count,
                'total_quantity': total_quantity
            }
        })
        
    except Exception as e:
        logger.error(f'查询购物车商品失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'查询购物车商品失败: {str(e)}'
        }, status=500)


@api_view(['PUT', 'POST'])
@permission_classes([AllowAny])
def update_cart_item_quantity(request):
    """
    更新购物车中商品的数量
    请求体参数: user_id, commodity_code, quantity
    """
    try:
        user_id = request.data.get('user_id')
        commodity_code = request.data.get('commodity_code')
        quantity = request.data.get('quantity')
        
        # 验证参数
        if not user_id or not commodity_code or quantity is None:
            return Response({
                'code': 400,
                'message': '参数错误：user_id、commodity_code和quantity不能为空'
            }, status=400)
        
        # 验证数量参数
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("数量必须为正整数")
        except ValueError:
            return Response({
                'code': 400,
                'message': '参数错误：quantity必须为正整数'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取购物车
        cart = get_object_or_404(Cart, user=user)
        
        # 确保商品编码是字符串类型
        commodity_code_str = str(commodity_code)
        
        # 更新商品数量
        success = cart.update_quantity(commodity_code_str, quantity)
        
        if not success:
            return Response({
                'code': 404,
                'message': f'商品编码 {commodity_code_str} 不在购物车中'
            }, status=404)
        
        # 保存购物车更改
        cart.save()
        
        return Response({
            'code': 200,
            'message': '商品数量更新成功',
            'data': {
                'commodity_code': commodity_code_str,
                'quantity': quantity,
                'total_quantity': cart.get_total_items()
            }
        })
        
    except Exception as e:
        logger.error(f'更新购物车商品数量失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'更新购物车商品数量失败: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def increase_cart_item_quantity(request):
    """
    购物车商品数量增加指定值
    请求体参数: user_id, commodity_code, quantity(可选，默认为1)
    """
    try:
        user_id = request.data.get('user_id')
        commodity_code = request.data.get('commodity_code')
        quantity = request.data.get('quantity', 1)  # 默认为1
        
        # 验证参数
        if not user_id or not commodity_code:
            return Response({
                'code': 400,
                'message': '参数错误：user_id和commodity_code不能为空'
            }, status=400)
        
        # 验证quantity参数
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({
                'code': 400,
                'message': '参数错误：quantity必须是正整数'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取购物车
        cart = get_object_or_404(Cart, user=user)
        
        # 确保商品编码是字符串类型
        commodity_code_str = str(commodity_code)
        
        # 检查商品是否存在
        if commodity_code_str not in cart.cart_items:
            return Response({
                'code': 404,
                'message': f'商品编码 {commodity_code_str} 不在购物车中'
            }, status=404)
        
        # 数量增加指定值
        current_quantity = cart.cart_items[commodity_code_str]['quantity']
        new_quantity = current_quantity + quantity
        
        # 更新商品数量
        success = cart.update_quantity(commodity_code_str, new_quantity)
        
        if not success:
            return Response({
                'code': 500,
                'message': '更新商品数量失败'
            }, status=500)
        
        # 保存购物车更改
        cart.save()
        
        return Response({
            'code': 200,
            'message': f'商品数量增加{quantity}成功',
            'data': {
                'commodity_code': commodity_code_str,
                'quantity': new_quantity,
                'total_quantity': cart.get_total_items()
            }
        })
        
    except Exception as e:
        logger.error(f'增加购物车商品数量失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'增加购物车商品数量失败: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def decrease_cart_item_quantity(request):
    """
    购物车商品数量减1（不能减到0）
    请求体参数: user_id, commodity_code
    """
    try:
        user_id = request.data.get('user_id')
        commodity_code = request.data.get('commodity_code')
        
        # 验证参数
        if not user_id or not commodity_code:
            return Response({
                'code': 400,
                'message': '参数错误：user_id和commodity_code不能为空'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取购物车
        cart = get_object_or_404(Cart, user=user)
        
        # 确保商品编码是字符串类型
        commodity_code_str = str(commodity_code)
        
        # 检查商品是否存在
        if commodity_code_str not in cart.cart_items:
            return Response({
                'code': 404,
                'message': f'商品编码 {commodity_code_str} 不在购物车中'
            }, status=404)
        
        # 检查当前数量是否为1，不能减到0
        current_quantity = cart.cart_items[commodity_code_str]['quantity']
        if current_quantity <= 1:
            return Response({
                'code': 400,
                'message': '商品数量不能减到0，请使用删除功能',
                'data': {
                    'commodity_code': commodity_code_str,
                    'quantity': current_quantity
                }
            }, status=400)
        
        # 数量减1
        new_quantity = current_quantity - 1
        
        # 更新商品数量
        success = cart.update_quantity(commodity_code_str, new_quantity)
        
        if not success:
            return Response({
                'code': 500,
                'message': '更新商品数量失败'
            }, status=500)
        
        # 保存购物车更改
        cart.save()
        
        return Response({
            'code': 200,
            'message': '商品数量减1成功',
            'data': {
                'commodity_code': commodity_code_str,
                'quantity': new_quantity,
                'total_quantity': cart.get_total_items()
            }
        })
        
    except Exception as e:
        logger.error(f'减少购物车商品数量失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'减少购物车商品数量失败: {str(e)}'
        }, status=500)


@api_view(['DELETE', 'POST'])
@permission_classes([AllowAny])
def clear_cart(request):
    """
    清空购物车
    DELETE请求: user_id(查询参数)
    POST请求: user_id(请求体参数)
    """
    # 同时支持DELETE和POST方法获取user_id
    if request.method == 'DELETE':
        user_id = request.GET.get('user_id')
    else:  # POST
        user_id = request.data.get('user_id')
    try:
        
        # 验证参数
        if not user_id:
            return Response({
                'code': 400,
                'message': '参数错误：user_id不能为空'
            }, status=400)
        
        # 获取用户
        user = get_object_or_404(User, user_id=user_id)
        
        # 获取购物车
        cart = get_object_or_404(Cart, user=user)
        
        # 记录清空前的商品数量
        cleared_items_count = len(cart.cart_items)
        
        # 清空购物车
        cart.cart_items = {}
        cart.save()
        
        return Response({
            'code': 200,
            'message': f'购物车已清空，共清除{cleared_items_count}个商品',
            'data': {
                'cleared_items_count': cleared_items_count,
                'remaining_items_count': 0,
                'total_quantity': 0
            }
        })
        
    except Exception as e:
        logger.error(f'清空购物车失败: {str(e)}')
        return Response({
            'code': 500,
            'message': f'清空购物车失败: {str(e)}'
        }, status=500)