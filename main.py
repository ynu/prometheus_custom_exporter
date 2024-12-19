import importlib
import time
import random
import threading
import multiprocessing
from prometheus_client import start_http_server, Gauge
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import sys

# 用于动态加载和重新加载 metrics 目录下的脚本
metrics_directory = 'metrics'
loaded_metrics = {}

# 用于多线程/多进程同步访问 loaded_metrics
lock = threading.Lock()

def load_metric_modules():
    """加载 metrics 目录下的所有模块"""
    global loaded_metrics  # Declare loaded_metrics as global to modify it
    
    # 获取当前 metrics 目录下所有的文件名
    current_files = set(os.listdir(metrics_directory))

    print(f"load_metric_modules, loaded_metrics: {loaded_metrics}, current_files: {current_files}")
    # 移除不再存在的文件
    to_remove = [metric_name for metric_name in loaded_metrics if f"{metric_name}.py" not in current_files]
    with lock:  # 使用锁来确保对 shared state (loaded_metrics) 的同步访问
        for metric_name in to_remove:
            # 卸载模块
            del loaded_metrics[metric_name]
            print(f"Module {metric_name} removed, loaded_metrics: {loaded_metrics}")

    # 加载新的模块
    for filename in current_files:
        if filename.endswith(".py") and filename != '__init__.py':
            module_name = filename[:-3]  # 去掉 '.py' 后缀
            if module_name not in loaded_metrics:
                try:
                    # 动态导入模块
                    module = importlib.import_module(f'metrics.{module_name}')
                    loaded_metrics[module_name] = module
                    print(f"Module {module_name} loaded, loaded_metrics: {loaded_metrics}")
                    # 确保新模块被执行
                    if hasattr(module, 'process'):
                        print(f"Processing {module_name}")
                        module.process()  # 执行新的模块的 `process` 方法
                except Exception as e:
                    print(f"Error loading {module_name}: {e}")
            # else:
            #     # 如果模块已经加载，强制重新加载并执行 `process` 方法
            #     try:
            #         print(f"Reloading module {module_name}")
            #         importlib.reload(loaded_metrics[module_name])  # 强制重新加载模块
            #         module = loaded_metrics[module_name]
            #         if hasattr(module, 'process'):
            #             print(f"Processing {module_name}")
            #             module.process()  # 执行 `process` 方法
            #     except Exception as e:
            #         print(f"Error reloading {module_name}: {e}")

def process_metrics():
    """处理所有加载的指标"""
    global loaded_metrics  # Declare loaded_metrics as global to access the updated version
    with lock:  # 使用锁来确保对 shared state (loaded_metrics) 的同步访问
        for metric_name, metric_module in loaded_metrics.items():
            try:
                if hasattr(metric_module, 'process'):
                    print(f"Processing {metric_name}")
                    metric_module.process()  # 调用 process 方法
            except Exception as e:
                print(f"Error processing {metric_name}: {e}")

class metricFileEventHandler(FileSystemEventHandler):
    """自定义事件处理器，用于处理文件增加、删除、修改"""
    
    def on_created(self, event):
        """当文件被创建时，加载模块"""
        if event.src_path.endswith(".py"):
            print(f"Detected new file: {event.src_path}, loading...")
            load_metric_modules()

    def on_deleted(self, event):
        """当文件被删除时，卸载模块"""
        if event.src_path.endswith(".py"):
            print(f"Detected deleted file: {event.src_path}, reloading...")
            load_metric_modules()

    # def on_modified(self, event):
    #     """当文件被修改时，重新加载模块"""
    #     if event.src_path.endswith(".py"):
    #         print(f"Detected modified file: {event.src_path}, reloading...")
    #         load_metric_modules()

def watch_metrics_directory():
    """监听 metrics 目录下文件的变化，动态更新指标"""
    event_handler = metricFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, metrics_directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start_metrics_server():
    """启动 Prometheus HTTP 服务器"""
    start_http_server(8000)

# def watch_metrics_directory_process():
#     """启动一个单独的进程来监听文件变化"""
#     process = multiprocessing.Process(target=watch_metrics_directory)
#     process.daemon = True  # 守护进程，在主进程退出时自动结束
#     process.start()

# if __name__ == '__main__':
#     load_metric_modules()  # 加载初始模块
#     start_metrics_server()  # 启动 Exporter 服务

#     # 启动监听文件变化的进程
#     watch_metrics_directory_process()

#     while True:
#         process_metrics()  # 处理所有加载的指标
#         time.sleep(10)  # 每 10 秒更新一次

def watch_metrics_directory_thread(loaded_metrics):
    """启动一个单独的线程来监听文件变化"""
    thread = threading.Thread(target=watch_metrics_directory)
    thread.daemon = True  # 守护线程，在主线程退出时自动结束
    thread.start()

if __name__ == '__main__':
    # 使用 threading.Lock 来避免多个线程之间的同步问题
    with threading.Lock():

        load_metric_modules()  # 加载初始模块
        start_metrics_server()  # 启动 Exporter 服务

        # 启动监听文件变化的线程
        watch_metrics_directory_thread(loaded_metrics)

        while True:
            process_metrics()  # 处理所有加载的指标
            time.sleep(10)  # 每 10 秒更新一次
