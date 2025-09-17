import os
import sys

# 首先设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')
import django
django.setup()

# 然后导入其他模块
import requests
import time
import hashlib
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
from commodity.models import Commodity

app_key = "e50a8f2e66c845c188a04f34ebf4a663"
app_select = 'b7a7e5df75ed4ae38c42db4fbe060fb8'
shop_id = 10162588

# 全局图片缓存字典，用于存储i_id对应的图片路径和MD5哈希值
# 确保在整个导入过程中都能重用已下载的图片
global_image_cache = {}


# 计算文件内容的MD5哈希值
def calculate_file_hash(file_path):
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败: {str(e)}")
        return None


# 计算内存中文件内容的MD5哈希值
def calculate_content_hash(content):
    try:
        return hashlib.md5(content).hexdigest()
    except Exception as e:
        print(f"计算内容哈希失败: {str(e)}")
        return None


# 检查文件系统中是否已存在相同内容的图片
def find_existing_image_by_content(image_content, style_code):
    try:
        # 计算内容哈希
        content_hash = calculate_content_hash(image_content)
        if not content_hash:
            return None
        
        # 构建目标目录路径
        if style_code:
            safe_style_code = ''.join(c for c in style_code if c.isalnum() or c in ['_', '-'])
            target_dir = os.path.join(settings.MEDIA_ROOT, 'commodities', safe_style_code)
        else:
            # 如果没有style_code，无法确定目标目录，返回None
            return None
        
        # 检查目录是否存在
        if not os.path.exists(target_dir):
            return None
        
        # 遍历目录中的所有文件，查找匹配的哈希值
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            if os.path.isfile(file_path):
                # 直接从文件名提取哈希值（如果文件名就是哈希值）
                base_name, _ = os.path.splitext(filename)
                if base_name == content_hash:
                    print(f"快速匹配到相同哈希值的文件: {filename}")
                    return os.path.join('commodities', safe_style_code, filename)
                
                # 如果文件名不是哈希值，计算文件内容哈希
                file_hash = calculate_file_hash(file_path)
                if file_hash == content_hash:
                    print(f"通过内容计算匹配到相同哈希值的文件: {filename}")
                    return os.path.join('commodities', safe_style_code, filename)
        
        return None
    except Exception as e:
        print(f"查找现有图片失败: {str(e)}")
        return None


# 保存图片时检查是否已存在相同内容的图片
def save_image_with_duplicate_check(commodity, image_path, image_name):
    try:
        # 设置临时图片路径属性，供models.py中的generate_unique_filename函数使用
        # 这是确保相同内容图片生成相同文件名的关键
        commodity._temp_image_path = image_path
        
        # 读取图片内容
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        # 检查文件系统中是否已存在相同内容的图片
        existing_image_path = find_existing_image_by_content(image_content, commodity.style_code)
        
        if existing_image_path:
            # 如果存在相同内容的图片，直接使用现有图片路径
            print(f"为商品 {commodity.commodity_id} 重用了已存在的相同内容图片: {existing_image_path}")
            # 构建完整的文件路径
            full_existing_path = os.path.join(settings.MEDIA_ROOT, existing_image_path)
            if os.path.exists(full_existing_path):
                # 使用现有文件创建ContentFile
                with open(full_existing_path, 'rb') as f:
                    # 注意：不需要重新计算文件名，直接使用现有文件名
                    # 这样可以确保文件系统中只保留一份相同内容的图片
                    existing_filename = os.path.basename(existing_image_path)
                    commodity.image.save(existing_filename, File(f), save=True)
                return True
        
        # 如果不存在相同内容的图片，保存新图片
        # 由于我们已经设置了_temp_image_path，generate_unique_filename会使用正确的文件内容计算哈希
        commodity.image.save(image_name, File(open(image_path, 'rb')), save=True)
        print(f"为商品 {commodity.commodity_id} 保存新图片")
        return True
    except Exception as e:
        print(f"保存图片失败: {str(e)}")
        return False


# 原有的md5_encrypt函数
def md5_encrypt(payment_str):
    # 进行MD5加密
    md5_hash = hashlib.md5()
    md5_hash.update(payment_str.encode('utf-8'))
    return md5_hash.hexdigest().lower()

