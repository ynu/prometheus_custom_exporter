from prometheus_client import Gauge
import random

# 定义指标
custom_metric_2 = Gauge('custom_metric_2', 'Description of custom metric 2', ['label2'])

def process():
    print(f'custom_metric 2 is processing ...')
    """模拟获取数据并更新指标"""
    data = {'value': random.randint(0, 1000)}  # 示例数据
    custom_metric_2.labels(label2="example").set(data['value'])
