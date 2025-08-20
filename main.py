import importlib
import time
import threading
import os
import contextlib
from dotenv import load_dotenv
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

load_dotenv()

METRICS_REFRESH_INTERVAL = int(os.environ.get('METRICS_REFRESH_INTERVAL', 10))

# Import MCP server
from mcps import mcp

# MCP directory
mcps_directory = 'mcps'
loaded_mcps = {}

# Function to load MCP modules
def load_mcp_modules():
    """Load all modules from the mcps directory"""
    global loaded_mcps
    
    # Get all files in the mcps directory
    current_files = set(os.listdir(mcps_directory))

    print(f"load_mcp_modules, loaded_mcps: {loaded_mcps}, current_files: {current_files}")
    
    # Remove modules that no longer exist
    to_remove = [mcp_name for mcp_name in loaded_mcps if f"{mcp_name}.py" not in current_files]
    with lock:
        for mcp_name in to_remove:
            del loaded_mcps[mcp_name]
            print(f"MCP module {mcp_name} removed, loaded_mcps: {loaded_mcps}")

    # Load new modules
    for filename in current_files:
        if filename.endswith(".py") and filename != '__init__.py':
            module_name = filename[:-3]
            if module_name not in loaded_mcps:
                try:
                    module = importlib.import_module(f'mcps.{module_name}')
                    loaded_mcps[module_name] = module
                    print(f"MCP module {module_name} loaded, loaded_mcps: {loaded_mcps}")
                except Exception as e:
                    print(f"Error loading MCP module {module_name}: {e}")

# Load environment variables from .env file
load_dotenv()

# Get port from environment variables, default to 8000
PORT = int(os.getenv("PORT", 8000))

# Metrics directory
metrics_directory = 'metrics'
loaded_metrics = {}

# Lock for thread safety
lock = threading.Lock()

def load_metric_modules():
    """Load all modules from the metrics directory"""
    global loaded_metrics
    
    # Get all files in the metrics directory
    current_files = set(os.listdir(metrics_directory))

    print(f"load_metric_modules, loaded_metrics: {loaded_metrics}, current_files: {current_files}")
    
    # Remove modules that no longer exist
    to_remove = [metric_name for metric_name in loaded_metrics if f"{metric_name}.py" not in current_files]
    with lock:
        for metric_name in to_remove:
            del loaded_metrics[metric_name]
            print(f"Module {metric_name} removed, loaded_metrics: {loaded_metrics}")

    # Load new modules
    for filename in current_files:
        if filename.endswith(".py") and filename != '__init__.py':
            module_name = filename[:-3]
            if module_name not in loaded_metrics:
                try:
                    module = importlib.import_module(f'metrics.{module_name}')
                    loaded_metrics[module_name] = module
                    refresh_interval = getattr(module, 'REFRESH_INTERVAL', METRICS_REFRESH_INTERVAL)
                    print(f"Module {module_name} loaded with refresh interval: {refresh_interval}s, loaded_metrics: {loaded_metrics}")
                    if hasattr(module, 'process'):
                        print(f"Processing {module_name}")
                        module.process()
                    # Start individual processing thread for this new module
                    start_individual_metric_processing(module_name, module)
                except Exception as e:
                    print(f"Error loading {module_name}: {e}")

def process_metrics():
    """
    Process all loaded metrics once (used during initial loading)
    Individual processing threads handle regular updates
    """
    global loaded_metrics
    with lock:
        for metric_name, metric_module in loaded_metrics.items():
            try:
                if hasattr(metric_module, 'process'):
                    refresh_interval = getattr(metric_module, 'REFRESH_INTERVAL', METRICS_REFRESH_INTERVAL)
                    print(f"Initial processing of {metric_name} (refresh: {refresh_interval}s)")
                    metric_module.process()
            except Exception as e:
                print(f"Error processing {metric_name}: {e}")