# 原有的get_token函数
def get_token():
    app_key = "e50a8f2e66c845c188a04f34ebf4a663"
    timestamp = int(time.time())
    charset = "uft-8"
    app_select = 'b7a7e5df75ed4ae38c42db4fbe060fb8'
    grant_type = "authorization_code"
    code = "4xFIOC"
    converted_str = f'{app_select}app_key{app_key}charset{charset}code{code}grant_type{grant_type}timestamp{timestamp}'
    sign = md5_encrypt(converted_str)
    url = "https://openapi.jushuitan.com/openWeb/auth/getInitToken"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "app_key": app_key,
        "grant_type": grant_type,
        "timestamp": timestamp,
        "code": code,
        "charset": charset,
        "sign": sign
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()["data"]["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"请求发送失败: {str(e)}")
        return None

# 原有的send_inventory_query函数
def send_inventory_query(app_key, access_token, timestamp, charset, version, sign, biz):
    url = "https://openapi.jushuitan.com/open/skumap/query"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "app_key": app_key,
        "access_token": access_token,
        "timestamp": timestamp,
        "charset": charset,
        "version": version,
        "sign": sign,
        "biz": biz
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求发送失败: {str(e)}")
        return None


# 改进的download_image函数
def download_image(image_url, i_id=None):
    # 下载图片并返回临时文件路径
    try:
        # 检查URL是否有效
        if not image_url.startswith(('http://', 'https://')):
            print(f"无效的图片URL: {image_url}")
            return None, None
        
        # 如果有i_id，先检查是否已在全局缓存中
        if i_id and i_id in global_image_cache:
            cached_path, cached_name, _ = global_image_cache[i_id]
            if os.path.exists(cached_path):
                print(f"直接使用全局缓存中的图片，i_id: {i_id}")
                return cached_path, cached_name
        
        # 下载图片内容
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        # 立即读取图片内容以计算哈希值（不先保存到文件）
        image_content = response.content
        image_hash = calculate_content_hash(image_content)
        
        # 检查是否有相同哈希值的图片已经在缓存中
        for cached_i_id, (cached_path, cached_name, cached_hash) in global_image_cache.items():
            if cached_hash == image_hash and os.path.exists(cached_path):
                print(f"找到相同内容的图片，i_id: {cached_i_id}，直接重用")
                # 如果有i_id且尚未缓存，则将当前i_id映射到已存在的图片
                if i_id and i_id not in global_image_cache:
                    global_image_cache[i_id] = (cached_path, cached_name, cached_hash)
                return cached_path, cached_name
        
        # 创建临时文件名
        filename = os.path.basename(image_url).split('?')[0]
        
        # 如果有i_id，创建基于i_id的文件名
        if i_id:
            base_name, ext = os.path.splitext(filename)
            safe_i_id = ''.join(c for c in i_id if c.isalnum() or c in ['_', '-'])
            filename = f"{safe_i_id}{ext}"
        else:
            # 如果没有i_id，使用哈希值作为文件名
            base_name, ext = os.path.splitext(filename)
            filename = f"{image_hash}{ext}"
        
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', filename)
        
        # 确保临时目录存在
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        # 保存图片
        with open(temp_path, 'wb') as f:
            f.write(image_content)
                
        # 将图片信息添加到全局缓存
        if i_id:
            global_image_cache[i_id] = (temp_path, filename, image_hash)
            print(f"下载图片并添加到全局缓存，i_id: {i_id}")
        else:
            # 如果没有i_id，使用哈希值作为键
            global_image_cache[image_hash] = (temp_path, filename, image_hash)
            print(f"下载图片并添加到全局缓存，哈希值: {image_hash}")
            
        return temp_path, filename
    except Exception as e:
        print(f"图片下载失败: {str(e)}")
        return None, None


# 原有的split_date_range函数
from datetime import datetime, timedelta

def split_date_range(start_date_str, end_date_str, days_per_chunk=7):
    """将日期范围分割成多个不超过指定天数的子范围"""
    # 解析日期字符串为datetime对象
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    
    # 存储分割后的日期范围
    date_ranges = []
    
    # 当前处理的起始日期
    current_start = start_date
    
    # 循环分割日期范围
    while current_start < end_date:
        # 计算当前子范围的结束日期
        current_end = current_start + timedelta(days=days_per_chunk - 1)  # -1因为包含起始日
        
        # 如果计算出的结束日期超过了总的结束日期，则使用总的结束日期
        if current_end > end_date:
            current_end = end_date
        
        # 添加到结果列表中
        date_ranges.append((current_start.strftime("%Y-%m-%d %H:%M:%S"), 
                            current_end.strftime("%Y-%m-%d %H:%M:%S")))
        
        # 移动到下一个子范围的起始日期
        current_start = current_end + timedelta(seconds=1)
    
    return date_ranges

# 改进的import_data_for_date_range函数
def import_data_for_date_range(access_token, modified_begin, modified_end):
    """为指定的日期范围导入商品数据"""
    # 初始化分页参数
    page_index = 1
    has_next = True
    imported_count = 0
    
    # 分页查询并导入数据
    while has_next:
        print(f"正在查询日期范围 [{modified_begin} 至 {modified_end}] 的第 {page_index} 页数据...")
        
        # 获取当前时间戳
        timestamp = int(time.time())
        
        # 构建请求参数
        charset = "UTF-8"
        version = 2
        biz = f'{{"page_index":"{page_index}","page_size":"100","modified_begin":"{modified_begin}","modified_end":"{modified_end}","shop_id":"{shop_id}"}}'
        
        # 生成签名
        converted_str = f'{app_select}access_token{access_token}app_key{app_key}biz{biz}charset{charset}timestamp{timestamp}version{version}'
        sign = md5_encrypt(converted_str)
        
        # 发送请求
        response = send_inventory_query(app_key, access_token, timestamp, charset, version, sign, biz)
        
        if not response or response.get('code') != 0:
            print(f"请求失败或返回异常: {response}")
            break
            
        # 处理返回数据
        data = response.get('data')
        if not data:
            print("没有返回数据")
            break
            
        # 导入商品数据
        datas = data.get('datas', [])
        if datas:
            print(f"正在导入第 {page_index} 页的 {len(datas)} 条数据...")
            
            for item in datas:
                try:
                    # 解析properties_value获取颜色和身高
                    properties_value = item.get('properties_value', '')
                    i_id = item.get('i_id', '')
                    color = ''
                    height = ''
                    if properties_value:
                        props = [p.strip() for p in properties_value.split(',') if p.strip()]
                        if len(props) >= 1:
                            color = props[0]
                        if len(props) >= 2:
                            height = props[1]
                    
                    # 检查商品是否已存在（使用sku_id作为唯一标识）
                    sku_id = item.get('sku_id')
                    if not sku_id:
                        continue
                    
                    # 下载图片 - 使用全局缓存，检查i_id是否已有缓存的图片
                    pic_url = item.get('pic')
                    image_path = None
                    image_name = None
                    
                    if pic_url and i_id:
                        # 如果i_id在全局缓存中，直接使用缓存的图片路径
                        if i_id in global_image_cache:
                            image_path, image_name, _ = global_image_cache[i_id]
                            print(f"使用全局缓存的图片，i_id: {i_id}")
                        else:
                            # 如果缓存中没有，下载图片并加入全局缓存
                            image_path, image_name = download_image(pic_url, i_id)
                            # 图片已经通过download_image函数添加到全局缓存
                            pass
                    
                    # 创建或更新商品，使用commodity_id作为主键
                    commodity_id = item.get('raw_sku_id', '')
                    if not commodity_id:
                        print(f"跳过无commodity_id的商品: {item}")
                        continue
                    
                    # 确保style_code格式统一（去掉可能的特殊字符）
                    safe_style_code = ''.join(c for c in i_id if c.isalnum() or c in ['_', '-'])
                    
                    defaults = {
                        'name': item.get('name', ''),
                        'style_code': safe_style_code,  # 使用统一格式的style_code
                        'category': '',  # 临时设置，根据实际情况调整
                        'category_detail': '',  # 按要求先传空
                        'price': 0.0,  # 默认价格，实际应从接口获取
                        'color': color,
                        'height': height,
                        'size': height,  # 暂时用height作为size
                    }
                    
                    try:
                        commodity = Commodity.objects.get(commodity_id=commodity_id)
                        created = False
                        # 更新现有商品
                        for key, value in defaults.items():
                            setattr(commodity, key, value)
                    except Commodity.DoesNotExist:
                        # 检查是否已有相同style_code的商品，如果有则重用图片
                        existing_commodity = Commodity.objects.filter(style_code=safe_style_code).first()
                        if existing_commodity and existing_commodity.image:
                            # 创建新商品但重用现有图片路径
                            commodity = Commodity(commodity_id=commodity_id, **defaults)
                            # 直接设置image字段为现有图片路径
                            commodity.image = existing_commodity.image
                            print(f"为商品 {commodity_id} 重用相同style_code {safe_style_code} 的现有图片")
                            created = True
                        else:
                            # 创建新商品
                            commodity = Commodity(commodity_id=commodity_id, **defaults)
                            created = True
                    
                    # 保存商品
                    try:
                        print(f"准备保存商品，ID类型: {type(commodity_id)}, ID值: {commodity_id}")
                        commodity.save()
                        print(f"商品 {commodity_id} 保存成功")
                    except Exception as e:
                        print(f"保存商品失败: {str(e)}, 商品ID: {commodity_id}")
                        # 打印详细的错误信息和商品数据类型
                        import traceback
                        traceback.print_exc()
                        print(f"commodity对象类型: {type(commodity)}")
                        print(f"commodity_id字段类型: {type(commodity.commodity_id)}")
                        continue
                    
                    # 只有在新创建的商品且没有重用现有图片的情况下，才需要保存新图片
                    if created and image_path and image_name and not (hasattr(commodity, 'image') and commodity.image):
                        save_image_with_duplicate_check(commodity, image_path, image_name)
                    elif created and image_path and image_name:
                        print(f"商品 {commodity_id} 已通过style_code重用了图片，无需保存新图片")
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"导入商品失败: {str(e)}, 商品信息: {item}")
                    continue
            
            # 注意：这里不再立即删除临时图片文件，而是在处理完所有商品后再删除
            
        else:
            print(f"第 {page_index} 页没有数据")
            
        # 更新分页信息
        has_next = data.get('has_next', False)
        page_index += 1
        
        # 避免请求过于频繁
        time.sleep(1)
    
        return imported_count

