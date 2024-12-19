from prometheus_client import Gauge
import random

# 定义指标
custom_metric_1 = Gauge('custom_metric_1', 'Description of custom metric', ['label1'])

def process():
    print(f'custom_metric 1 is processing ...')
    """模拟获取数据并更新指标"""
    data = {'value': random.randint(0, 100)}  # 示例数据
    custom_metric_1.labels(label1="example").set(data['value'])