def start_individual_metric_processing(metric_name, metric_module):
    """Start processing a specific metric in its own background thread with its own refresh interval"""
    def individual_process_loop():
        while True:
            try:
                # Get the module's refresh interval or use the global default
                refresh_interval = getattr(metric_module, 'REFRESH_INTERVAL', METRICS_REFRESH_INTERVAL)
                
                if hasattr(metric_module, 'process'):
                    print(f"Processing {metric_name} (refresh: {refresh_interval}s)")
                    with lock:
                        metric_module.process()
                
                # Sleep for this metric's specific refresh interval
                time.sleep(refresh_interval)
            except Exception as e:
                print(f"Error processing {metric_name}: {e}")
                time.sleep(METRICS_REFRESH_INTERVAL)  # Use default interval on error
    
    thread = threading.Thread(target=individual_process_loop)
    thread.daemon = True
    thread.start()
    print(f"Started processing thread for {metric_name} with refresh interval: {getattr(metric_module, 'REFRESH_INTERVAL', METRICS_REFRESH_INTERVAL)}s")

class MetricFileEventHandler(FileSystemEventHandler):
    """Custom event handler for file system events in metrics directory"""
    
    def on_created(self, event):
        """When a file is created, load the module"""
        if event.src_path.endswith(".py"):
            print(f"Detected new metric file: {event.src_path}, loading...")
            load_metric_modules()

    def on_deleted(self, event):
        """When a file is deleted, unload the module"""
        if event.src_path.endswith(".py"):
            print(f"Detected deleted metric file: {event.src_path}, reloading...")
            load_metric_modules()

class McpFileEventHandler(FileSystemEventHandler):
    """Custom event handler for file system events in mcps directory"""
    
    def on_created(self, event):
        """When a file is created, load the module"""
        if event.src_path.endswith(".py"):
            print(f"Detected new MCP file: {event.src_path}, loading...")
            load_mcp_modules()

    def on_deleted(self, event):
        """When a file is deleted, unload the module"""
        if event.src_path.endswith(".py"):
            print(f"Detected deleted MCP file: {event.src_path}, reloading...")
            load_mcp_modules()

def watch_directories():
    """Watch the metrics and mcps directories for changes"""
    # Set up metrics directory watching
    metrics_handler = MetricFileEventHandler()
    metrics_observer = Observer()
    metrics_observer.schedule(metrics_handler, metrics_directory, recursive=False)
    metrics_observer.start()
    
    # Set up mcps directory watching
    mcps_handler = McpFileEventHandler()
    mcps_observer = Observer()
    mcps_observer.schedule(mcps_handler, mcps_directory, recursive=False)
    mcps_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        metrics_observer.stop()
        mcps_observer.stop()
    
    metrics_observer.join()
    mcps_observer.join()

def start_metrics_processing():
    """Start processing metrics in a background thread"""
    # Start individual metric processing threads with their own refresh intervals
    for metric_name, metric_module in loaded_metrics.items():
        start_individual_metric_processing(metric_name, metric_module)

def start_directory_watching():
    """Start watching the metrics and mcps directories in a background thread"""
    thread = threading.Thread(target=watch_directories)
    thread.daemon = True
    thread.start()

# # Create FastAPI app with lifespan context
# @contextlib.asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Initialize everything when the FastAPI app starts
#     load_metric_modules()  # Load initial modules
#     start_metrics_processing()  # Start processing metrics
#     start_directory_watching()  # Start watching for file changes
#     yield
#     # Shutdown: Clean up resources if needed

# Custom lifespan manager
@contextlib.asynccontextmanager
async def custom_lifespan(app: FastAPI):
    # Startup logic
    load_metric_modules()  # Load metrics modules
    load_mcp_modules()     # Load MCP modules
    start_metrics_processing()
    start_directory_watching()
    yield
    # Shutdown logic (if any)

# 合并两个lifespan：自定义的和mcp_app的
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # 先执行自定义的lifespan
    async with custom_lifespan(app):
        # 再执行mcp_app的lifespan
        async with mcp_app.lifespan(app):
            yield

# Create FastAPI app with the lifespan
app = FastAPI(
    title="Prometheus Custom Exporter with MCP",
    lifespan=lifespan
)

# Create and mount the MCP server
# Use the correct path parameter to avoid redirection issues
mcp_app = mcp.http_app(path="/")
app.mount("/mcp", mcp_app)

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Prometheus Custom Exporter with MCP",
        "endpoints": {
            "metrics": "/metrics",
            "mcp": "/mcp"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)