import sys
import os

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youlan_kids_django.settings')
import django
django.setup()

# 导入模型
from commodity.models import Commodity

# 测试函数
def test_commodity_id():
    # 准备测试数据
    test_id = 'C36G3028FR725100'  # 一个典型的字符串类型商品ID
    
    print(f"开始测试字符串类型的commodity_id: {test_id}")
    
    # 尝试创建一个新商品
    try:
        # 先删除可能存在的测试数据
        Commodity.objects.filter(commodity_id=test_id).delete()
        
        # 创建新商品
        commodity = Commodity(
            commodity_id=test_id,
            name='测试商品',
            style_code='TEST',
            category='测试类目',
            price=99.99
        )
        
        # 打印类型信息
        print(f"商品对象类型: {type(commodity)}")
        print(f"commodity_id字段类型: {type(commodity.commodity_id)}")
        print(f"字符串类型确认: {isinstance(commodity.commodity_id, str)}")
        
        # 尝试保存
        commodity.save()
        print(f"商品保存成功，ID: {test_id}")
        
        # 验证保存是否成功
        saved_commodity = Commodity.objects.get(commodity_id=test_id)
        print(f"成功获取保存的商品，ID: {saved_commodity.commodity_id}")
        print("测试通过!")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_commodity_id()