# 原有的import_commodity_data和主函数部分
def import_commodity_data():
    # 获取访问令牌
    access_token = get_token()
    if not access_token:
        print("无法获取访问令牌")
        return
        
    # 设置日期范围：2025-08-20 到 2025-09-13
    modified_begin = "2025-08-20 00:00:00"
    modified_end = "2025-09-13 23:59:59"
    
    # 分割日期范围以符合API的7天限制
    date_ranges = split_date_range(modified_begin, modified_end, days_per_chunk=7)
    print(f"日期范围已分割为 {len(date_ranges)} 个子范围")
    
    total_imported = 0
    
    # 对每个子范围导入数据
    for i, (start, end) in enumerate(date_ranges, 1):
        print(f"正在处理第 {i}/{len(date_ranges)} 个子范围: {start} 至 {end}")
        imported_count = import_data_for_date_range(access_token, start, end)
        total_imported += imported_count
        print(f"子范围 {i} 导入完成，导入了 {imported_count} 条数据")
        
        # 子范围之间也添加延迟，避免请求过于频繁
        if i < len(date_ranges):
            time.sleep(2)
    
        print(f"数据导入完成，共导入 {total_imported} 条商品数据")
    
    # 最后清理临时图片文件并清空全局缓存
    print(f"开始清理全局缓存中的临时图片文件，共 {len(global_image_cache)} 个")
    for image_path, _, _ in global_image_cache.values():
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"清理临时图片失败: {str(e)}")
    
    # 清空全局缓存
    global_image_cache.clear()


if __name__ == '__main__':
    import_commodity_data()

