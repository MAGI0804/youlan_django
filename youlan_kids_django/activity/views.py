from django.shortcuts import render

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ActivityImage
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta
from commodity.models import Commodity
from datetime import datetime
@csrf_exempt
def add_activity_img(request):      #添加活动图
    if request.method == 'POST':
        try:
            # 获取表单数据
            category = request.POST.get('category', '')
            notes = request.POST.get('notes', '')
            commodities = request.POST.get('commodities', '')

            # 处理文件上传
            image = request.FILES.get('image')

            # 创建活动图对象，状态默认为'pending'
            activity_img = ActivityImage(
                status='pending',
                category=category,
                notes=notes,
                commodities=commodities
            )

            # 保存图片
            if image:
                activity_img.image = image

            activity_img.save()

            return JsonResponse({'code': 200, 'message': '添加成功', 'data': {'id': activity_img.id}})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'添加失败: {str(e)}'})
    else:
        return JsonResponse({'code': 405, 'message': '不支持的请求方法'})

@csrf_exempt
def activity_image_online(request):    #上线活动图
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            activity_id = data.get('activity_id')
            # 自动使用当前时间作为上线时间
            online_time = datetime.now()

            # 验证活动图是否存在
            try:
                activity_img = ActivityImage.objects.get(id=activity_id)
            except ActivityImage.DoesNotExist:
                return JsonResponse({'code': 404, 'message': '活动图不存在'})

            # 检查关联商品数量
            commodities = activity_img.commodities
            if commodities:
                commodity_ids = [id.strip() for id in commodities.split(',') if id.strip()]
                if len(commodity_ids) > 5:
                    return JsonResponse({'code': 400, 'message': '上线失败：活动图关联商品数量不能超过5个'})

            # 检查已上线活动图数量
            online_count = ActivityImage.objects.filter(status='online').count()
            # 如果当前活动图不是已上线状态，且已上线数量已达5，则不允许上线
            if activity_img.status != 'online' and online_count >= 5:
                return JsonResponse({'code': 400, 'message': '上线失败：最多只能上线5张活动图'})

            # 更新活动图状态和上线时间
            activity_img.status = 'online'
            activity_img.online_time = online_time
            activity_img.save()

            return JsonResponse({'code': 200, 'message': '上线成功', 'data': {'id': activity_img.id}})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'上线失败: {str(e)}'})
    else:
        return JsonResponse({'code': 405, 'message': '不支持的请求方法'})

@csrf_exempt
def batch_query_activity_images(request):    #批量查询
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            shopname = data.get('shopname')

            # 验证shopname
            if shopname != 'youlan_kids':
                return JsonResponse({'code': 400, 'message': 'shopname不正确'})

            # 查询所有活动图
            activity_images = ActivityImage.objects.all()
            result = []

            for img in activity_images:
                # 处理时间字段，增加8小时并格式化
                online_time = (img.online_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') if img.online_time else None
                offline_time = (img.offline_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S') if img.offline_time else None
                created_at = (img.created_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                updated_at = (img.updated_at + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')

                # 构建返回数据
                img_data = {
                    'id': img.id,
                    'image': request.build_absolute_uri(img.image.url) if img.image else None,
                    'status': img.status,
                    'online_time': online_time,
                    'offline_time': offline_time,
                    'commodities': img.commodities,
                    'category': img.category,
                    'notes': img.notes,
                    'created_at': created_at,
                    'updated_at': updated_at
                }
                result.append(img_data)

            return JsonResponse({'code': 200, 'message': '查询成功', 'data': result})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'查询失败: {str(e)}'})
    else:
        return JsonResponse({'code': 405, 'message': '不支持的请求方法'})

@csrf_exempt
def activity_image_offline(request):     #下线活动图
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            activity_id = data.get('activity_id')
            # 自动使用当前时间作为下线时间
            offline_time = datetime.now()

            # 验证活动图是否存在
            try:
                activity_img = ActivityImage.objects.get(id=activity_id)
            except ActivityImage.DoesNotExist:
                return JsonResponse({'code': 404, 'message': '活动图不存在'})

            # 更新活动图状态和下线时间
            activity_img.status = 'offline'
            activity_img.offline_time = offline_time
            activity_img.save()

            return JsonResponse({'code': 200, 'message': '下线成功', 'data': {'id': activity_img.id}})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'下线失败: {str(e)}'})
    else:
        return JsonResponse({'code': 405, 'message': '不支持的请求方法'})

@csrf_exempt
def update_activity_image_relations(request):     #修改关联信息
    if request.method == 'POST':
        try:
            # 获取请求数据
            data = json.loads(request.body)
            activity_id = data.get('activity_id')
            commodities = data.get('commodities', '')
            category = data.get('category', '')

            # 验证活动图是否存在
            try:
                activity_img = ActivityImage.objects.get(id=activity_id)
            except ActivityImage.DoesNotExist:
                return JsonResponse({'code': 404, 'message': '活动图不存在'})

            # 验证商品ID是否存在于commodity应用中
            if commodities:
                commodity_ids = [id.strip() for id in commodities.split(',') if id.strip()]
                invalid_ids = []
                for cid in commodity_ids:
                    try:
                        # 尝试将cid转换为整数
                        cid_int = int(cid)
                        # 检查商品是否存在
                        if not Commodity.objects.filter(commodity_id=cid_int).exists():
                            invalid_ids.append(cid)
                    except ValueError:
                        invalid_ids.append(cid)

                if invalid_ids:
                    return JsonResponse({'code': 400, 'message': f'无效的商品ID: {invalid_ids}'})

            # 更新活动图信息
            activity_img.category = category
            activity_img.commodities = commodities
            activity_img.save()

            return JsonResponse({'code': 200, 'message': '更新成功', 'data': {'id': activity_img.id}})
        except Exception as e:
            return JsonResponse({'code': 500, 'message': f'更新失败: {str(e)}'})
    else:
        return JsonResponse({'code': 405, 'message': '不支持的请求方法'})
