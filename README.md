# Dynamic Prometheus Custom Exporter Server

## Introduction

This project implements a **dynamic Prometheus custom exporter server** that automatically loads and processes Python modules to expose custom metrics. The server watches a specified directory (`metrics`) for any changes in Python files (such as creation or deletion) and dynamically loads or unloads them as needed. The metrics are exposed over HTTP in a format compatible with Prometheus, allowing it to scrape and monitor custom metrics.

### Key Features:
- **Dynamic Metric Loading**: Automatically loads Python modules from a specified directory (`metrics`) and exposes the metrics through a Prometheus-compatible HTTP server.
- **Automatic Module Reloading**: Detects changes (e.g., file creation or deletion) in the `metrics` directory and dynamically loads or unloads modules.
- **Prometheus Compatibility**: Exposes metrics via an HTTP server that Prometheus can scrape for monitoring.
- **Multi-threading for Real-time Updates**: The server runs in the background, processing and updating metrics at regular intervals, while watching the `metrics` directory in real-time using multi-threading.

## Installation

Ensure you have Python installed and then install the required dependencies:

```bash
pip install prometheus_client watchdog # OR pip install -r requirements.txt
```

Make sure to place your custom metric Python scripts in the `metrics` directory. Each script must define a `process()` function to collect the respective metrics.

## Project Structure

Your project directory should look like this:

```
your_project/
├── main.py               # The main script to run the exporter
├── metrics/              # Directory containing metric Python scripts
│   ├── metric1.py
│   ├── metric2.py
│   └── ...
└── requirements.txt      # Dependency file
```

Each Python file inside the `metrics` directory should implement a `process()` function, which is responsible for collecting and updating metrics.

## Usage

1. **Run the exporter**:
   To start the dynamic Prometheus custom exporter server, run the following command:

   ```bash
   python main.py
   ```

   This will:
   - Load all Python modules in the `metrics` directory.
   - Start a Prometheus-compatible HTTP server on port `8000`.
   - Continuously watch the `metrics` directory for file changes (new or deleted Python scripts).
   - Periodically process the loaded metrics every 10 seconds.

2. **Access Metrics**:
   Once the server is running, Prometheus can scrape the metrics from:

   ```
   http://localhost:8000/metrics
   ```

3. **Modifying the Metrics**:
   - **Add new metrics**: Add new Python files to the `metrics` directory, and the server will automatically load them.
   - **Remove metrics**: Delete Python files from the `metrics` directory, and the server will automatically unload them.
   - **Modify existing metrics**: Modify a Python file in the `metrics` directory, and the server will dynamically reload it.

4. **Understanding Metric Modules**:
   Each metric module in the `metrics` directory must define a `process()` function that collects and updates the metric. Here’s an example of a simple metric module:

   ```python
   # metrics/example_metric.py

   from prometheus_client import Gauge

   # Define a Prometheus Gauge metric
   example_metric = Gauge('example_metric', 'An example metric')

   def process():
       # Update the metric value
       example_metric.set(42)
   ```

5. **Multi-threading/Concurrency**:
   - The server uses Python's threading capabilities to monitor the `metrics` directory for changes and process metrics concurrently.
   - If you prefer multiprocessing for handling file monitoring, there is an option to switch to that in the script (currently commented out).

## Code Overview

- **Dynamic Loading of Metrics**: 
  The script uses `importlib` to dynamically load Python files from the `metrics` directory. It checks for files with a `.py` extension and loads them as Python modules. The `process()` function defined in each module is called periodically to update the metrics.

- **Prometheus Exporter**: 
  The script uses `prometheus_client` to expose metrics over HTTP. The HTTP server is set up on port `8000`, and Prometheus can scrape the metrics from this endpoint.

- **File System Monitoring**: 
  The script uses `watchdog` to monitor the `metrics` directory for file changes. When new files are created or deleted, the server dynamically updates the list of loaded modules, adding or removing them as necessary.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
