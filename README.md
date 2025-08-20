# Prometheus Custom Exporter with MCP Integration

## Introduction

This project implements a dynamic Prometheus custom exporter server with Model Context Protocol (MCP) integration. The server automatically loads and processes Python modules to expose custom metrics and MCP tools/resources. It watches specified directories (`metrics` and `mcps`) for any changes in Python files and dynamically loads or unloads them as needed.

### Key Features:

- **Dynamic Metric Loading**: Automatically loads Python modules from the `metrics` directory and exposes them through a Prometheus-compatible HTTP server.
- **Dynamic MCP Integration**: Automatically loads Python modules from the `mcps` directory and exposes MCP tools, resources, and prompts.
- **Automatic Module Reloading**: Detects changes in both directories and dynamically loads or unloads modules.
- **Unified API**: Both Prometheus metrics and MCP endpoints work on the same FastAPI server and port.
- **Environment Configuration**: Uses dotenv for configuration management.
- **Multi-threading for Real-time Updates**: The server runs in the background, processing and updating metrics at regular intervals.

## Installation

Ensure you have Python installed and then install the required dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

Your project directory should look like this:

```
prometheus_custom_exporter/
├── main.py               # The main FastAPI server script
├── .env                  # Environment configuration
├── metrics/              # Directory containing metric Python scripts
│   ├── custom_metrics_1.py
│   ├── custom_metrics_2.py
│   └── ...
├── mcps/                 # Directory containing MCP Python scripts
│   ├── __init__.py       # Initializes the FastMCP instance
│   ├── custom_mcp_1.py   # Custom MCP tools and resources
│   ├── custom_mcp_2.py   # Additional MCP tools and resources
│   └── ...
├── test_server.py        # Test script for verifying functionality
└── requirements.txt      # Dependency file
```

## Configuration

The server configuration is managed through the `.env` file:

```
# Configuration for Prometheus Custom Exporter with MCP
PORT=8000
```

## Usage

1. **Run the server**:
   To start the Prometheus custom exporter server with MCP integration, run:

   ```bash
   python main.py
   ```

   This will:
   - Load all Python modules in the `metrics` and `mcps` directories
   - Start a FastAPI server on the configured port (default: 8000)
   - Mount Prometheus metrics at `/metrics`
   - Mount MCP endpoints at `/mcp`
   - Continuously watch both directories for file changes
   - Periodically process the loaded metrics

2. **Access Endpoints**:
   - **Root**: `http://localhost:8000/`
   - **Metrics**: `http://localhost:8000/metrics`
   - **MCP**: `http://localhost:8000/mcp/`

3. **Testing the Server**:
   Run the test script to verify all functionality:

   ```bash
   python test_server.py
   ```

## Implementing Custom Metrics

Each metric module in the `metrics` directory must define a `process()` function that collects and updates metrics:

```python
# metrics/custom_metrics_1.py
from prometheus_client import Gauge
import random

# Define metrics
custom_metric_1 = Gauge('custom_metric_1', 'Description of custom metric', ['label1'])

def process():
    """Update the custom metric with simulated data"""
    data = {'value': random.randint(0, 100)}
    custom_metric_1.labels(label1="example").set(data['value'])
```

## Implementing MCP Tools and Resources

The MCP modules in the `mcps` directory can define tools, resources, and prompts:

### Tools

```python
# mcps/custom_mcp_1.py
from . import mcp

@mcp.tool("add")
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

### Resources

MCP resources can be static or dynamic:

```python
# Static resource
@mcp.resource("greeting://hello")
def get_greeting_hello() -> str:
    """Simple greeting"""
    return f"Hello!"

# Dynamic resource with parameters
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting message"""
    return f"Hello, {name}!"
```

### Prompts

```python
@mcp.prompt("weather_report")
def weather_prompt(city: str, date: str) -> str:
    """Generate a weather query prompt template"""
    return f"Please tell me the weather in {city} on {date}:"
```

## API Usage Examples

### MCP Tool Calls

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 7
    }
  },
  "id": 1
}
```

### MCP Resource Access

```json
{
  "jsonrpc": "2.0",
  "method": "resources/read",
  "params": {
    "uri": "greeting://Alice"
  },
  "id": 2
}
```

### MCP Prompt Access

```json
{
  "jsonrpc": "2.0",
  "method": "prompts/get",
  "params": {
    "name": "weather_report",
    "arguments": {
      "city": "Shanghai",
      "date": "today"
    }
  },
  "id": 3
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.