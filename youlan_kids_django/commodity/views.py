from dataclasses import field
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Commodity, CommoditySituation, CommodityImage, StyleCodeSituation
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError, transaction, models
import logging
import json
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 初始化审计日志
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger('audit')

@csrf_exempt
@require_http_methods("POST")
def batch_get_products_by_ids(request):  # 批量根据ID查询商品
    try:
        data = json.loads(request.body)
        commodity_ids = data.get('commodity_ids', [])
        fields = data.get('fields', [])  # 可选参数，指定返回字段

        if not commodity_ids or not isinstance(commodity_ids, list):
            return JsonResponse({'code': 400, 'message': '商品ID列表不能为空且必须是数组'}, status=400)

        # 批量查询商品
        commodities = Commodity.objects.filter(commodity_id__in=commodity_ids)

        # 构建响应数据
        result = []
        for commodity in commodities:
            # 先处理图片字段
            image_url = request.build_absolute_uri(commodity.image.url) if commodity.image else None
            promo_image_url = request.build_absolute_uri(commodity.promo_image.url) if commodity.promo_image else image_url
            
            commodity_data = {
                'commodity_id': commodity.commodity_id,
                'name': commodity.name,
                'style_code': commodity.style_code,
                'category': commodity.category,
                'price': commodity.price,
                'image': image_url,
                'promo_image': promo_image_url,
                'size': commodity.size,
                'color': commodity.color,
                'created_at': (commodity.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            }

            # 如果指定了返回字段，则只保留指定的字段
            if fields:
                commodity_data = {k: v for k, v in commodity_data.items() if k in fields}

            result.append(commodity_data)

        # 记录审计日志
        audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        audit_logger.info(f'BATCH_GET_BY_IDS|user:{audit_user}|ids:{commodity_ids}')

        return JsonResponse({
            'code': 200,
            'message': '查询成功',
            'data': result
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'批量查询商品失败: {str(e)}', exc_info=True)
        return JsonResponse({'code': 500, 'message': f'查询失败: {str(e)}'})


@csrf_exempt
@require_http_methods("POST")
def search_products_by_name(request):  # 根据名称搜索商品
    try:
        data = json.loads(request.body)
        search_str = data.get('search_str', '').strip()
        page = int(data.get('page', 1))  # 默认第一页
        page_size = int(data.get('page_size', 10))  # 默认每页10条
        
        if not search_str:
            return JsonResponse({'code': 400, 'message': '搜索字符串不能为空'}, status=400)
        
        # 搜索商品名称中包含搜索字符串的商品
        commodities_query = Commodity.objects.filter(name__icontains=search_str)
        
        # 计算总记录数和总页数
        total_count = commodities_query.count()
        pages = (total_count + page_size - 1) // page_size
        
        # 计算偏移量并获取当前页数据
        offset = (page - 1) * page_size
        commodities = commodities_query[offset:offset + page_size]
        
        # 构建响应数据
        result = []
        for commodity in commodities:
            commodity_data = {
                'commodity_id': commodity.commodity_id,
                'name': commodity.name,
                'style_code': commodity.style_code,
                'category': commodity.category,
                'price': commodity.price,
                'image': request.build_absolute_uri(commodity.image.url) if commodity.image else None,
                'promo_image': request.build_absolute_uri(commodity.promo_image.url) if commodity.promo_image else None,
                'created_at': (commodity.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            }
            result.append(commodity_data)
        
        # 记录审计日志
        audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        audit_logger.info(f'SEARCH_BY_NAME|user:{audit_user}|search_str:{search_str}|page:{page}|page_size:{page_size}')
        
        return JsonResponse({
            'code': 200,
            'message': '搜索成功',
            'data': {
                'list': result,
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'pages': pages
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'搜索商品失败: {str(e)}', exc_info=True)
        return JsonResponse({'code': 500, 'message': f'搜索失败: {str(e)}'})

@csrf_exempt
@require_http_methods("POST") 
def get_all_categories(request):   #获取所有商品类别

    try:
        # 解析请求体
        data = json.loads(request.body)
        # 验证shop参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({'code': 400, 'message': '无效的店铺名称'}, status=400)
        
        # 查询所有不重复的商品类别
        categories = Commodity.objects.values_list('category', flat=True).distinct().order_by('category')
        # 转换为列表
        category_list = list(categories)
        return JsonResponse({'code': 200, 'message': '查询成功', 'data': category_list})
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'查询类别失败: {str(e)}', exc_info=True)
        return JsonResponse({'code': 500, 'message': f'查询失败: {str(e)}'})

@csrf_exempt
@require_http_methods(['POST'])
def change_style_code_status_online(request):  #款式编码上线
    try:
        data = json.loads(request.body)
        style_code = data['style_code']
        
        # 更新StyleCodeSituation记录
        style_record, created = StyleCodeSituation.objects.get_or_create(style_code=style_code)
        style_record.status = 'online'
        style_record.online_time = timezone.now()
        style_record.save()
        
        # 更新所有拥有相同style_code的商品状态
        commodity_situations = CommoditySituation.objects.filter(style_code=style_code)
        count = commodity_situations.count()
        for situation in commodity_situations:
            situation.status = 'online'
            situation.online_time = timezone.now()
            situation.save()
        
        # 格式化上线时间为中国时区
        local_time = style_record.online_time + timedelta(hours=8)
        formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return JsonResponse({
            'status': 'success', 
            'online_time': formatted_time,
            'affected_commodities': count
        })
    except KeyError:
        return JsonResponse({'error': '缺少style_code参数'}, status=400)
    except Exception as e:
        logger.error(f'款式编码上线失败: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def change_style_code_status_offline(request):  #款式编码下线
    try:
        data = json.loads(request.body)
        style_code = data['style_code']
        
        # 更新StyleCodeSituation记录
        style_record, created = StyleCodeSituation.objects.get_or_create(style_code=style_code)
        style_record.status = 'offline'
        style_record.offline_time = timezone.now()
        style_record.save()
        
        # 更新所有拥有相同style_code的商品状态
        commodity_situations = CommoditySituation.objects.filter(style_code=style_code)
        count = commodity_situations.count()
        for situation in commodity_situations:
            situation.status = 'offline'
            situation.offline_time = timezone.now()
            situation.save()
        
        # 格式化下线时间为中国时区
        local_time = style_record.offline_time + timedelta(hours=8)
        formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return JsonResponse({
            'status': 'success', 
            'offline_time': formatted_time,
            'affected_commodities': count
        })
    except KeyError:
        return JsonResponse({'error': '缺少style_code参数'}, status=400)
    except Exception as e:
        logger.error(f'款式编码下线失败: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_goods(request):  #增加商品
    try:
        good_data = {}
        
        # 检查请求类型并解析数据
        if request.content_type.startswith('multipart/form-data'):
            # 处理表单数据和文件上传
            commodity_id = request.POST.get('commodity_id')
            name = request.POST.get('name')
            price = request.POST.get('price')
            category = request.POST.get('category')
            style_code = request.POST.get('style_code', '')
            size = request.POST.get('size', '')
            notes = request.POST.get('notes', '')
            
            # 处理图片上传
            image = request.FILES.get('image')
            promo_image = request.FILES.get('promo_image')
            # 获取多图片
            multiple_images = request.FILES.getlist('multiple_images')
            
            # 构造good_data字典
            good_data = {
                'commodity_id': commodity_id,
                'name': name,
                'price': price,
                'category': category,
                'style_code': style_code,
                'size': size,
                'notes': notes,
                'image': image,
                'promo_image': promo_image,
                'multiple_images': multiple_images
            }
        elif request.content_type == 'application/json':
            # 处理JSON请求
            try:
                good_data = json.loads(request.body.decode('utf-8'))
            except UnicodeDecodeError:
                logger.warning('请求体编码错误，请使用UTF-8编码')
                return JsonResponse({'code': 400, 'message': '请求体编码错误，请使用UTF-8编码'}, status=400)
            except json.JSONDecodeError:
                logger.warning('请求体不是有效的JSON格式')
                return JsonResponse({'code': 400, 'message': '请求体不是有效的JSON格式'}, status=400)
        else:
            logger.warning(f'不支持的请求类型: {request.content_type}')
            return JsonResponse({'code': 400, 'message': f'不支持的请求类型: {request.content_type}'}, status=400)
        
        # 参数校验（必需字段）
        required_fields = ['commodity_id', 'name', 'price', 'category']
        
        # 检查good_data是否存在且为字典
        if not isinstance(good_data, dict):
            logger.warning('请求数据格式错误')
            return JsonResponse({'code': 400, 'message': '请求数据格式错误'}, status=400)
        
        # 检查必填字段
        missing_fields = [field for field in required_fields if field not in good_data or not good_data[field]]
        
        if missing_fields:
            logger.warning(f'缺少必填字段: {missing_fields}')
            return JsonResponse({'code': 400, 'message': f'缺少必填字段: {missing_fields}'})
    except:
        return JsonResponse({'code':500,'message':'服务器错误'})
    missing_fields = [field for field in required_fields if field not in good_data]
    
    if missing_fields:
        logger.warning(f'缺少必填字段: {missing_fields}')
        return JsonResponse({'error': f'缺少必填字段: {", ".join(missing_fields)}'}, status=400)

    # 动态处理所有传入字段
    create_data = {
        'commodity_id': good_data['commodity_id'],
        'name': good_data['name'],
        'price': good_data['price'],
        'category': good_data.get('category', ''),
        'style_code': good_data.get('style_code', ''),
        'size': good_data.get('size', ''),
        'notes': good_data.get('notes', '')
    }

    # 处理图片上传
    if 'image' in good_data and good_data['image']:
        create_data['image'] = good_data['image']
    
    if 'promo_image' in good_data and good_data['promo_image']:
        create_data['promo_image'] = good_data['promo_image']

    # 提取多图片但不加入create_data，因为需要先创建商品
    multiple_images = good_data.get('multiple_images', [])

    # 合并其他可选参数
    create_data.update({
        k: v for k, v in good_data.items() 
        if k in [f.name for f in Commodity._meta.get_fields()]
        and k not in create_data
    })
    try:
        with transaction.atomic():
            # 创建商品对象
            new_commodity = Commodity(**create_data)
            # 保存商品
            new_commodity.save()
            
            # 处理多图片上传
            if multiple_images:
                # 如果有主图，先将其设置为非主图
                if hasattr(new_commodity, 'image') and new_commodity.image:
                    CommodityImage.objects.create(
                        commodity=new_commodity,
                        image=new_commodity.image,
                        is_main=True
                    )
                    # 清除主图，因为现在通过CommodityImage管理所有图片
                    new_commodity.image = None
                    new_commodity.save()
                
                # 保存所有图片
                for img in multiple_images:
                    is_main = len(CommodityImage.objects.filter(commodity=new_commodity, is_main=True)) == 0
                    CommodityImage.objects.create(
                        commodity=new_commodity,
                        image=img,
                        is_main=is_main
                    )
            elif hasattr(new_commodity, 'image') and new_commodity.image:
                # 只有单张主图的情况
                CommodityImage.objects.create(
                    commodity=new_commodity,
                    image=new_commodity.image,
                    is_main=True
                )
                # 清除主图
                new_commodity.image = None
                new_commodity.save()
            
            # 创建商品状态记录
            CommoditySituation.objects.create(
                commodity_id=new_commodity.commodity_id,
                status='pending'
            )
            
            logger.info(f'商品添加成功: {new_commodity.commodity_id}')
            return JsonResponse({
                'code': 200,
                'message': '添加成功', 
                'data': {
                    'commodity_id': new_commodity.commodity_id,
                    'image_count': CommodityImage.objects.filter(commodity=new_commodity).count()
                }
            })
    except Exception as e:
        logger.error(f'添加商品失败: {str(e)}')
        return JsonResponse({'code': 500, 'message': f'添加商品失败: {str(e)}'})
                

                # created_by=User.objects.get(username='system')
                
    except IntegrityError:
        return JsonResponse({'error': '商品ID已存在'}, status=409)
        
        return JsonResponse({'message':'商品添加成功','commodity_id': new_commodity.commodity_id})

    except Exception as e:
        logger.error(f'服务器异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)


@require_http_methods(['POST'])
@csrf_exempt
def delete_goods(request):  #删除商品 
    logger = logging.getLogger('audit')
    import os
    from django.conf import settings
    
    try:
        data = json.loads(request.body)
        commodity_id = data['commodity_id']
        
        with transaction.atomic():
            # 先获取商品对象和所有图片
            commodity = Commodity.objects.get(commodity_id=commodity_id)
            commodity_images = CommodityImage.objects.filter(commodity_id=commodity_id)
            
            # 删除主图文件
            if commodity.image:
                main_image_path = os.path.join(settings.MEDIA_ROOT, str(commodity.image))
                if os.path.exists(main_image_path):
                    os.remove(main_image_path)
                    logger.info(f'删除商品主图: {main_image_path}')
            
            # 删除推广图文件
            if commodity.promo_image:
                promo_image_path = os.path.join(settings.MEDIA_ROOT, str(commodity.promo_image))
                if os.path.exists(promo_image_path):
                    os.remove(promo_image_path)
                    logger.info(f'删除商品推广图: {promo_image_path}')
            
            # 删除多图片文件
            for img in commodity_images:
                if img.image:
                    image_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.info(f'删除商品图片: {image_path}')
            
            # 删除数据库记录
            commodity_images.delete()
            CommoditySituation.objects.filter(commodity_id=commodity_id).delete()
            commodity.delete()
            
            # 删除空文件夹
            commodity_dir = os.path.join(settings.MEDIA_ROOT, f'commodities/{commodity_id}')
            if os.path.exists(commodity_dir) and not os.listdir(commodity_dir):
                os.rmdir(commodity_dir)
                logger.info(f'删除空文件夹: {commodity_dir}')
        
        return JsonResponse({'status': 'success'})
    except KeyError:
        return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
    except Commodity.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'删除失败: {str(e)}'}, status=500)
    
        #     # 记录精简版审计日志
        #     audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        #     logger.info(f'DELETE|user:{audit_user}|commodity_id:{commodity_id}')
            
        #     return JsonResponse({'status': 'success', 'deleted_id': commodity_id},status=200)
            
        # except Commodity.DoesNotExist:
        #     return JsonResponse({'error': '商品不存在'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'删除操作异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def search_commodity_data(request):   #查询商品信息
    try:
        data = json.loads(request.body)
        commodity_id = data['commodity_id']
        data_list = data.get('data_list', [])

        # 获取商品对象
        commodity = Commodity.objects.get(commodity_id=commodity_id)
        
        # 构建响应数据
        result = {}
        for field in data_list:
            if hasattr(commodity, field):
                value = getattr(commodity, field)
                # 处理created_at字段，添加8小时并格式化
                if field == 'created_at' and isinstance(value, datetime):
                    # 添加8小时转换为中国时间
                    local_time = value + timedelta(hours=8)
                    # 格式化为YYYY-MM-DD HH:MM:SS
                    result[field] = local_time.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # 处理图片字段，返回完整URL
                    if field in ['image', 'promo_image']:
                        result[field] = request.build_absolute_uri(value.url) if value else None
                    else:
                        result[field] = value

        # 添加所有图片信息
        commodity_images = CommodityImage.objects.filter(commodity_id=commodity_id)
        images = []
        for img in commodity_images:
            image_info = {
                'id': img.id,
                'url': request.build_absolute_uri(img.image.url) if img.image else None,
                'is_main': img.is_main,
                'created_at': (img.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            }
            images.append(image_info)
        result['images'] = images
        
        # 添加主图和其他图片分类
        main_image = next((img for img in images if img['is_main']), None)
        other_images = [img for img in images if not img['is_main']]
        result['main_image'] = main_image
        result['other_images'] = other_images
        # 审计日志
        audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        audit_logger.info(f'SEARCH|user:{audit_user}|id:{commodity_id}|fields:{data_list}')

        return JsonResponse({'status': 'success', 'data': result})

    except KeyError:
        return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
    except Commodity.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'查询异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def change_commodity_data(request):  #修改商品信息
    try:
        data = json.loads(request.body)
        commodity_id = data['commodity_id']
        update_fields = {k: v for k, v in data.items() if k != 'commodity_id'}

        commodity = Commodity.objects.get(commodity_id=commodity_id)
        
        # 更新允许修改的字段
        for field, value in update_fields.items():
            if hasattr(commodity, field):
                setattr(commodity, field, value)
        
        commodity.save()

        # 审计日志
        audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        audit_logger.info(f'UPDATE|user:{audit_user}|id:{commodity_id}|fields:{list(update_fields.keys())}')

        return JsonResponse({'status': 'success', 'updated_fields': list(update_fields.keys())})

    except KeyError:
        return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
    except Commodity.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'修改异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)

@csrf_exempt
@require_http_methods(['POST'])
def change_commodity_status_online(request):  #商品上线
        try:
            data = json.loads(request.body)
            commodity_id = data['commodity_id']
            commodity = CommoditySituation.objects.get(commodity_id=commodity_id)
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            setattr(commodity, 'status' , 'online')
            # setattr(commodity, 'online_time' , time_now)
            setattr(commodity, 'online_time' , timezone.now())
            commodity.save()
            # 格式化上线时间为中国时区
            local_time = commodity.online_time + timedelta(hours=8)
            formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
            return JsonResponse({'status': 'success', 'online_time': formatted_time})
        except KeyError:
            return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
        except CommoditySituation.DoesNotExist:
            return JsonResponse({'error': '商品不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON格式'}, status=400)
        except Exception as e:
            logger.error(f'修改异常: {str(e)}', exc_info=True)
            return JsonResponse({'error': '服务器处理失败'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def change_commodity_status_offline(request):  #商品下线
        try:
            data = json.loads(request.body)
            commodity_id = data['commodity_id']
            commodity = CommoditySituation.objects.get(commodity_id=commodity_id)
            setattr(commodity, 'status' , 'offline')
            setattr(commodity, 'offline_time' , timezone.now())
            commodity.save()
            # 格式化下线时间为中国时区
            local_time = commodity.offline_time + timedelta(hours=8)
            formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S")
            return JsonResponse({'status': 'success', 'offline_time': formatted_time})
        except KeyError:
            return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
        except CommoditySituation.DoesNotExist:
            return JsonResponse({'error': '商品不存在'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON格式'}, status=400)
        except Exception as e:
            logger.error(f'修改异常: {str(e)}', exc_info=True)
            return JsonResponse({'error': '服务器处理失败'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def get_commodity_status(request):  #获取商品状态

    try:
        data = json.loads(request.body)
        commodity_id = data['commodity_id']
        commodity = CommoditySituation.objects.get(commodity_id=commodity_id)
        status_now = commodity.status
        response_data = {'status': status_now}
        
        # 根据状态返回对应时间
        if status_now == 'online' and commodity.online_time:
            local_time = commodity.online_time + timedelta(hours=8)
            response_data['online_time'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
        elif status_now == 'offline' and commodity.offline_time:
            local_time = commodity.offline_time + timedelta(hours=8)
            response_data['offline_time'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 状态既不是online也不是offline，返回空值
            response_data['online_time'] = ''
            response_data['offline_time'] = ''
        
        return JsonResponse(response_data, status=200)
    except KeyError:
        return JsonResponse({'error': '缺少commodity_id参数'}, status=400)
    except CommoditySituation.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)


@csrf_exempt
@require_http_methods(['POST'])
def get_commodities_by_style_code(request):
    try:
        data = json.loads(request.body)
        # 验证shopname参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({'error': '无效的店铺名称'}, status=400)
        
        # 获取style_code参数
        style_code = data.get('style_code')
        if not style_code:
            return JsonResponse({'error': '缺少style_code参数'}, status=400)
        
        # 查询该style_code下的所有商品
        commodities = Commodity.objects.filter(style_code=style_code)
        
        # 查询商品状态，只返回上线商品
        online_commodity_ids = CommoditySituation.objects.filter(
            status='online', 
            commodity_id__in=commodities.values_list('commodity_id', flat=True)
        ).values_list('commodity_id', flat=True)
        
        # 过滤出上线的商品
        commodities = commodities.filter(commodity_id__in=online_commodity_ids)
        
        # 构建响应数据
        result = {
            'name': '',
            'price': 0,
            'items': [],
            'images': [],
            'main_image': None,
            'other_images': []
        }
        
        # 创建颜色分组的字典
        color_groups = {}
        
        for i, commodity in enumerate(commodities):
            # 设置name和price（使用第一款商品的名称和价格）
            if i == 0:
                result['name'] = commodity.name
                result['price'] = commodity.price
                
                # 获取该商品的所有图片信息（作为style_code的图片组）
                commodity_images = CommodityImage.objects.filter(commodity=commodity)
                images = []
                for img in commodity_images:
                    image_info = {
                        'id': img.id,
                        'url': request.build_absolute_uri(img.image.url) if img.image else None,
                        'is_main': img.is_main,
                        'created_at': (img.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    }
                    images.append(image_info)
                
                # 如果没有从CommodityImage获取到图片，使用商品本身的图片作为备选
                if not images:
                    # 优先使用image字段
                    if commodity.image:
                        main_image_url = request.build_absolute_uri(commodity.image.url)
                        images.append({
                            'id': None,
                            'url': main_image_url,
                            'is_main': True,
                            'created_at': (commodity.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        })
                    # 再检查promo_image字段
                    elif commodity.promo_image:
                        promo_image_url = request.build_absolute_uri(commodity.promo_image.url)
                        images.append({
                            'id': None,
                            'url': promo_image_url,
                            'is_main': True,
                            'created_at': (commodity.created_at + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                        })
                
                result['images'] = images
                
                # 添加主图和其他图片分类
                main_image = next((img for img in images if img['is_main']), None)
                other_images = [img for img in images if not img['is_main']]
                result['main_image'] = main_image
                result['other_images'] = other_images
            
            # 获取color_image，如果为空则使用image
            color_image = request.build_absolute_uri(commodity.color_image.url) if hasattr(commodity, 'color_image') and commodity.color_image else None
            if not color_image and commodity.image:
                color_image = request.build_absolute_uri(commodity.image.url)
            
            # 按颜色分组
            color = commodity.color
            if color not in color_groups:
                # 新颜色，创建颜色组
                color_groups[color] = {
                    'color': color,
                    'color_image': color_image,
                    'sizes': []
                }
            
            # 添加尺码信息到颜色组
            color_groups[color]['sizes'].append({
                'commodity_id': commodity.commodity_id,
                'size': commodity.size
            })
        
        # 将颜色分组字典转换为列表格式
        result['items'] = list(color_groups.values())
        
        # 记录审计日志
        audit_user = request.user.username if request.user.is_authenticated else 'anonymous'
        audit_logger.info(f'GET_COMMODITIES_BY_STYLE_CODE|user:{audit_user}|style_code:{style_code}')
        
        return JsonResponse({
            'status': 'success',
            'data': result
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'根据款式编码查询商品失败: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def goods_query(request):   #
    try:
        data = json.loads(request.body)
        # 验证shopname参数
        if data.get('shopname') != 'youlan_kids':
            return JsonResponse({'error': '无效的店铺名称'}, status=400)
        
        # 获取demand参数
        demand = data.get('demand')
        
        # 如果指定了demand为style_code或goods，使用特定逻辑
        if demand in ['style_code', 'goods']:
            # 获取style_code和category参数
            style_code = data.get('style_code')
            category = data.get('category')
            
            # 只返回StyleCodeSituation中status为online的商品
            online_style_codes = StyleCodeSituation.objects.filter(status='online').values_list('style_code', flat=True)
            
            # 构建查询集
            commodities = Commodity.objects.filter(style_code__in=online_style_codes)
            
            # 如果demand不是style_code，但提供了style_code，进一步过滤
            if demand != 'style_code' and style_code:
                commodities = commodities.filter(style_code=style_code)
            
            # 如果提供了category，进一步过滤
            if category:
                if isinstance(category, list):
                    commodities = commodities.filter(category__in=category)
                else:
                    commodities = commodities.filter(category=category)
        else:
            # 原始逻辑：查询所有商品
            commodities = Commodity.objects.all().only('commodity_id', 'name', 'style_code', 'category', 'price', 'created_at')
        
        # 处理状态过滤
        status = data.get('status')
        if status:
            # 验证状态值是否有效
            valid_statuses = [choice[0] for choice in CommoditySituation.STATUS_CHOICES]
            if status not in valid_statuses:
                return JsonResponse({'error': '无效的状态值'}, status=400)
            
            # 获取符合状态的商品ID列表
            situation_ids = CommoditySituation.objects.filter(status=status).values_list('commodity_id', flat=True)
            commodities = commodities.filter(commodity_id__in=situation_ids)
        
        # 处理类目过滤
        category = data.get('category')
        if category and demand != 'style_code':  # style_code需求时不重复应用类目过滤
            # 支持单个类目或类目列表筛选
            if isinstance(category, list):
                commodities = commodities.filter(category__in=category)
            else:
                commodities = commodities.filter(category=category)
        
        # 处理分页参数
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        # 验证分页参数
        try:
            page = int(page)
            page_size = int(page_size)
            # 限制page_size最大值为50
            page_size = min(page_size, 50)
            # 确保页码和每页数量为正数
            page = max(page, 1)
            page_size = max(page_size, 1)
        except (ValueError, TypeError):
            return JsonResponse({'error': '无效的分页参数'}, status=400)
        
        # 对查询集进行排序
        commodities = commodities.order_by('-created_at')
        
        # 当demand为style_code时，相同的style_code只返回一条记录
        if demand == 'style_code':
            # 首先执行查询获取所有记录
            all_commodities = list(commodities)
            
            # 使用字典去重，确保每个style_code只保留一条最新记录
            unique_commodities = []
            seen_style_codes = set()
            
            for commodity in all_commodities:
                if commodity.style_code not in seen_style_codes:
                    seen_style_codes.add(commodity.style_code)
                    unique_commodities.append(commodity)
            
            # 将去重后的结果转换为一个自定义的分页器兼容对象
            from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
            
            # 手动处理分页
            total = len(unique_commodities)
            start = (page - 1) * page_size
            end = start + page_size
            
            # 获取当前页的数据
            current_page_commodities = unique_commodities[start:end]
            
            # 创建一个简单的对象来模拟查询集和分页结果
            class PaginationWrapper:
                def __init__(self, items, total, page, page_size):
                    self.object_list = items
                    self.number = page
                    self.paginator = type('Paginator', (), {
                        'count': total,
                        'num_pages': (total + page_size - 1) // page_size,
                        'page_size': page_size
                    })
                
                # 添加迭代方法，使PaginationWrapper对象可以被遍历
                def __iter__(self):
                    return iter(self.object_list)
            
            commodities_page = PaginationWrapper(current_page_commodities, total, page, page_size)
        else:
            # 创建分页器
            paginator = Paginator(commodities, page_size)
            
            try:
                commodities_page = paginator.page(page)
            except PageNotAnInteger:
                # 如果页码不是整数，返回第一页
                commodities_page = paginator.page(1)
            except EmptyPage:
                # 如果页码超出范围，返回最后一页
                commodities_page = paginator.page(paginator.num_pages)
        
        result = []
        for commodity in commodities_page:
            # 根据demand参数决定返回数据格式
            if demand in ['style_code', 'goods']:
                # 对于style_code或goods需求，只返回指定字段
                # 构建promo_image_url，当为空时使用image的值
                if commodity.promo_image:
                    promo_image_url = request.build_absolute_uri(commodity.promo_image.url)
                elif commodity.image:
                    promo_image_url = request.build_absolute_uri(commodity.image.url)
                else:
                    # 查找第一个主图作为备用
                    main_image = CommodityImage.objects.filter(commodity=commodity, is_main=True).first()
                    if main_image:
                        promo_image_url = request.build_absolute_uri(main_image.image.url)
                    else:
                        promo_image_url = None
                
                goods_data = {
                    'promo_image_url': promo_image_url,
                    'price': commodity.price,
                    'name': commodity.name,
                    'style_code': commodity.style_code
                }
            else:
                # 原始逻辑：返回所有字段
                # 处理添加时间(created_at)：加8小时并格式化
                created_time = commodity.created_at + timedelta(hours=8)
                formatted_time = created_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取商品的所有图片
                commodity_images = CommodityImage.objects.filter(commodity=commodity).order_by('created_at')
                
                # 构建图片URL列表
                image_urls = []
                for img in commodity_images:
                    image_urls.append({
                        'id': img.id,
                        'url': request.build_absolute_uri(img.image.url),
                        'is_main': img.is_main,
                        'created_at': img.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # 构建商品数据字典
                goods_data = {
                    'commodity_id': commodity.commodity_id,
                    'name': commodity.name,
                    'style': commodity.style_code,
                    'category': commodity.category,
                    'price': commodity.price,
                    'promo_image_url': request.build_absolute_uri(commodity.promo_image.url) if commodity.promo_image else None,
                    'images': image_urls,
                    'main_image': next((img for img in image_urls if img['is_main']), None),
                    'other_images': [img for img in image_urls if not img['is_main']],
                    'created_at': formatted_time
                }
            result.append(goods_data)
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'pagination': {
                'total': commodities_page.paginator.count,
                'page': commodities_page.number,
                'page_size': commodities_page.paginator.page_size,
                'pages': commodities_page.paginator.num_pages
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON格式'}, status=400)
    except Exception as e:
        logger.error(f'商品查询异常: {str(e)}', exc_info=True)
        return JsonResponse({'error': '服务器处理失败'}, status=500)


