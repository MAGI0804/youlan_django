import sys
import os
import sys
import requests,time,hashlib

# 设置Django环境 - 确保从项目根目录运行
# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（youlan_kids_django）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径
sys.path.append(project_root)
# 设置Django设置模块
sys.path.append(os.path.dirname(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')

# 导入Django
import django
django.setup()

# 导入Django模型
from commodity.models import Commodity
from tests import get_token

app_key = "e50a8f2e66c845c188a04f34ebf4a663"
access_token = get_token()
timestamp = int(time.time())
print(timestamp)
charset = "UTF-8"
version = 2
app_select = 'b7a7e5df75ed4ae38c42db4fbe060fb8'
wms_co_id = 12740959


def md5_encrypt(payment_str):   #进行MD5加密
    md5_hash = hashlib.md5()
    md5_hash.update(payment_str.encode('utf-8'))
    return md5_hash.hexdigest().lower()

def send_inventory_query(app_key,access_token,timestamp,charset,version,sign,biz):
    url = "https://openapi.jushuitan.com/open/sku/query"
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
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求发送失败: {str(e)}")
        return None


def get_commodity_ids():
    """从Commodity模型中获取所有commodity_id"""
    try:
        # 查询所有商品的commodity_id
        commodities = Commodity.objects.values_list('commodity_id', flat=True)
        return list(commodities)
    except Exception as e:
        print(f"获取商品ID失败: {str(e)}")
        return []


def batch_process_commodities():
    """批量处理商品数据，每20个ID一组"""
    # 获取所有商品ID
    all_commodity_ids = get_commodity_ids()
    if not all_commodity_ids:
        print("没有找到商品ID")
        return
    
    print(f"总共找到 {len(all_commodity_ids)} 个商品ID")
    
    # 分批处理，每20个ID一组
    batch_size = 20
    for i in range(0, len(all_commodity_ids), batch_size):
        # 获取当前批次的ID
        batch_ids = all_commodity_ids[i:i+batch_size]
        sku_ids = ",".join(batch_ids)
        
        print(f"处理批次 {i//batch_size + 1}，包含 {len(batch_ids)} 个商品ID")
        
        # 调用API查询这批商品
        result = process_commodity_batch(sku_ids)
        
        # 如果处理失败，打印错误信息
        if not result:
            print(f"批次 {i//batch_size + 1} 处理失败")
        
        # 避免请求过于频繁
        time.sleep(1)


def process_commodity_batch(sku_ids):
    """处理一批商品ID，调用API并更新数据库，同时删除查不到数据的商品"""
    try:
        # 保存当前批次的所有商品ID列表
        batch_id_list = sku_ids.split(',')
        
        # 构建请求参数
        timestamp = int(time.time())
        biz = f'{{"page_index":"1","page_size":"100","sku_ids":"{sku_ids}"}}'
        converted_str = f'{app_select}access_token{access_token}app_key{app_key}biz{biz}charset{charset}timestamp{timestamp}version{version}'
        sign = md5_encrypt(converted_str)
        
        # 发送请求
        response = send_inventory_query(app_key, access_token, timestamp, charset, version, sign, biz)
        
        if not response or response.get('code') != 0:
            print(f"API请求失败或返回异常: {response}")
            # API失败时，删除当前批次的所有商品
            delete_commodities_not_found(batch_id_list, [])
            return False
        
        # 处理返回的数据
        data = response.get('data')
        if not data:
            print("API返回数据为空")
            # 数据为空时，删除当前批次的所有商品
            delete_commodities_not_found(batch_id_list, [])
            return False
        
        datas = data.get('datas', [])
        
        # 获取在API响应中找到的商品ID
        found_ids = [item.get('sku_id') for item in datas if item.get('sku_id')]
        
        # 删除在API响应中找不到的商品
        delete_commodities_not_found(batch_id_list, found_ids)
        
        # 如果有找到的数据，更新数据库
        if datas:
            update_commodity_data(datas)
        
        return True
    except Exception as e:
        print(f"处理商品批次失败: {str(e)}")
        # 异常情况下，也删除当前批次的所有商品
        try:
            batch_id_list = sku_ids.split(',')
            delete_commodities_not_found(batch_id_list, [])
        except:
            pass
        return False

def delete_commodities_not_found(batch_id_list, found_ids):
    """删除在API响应中找不到的商品记录"""
    # 找出在批次中但不在API响应中的商品ID
    not_found_ids = [sku_id for sku_id in batch_id_list if sku_id not in found_ids]
    
    if not not_found_ids:
        return
    
    # 删除这些商品记录
    deleted_count = Commodity.objects.filter(commodity_id__in=not_found_ids).delete()[0]
    
    if deleted_count > 0:
        print(f"删除了 {deleted_count} 个在API中找不到数据的商品记录")
    else:
        print(f"没有需要删除的商品记录")


def update_commodity_data(datas):
    """根据API返回的数据更新Commodity模型"""
    for item in datas:
        try:
            # 获取商品ID
            sku_id = item.get('sku_id')
            if not sku_id:
                continue
            
            # 根据用户需求，检查必要字段是否存在
            category = item.get('other_6')
            category_detail = item.get('vc_name')
            price = item.get('sale_price')
            
            # 尝试获取商品记录
            commodity = Commodity.objects.get(commodity_id=sku_id)
            
            # 检查必要字段是否存在，如果不存在则删除记录
            if category is None or category_detail is None or price is None:
                print(f"必要字段缺失，删除商品记录: {sku_id}")
                commodity.delete()
                continue
            
            # 更新商品信息
            commodity.category = category
            commodity.category_detail = category_detail
            commodity.price = price
            commodity.save()
            
            print(f"更新商品成功: {sku_id}, category: {category}, category_detail: {category_detail}, price: {price}")
        except Commodity.DoesNotExist:
            print(f"商品不存在: {sku_id}")
        except Exception as e:
            print(f"处理商品失败: {sku_id}, 错误: {str(e)}")


if __name__ == '__main__':
    # 开始批量处理商品
    batch_process_commodities()

