from prometheus_client import start_http_server, Gauge
import requests
import time
import random

# 定义指标
custom_metric = Gauge('custom_metric', 'Description of custom metric', ['label1'])

def fetch_data():
    # 模拟从 API 获取数据
    # response = requests.get('https://api.example.com/data')
    # data = response.json()
    data = {'value': random.randint(0, 100)}
    custom_metric.labels(label1="example").set(data['value'])

if __name__ == '__main__':
    start_http_server(8000)  # 启动 Exporter 服务
    while True:
        fetch_data()
        time.sleep(10)  # 每 10 秒更新一次
