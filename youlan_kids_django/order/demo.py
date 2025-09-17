import requests
import json
import hashlib
import base64
import urllib.parse


def encrypt(content, api_key):
    """
    按照快递鸟API要求进行加密处理
    :param content: 需要加密的内容
    :param api_key: API密钥
    :return: 加密后的结果
    """
    # 将content和api_key拼接
    content_with_key = content + api_key
    
    # 进行MD5加密（32位小写）
    md5_hash = hashlib.md5(content_with_key.encode('utf-8'))
    md5_result = md5_hash.hexdigest()  # 已经是小写形式
    
    # 进行Base64编码
    base64_result = base64.b64encode(md5_result.encode('utf-8')).decode('utf-8')
    
    # 进行URL编码
    url_encoded_result = urllib.parse.quote(base64_result, safe='')
    
    return url_encoded_result


def get_kdniao_logistics(tracking_number):
    """
    发送请求到快递鸟API查询物流信息
    :param tracking_number: 快递单号
    :return: 格式化后的物流信息列表
    """
    # API配置信息
    url = 'https://api.kdniao.com/api/dist'
    e_business_id = '1894943'
    request_type = '8002'
    data_type = '2'
    api_key = 'bf425ddf-e9a9-487d-bcb6-b19868f5a275'
    
    # 构建请求数据
    request_data = {
        "LogisticCode": tracking_number
    }
    
    # 将请求数据转换为JSON字符串
    request_data_json = json.dumps(request_data)
    
    # 生成DataSign
    data_sign = encrypt(request_data_json, api_key)
    
    # 构建完整的请求体
    payload = {
        "RequestData": request_data_json,
        "EBusinessID": e_business_id,
        "RequestType": request_type,
        "DataType": data_type,
        "DataSign": data_sign
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, data=payload, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            # 尝试解析JSON响应
            try:
                result = response.json()
                
                # 检查请求是否成功
                if result.get('Success'):
                    # 提取并格式化物流信息
                    logistics_info = []
                    traces = result.get('Traces', [])
                    
                    for trace in traces:
                        logistics_item = {
                            'time': trace.get('AcceptTime', ''),
                            'location': trace.get('Location', ''),
                            'description': trace.get('AcceptStation', '')
                        }
                        logistics_info.append(logistics_item)
                    
                    # 返回完整结果和提取的物流信息
                    return {
                        'success': True,
                        'data': {
                            'logistics_info': logistics_info,
                            'shipper_code': result.get('ShipperCode', ''),
                            'logistic_code': result.get('LogisticCode', ''),
                            'location': result.get('Location', ''),
                            'state': result.get('State', ''),
                            'delivery_man_tel': result.get('DeliveryManTel', '')
                        }
                    }
                else:
                    # 请求失败，返回错误信息
                    reason = result.get('Reason', '未知错误')
                    return {
                        'success': False,
                        'message': f'查询失败: {reason}'
                    }
            except json.JSONDecodeError:
                # 如果响应不是有效的JSON格式，返回错误信息
                return {
                    'success': False,
                    'message': '响应格式不是有效的JSON',
                    'raw_response': response.text
                }
        else:
            return {
                'success': False,
                'message': f'请求失败，状态码: {response.status_code}',
                'raw_response': response.text
            }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'message': f'请求异常: {str(e)}'
        }


# 示例用法
if __name__ == "__main__":
    # 测试发送请求
    result = get_kdniao_logistics("773371781805082")
    print("API响应结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 如果成功，单独打印物流信息
    if result.get('success'):
        print("\n提取的物流信息:")
        logistics_info = result['data']['logistics_info']
        for item in logistics_info:
            print(f"时间: {item['time']}")
            print(f"地点: {item['location']}")
            print(f"描述: {item['description']}")
            print("-----")