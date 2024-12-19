import importlib
import time
import random
import os
import sys
import asyncio
from prometheus_client import start_http_server, Gauge
import inspect
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 用于动态加载和重新加载 metrics 目录下的脚本
metrics_directory = 'metrics'
loaded_metrics = {}

# 用于协程同步访问 loaded_metrics
lock = asyncio.Lock()

async def load_metric_modules():
    """加载 metrics 目录下的所有模块"""
    global loaded_metrics  # Declare loaded_metrics as global to modify it
    
    # 获取当前 metrics 目录下所有的文件名
    current_files = set(os.listdir(metrics_directory))

    print(f"load_metric_modules, loaded_metrics: {loaded_metrics}, current_files: {current_files}")
    # 移除不再存在的文件
    to_remove = [metric_name for metric_name in loaded_metrics if f"{metric_name}.py" not in current_files]
    async with lock:  # 使用锁来确保对 shared state (loaded_metrics) 的同步访问
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
                        # 检查 process 是否为协程函数
                        if inspect.iscoroutinefunction(module.process):
                            await module.process()  # 执行新的模块的 `process` 方法 (如果是协程)
                        else:
                            module.process()  # 如果不是协程，则直接调用
                except Exception as e:
                    print(f"Error loading {module_name}: {e}")

async def process_metrics():
    """处理所有加载的指标"""
    global loaded_metrics  # Declare loaded_metrics as global to access the updated version
    async with lock:  # 使用锁来确保对 shared state (loaded_metrics) 的同步访问
        for metric_name, metric_module in loaded_metrics.items():
            try:
                if hasattr(metric_module, 'process'):
                    print(f"Processing {metric_name}")
                    # 检查 process 是否为协程函数
                    if inspect.iscoroutinefunction(metric_module.process):
                        await metric_module.process()  # 调用协程的 process 方法
                    else:
                        metric_module.process()  # 调用普通函数的 process 方法
            except Exception as e:
                print(f"Error processing {metric_name}: {e}")

def run_croutine(loop, croutine):
    """运行一个协程"""
    if loop.is_running():
        loop.create_task(croutine())  # If loop is running, create the task
    else:
        loop.run_until_complete(croutine())  # If no loop is running, run the coroutine directly

class metricFileEventHandler(FileSystemEventHandler):
    """自定义事件处理器，用于处理文件增加、删除、修改"""
    
    def __init__(self):
        super().__init__()
        print(f'Creating and attach a new event loop')
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
    
    def on_created(self, event):
        print(f"File created from {event.src_path} to {event.dest_path}")
        """当文件被创建时，加载模块"""
        if event.src_path.endswith(".py"):
            print(f"Detected new file: {event.src_path}, loading...")
            run_croutine(self._loop, load_metric_modules)
            # load_metric_modules()

    def on_deleted(self, event):
        print(f"File deleted from {event.src_path} to {event.dest_path}")
        """当文件被删除时，卸载模块"""
        if event.src_path.endswith(".py"):
            print(f"Detected deleted file: {event.src_path}, reloading...")
            run_croutine(self._loop, load_metric_modules)
            # load_metric_modules()

    def on_modified(self, event):
        """当文件被修改时，重新加载模块"""
        print(f"File modified from {event.src_path} to {event.dest_path}")
        if not event.dest_path:
            return
        if event.src_path.endswith(".py"):
            print(f"Detected modified file: {event.src_path}, reloading...")
            run_croutine(self._loop, load_metric_modules)
            # load_metric_modules()

async def watch_metrics_directory():
    """监听 metrics 目录下文件的变化，动态更新指标"""
    event_handler = metricFileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, metrics_directory, recursive=False)
    observer.start()

    try:
        while True:
            await asyncio.sleep(1)  # 使用协程休眠替代 time.sleep
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

async def start_metrics_server():
    """启动 Prometheus HTTP 服务器"""
    start_http_server(8000)

async def main():
    """主协程，控制整个程序的流程"""
    # 加载初始模块
    await load_metric_modules()

    # 启动 Prometheus HTTP 服务器
    asyncio.create_task(start_metrics_server())

    # 启动监听文件变化的协程
    asyncio.create_task(watch_metrics_directory())

    # 主循环，每 10 秒处理一次指标
    while True:
        await process_metrics()  # 处理所有加载的指标
        await asyncio.sleep(10)  # 每 10 秒更新一次

if __name__ == '__main__':
    # 使用 asyncio 事件循环来运行主协程
    asyncio.run(main())
