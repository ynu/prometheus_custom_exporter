from . import mcp
import json
from metrics.zstack_metrics import (
    zstack_available_host_count,
    zstack_total_memory_capacity,
    zstack_total_cpu_capacity,
    zstack_available_cpu_capacity,
    zstack_available_memory_capacity,
    zstack_primary_storage_total_capacity,
    zstack_primary_storage_available_capacity,
    zstack_total_host_count,
    zstack_total_vm_count,
    zstack_running_vm_count,
    fetch_zstack_metrics
)

# Helper function to get metric value
def get_metric_value(metric):
    """Get the current value of a Prometheus metric"""
    try:
        return metric._value.get()
    except Exception as e:
        return f"Error retrieving metric: {str(e)}"

# Tool to get all ZStack metrics
@mcp.tool("get_zstack_metrics")
def get_zstack_metrics() -> dict:
    """
    Get all current ZStack metrics
    
    Returns:
        A dictionary containing all ZStack metrics
    """
    return {
        "availableHostCount": get_metric_value(zstack_available_host_count),
        "totalMemoryCapacity": get_metric_value(zstack_total_memory_capacity),
        "totalCpuCapacity": get_metric_value(zstack_total_cpu_capacity),
        "availableCpuCapacity": get_metric_value(zstack_available_cpu_capacity),
        "availableMemoryCapacity": get_metric_value(zstack_available_memory_capacity),
        "primaryStorageTotalCapacity": get_metric_value(zstack_primary_storage_total_capacity),
        "primaryStorageAvailableCapacity": get_metric_value(zstack_primary_storage_available_capacity),
        "totalHostCount": get_metric_value(zstack_total_host_count),
        "totalVmCount": get_metric_value(zstack_total_vm_count),
        "runningVmCount": get_metric_value(zstack_running_vm_count)
    }

# Tool to refresh ZStack metrics
@mcp.tool("refresh_zstack_metrics")
def refresh_zstack_metrics() -> dict:
    """
    Fetch fresh metrics from ZStack API and update Prometheus metrics
    
    Returns:
        The newly fetched metrics or an error message
    """
    metrics_data = fetch_zstack_metrics()
    if metrics_data:
        return metrics_data
    else:
        return {"error": "Failed to fetch ZStack metrics"}

# Individual metric tools
@mcp.tool("get_zstack_available_host_count")
def get_available_host_count() -> int:
    """Get the number of available hosts in ZStack"""
    return get_metric_value(zstack_available_host_count)

@mcp.tool("get_zstack_total_memory_capacity")
def get_total_memory_capacity() -> int:
    """Get the total memory capacity in ZStack (bytes)"""
    return get_metric_value(zstack_total_memory_capacity)

@mcp.tool("get_zstack_total_cpu_capacity")
def get_total_cpu_capacity() -> int:
    """Get the total CPU capacity in ZStack"""
    return get_metric_value(zstack_total_cpu_capacity)

@mcp.tool("get_zstack_available_cpu_capacity")
def get_available_cpu_capacity() -> int:
    """Get the available CPU capacity in ZStack"""
    return get_metric_value(zstack_available_cpu_capacity)

@mcp.tool("get_zstack_available_memory_capacity")
def get_available_memory_capacity() -> int:
    """Get the available memory capacity in ZStack (bytes)"""
    return get_metric_value(zstack_available_memory_capacity)

@mcp.tool("get_zstack_primary_storage_total_capacity")
def get_primary_storage_total_capacity() -> int:
    """Get the total primary storage capacity in ZStack (bytes)"""
    return get_metric_value(zstack_primary_storage_total_capacity)

@mcp.tool("get_zstack_primary_storage_available_capacity")
def get_primary_storage_available_capacity() -> int:
    """Get the available primary storage capacity in ZStack (bytes)"""
    return get_metric_value(zstack_primary_storage_available_capacity)

@mcp.tool("get_zstack_total_host_count")
def get_total_host_count() -> int:
    """Get the total number of hosts in ZStack"""
    return get_metric_value(zstack_total_host_count)

@mcp.tool("get_zstack_total_vm_count")
def get_total_vm_count() -> int:
    """Get the total number of VMs in ZStack"""
    return get_metric_value(zstack_total_vm_count)

@mcp.tool("get_zstack_running_vm_count")
def get_running_vm_count() -> int:
    """Get the number of running VMs in ZStack"""
    return get_metric_value(zstack_running_vm_count)

# Resources for each metric
@mcp.resource("zstack://metrics")
def zstack_metrics_resource() -> str:
    """Get all ZStack metrics as a formatted JSON string"""
    metrics = get_zstack_metrics()
    return json.dumps(metrics, indent=2)

@mcp.resource("zstack://availableHostCount")
def available_host_count_resource() -> str:
    """Get the number of available hosts in ZStack"""
    return f"ZStack Available Host Count: {get_metric_value(zstack_available_host_count)}"

@mcp.resource("zstack://totalMemoryCapacity")
def total_memory_capacity_resource() -> str:
    """Get the total memory capacity in ZStack"""
    value = get_metric_value(zstack_total_memory_capacity)
    gb_value = value / (1024 * 1024 * 1024)
    return f"ZStack Total Memory Capacity: {value} bytes ({gb_value:.2f} GB)"

@mcp.resource("zstack://totalCpuCapacity")
def total_cpu_capacity_resource() -> str:
    """Get the total CPU capacity in ZStack"""
    return f"ZStack Total CPU Capacity: {get_metric_value(zstack_total_cpu_capacity)}"

@mcp.resource("zstack://availableCpuCapacity")
def available_cpu_capacity_resource() -> str:
    """Get the available CPU capacity in ZStack"""
    return f"ZStack Available CPU Capacity: {get_metric_value(zstack_available_cpu_capacity)}"

@mcp.resource("zstack://availableMemoryCapacity")
def available_memory_capacity_resource() -> str:
    """Get the available memory capacity in ZStack"""
    value = get_metric_value(zstack_available_memory_capacity)
    gb_value = value / (1024 * 1024 * 1024)
    return f"ZStack Available Memory Capacity: {value} bytes ({gb_value:.2f} GB)"

@mcp.resource("zstack://primaryStorageTotalCapacity")
def primary_storage_total_capacity_resource() -> str:
    """Get the total primary storage capacity in ZStack"""
    value = get_metric_value(zstack_primary_storage_total_capacity)
    tb_value = value / (1024 * 1024 * 1024 * 1024)
    return f"ZStack Primary Storage Total Capacity: {value} bytes ({tb_value:.2f} TB)"

@mcp.resource("zstack://primaryStorageAvailableCapacity")
def primary_storage_available_capacity_resource() -> str:
    """Get the available primary storage capacity in ZStack"""
    value = get_metric_value(zstack_primary_storage_available_capacity)
    tb_value = value / (1024 * 1024 * 1024 * 1024)
    return f"ZStack Primary Storage Available Capacity: {value} bytes ({tb_value:.2f} TB)"

@mcp.resource("zstack://totalHostCount")
def total_host_count_resource() -> str:
    """Get the total number of hosts in ZStack"""
    return f"ZStack Total Host Count: {get_metric_value(zstack_total_host_count)}"

@mcp.resource("zstack://totalVmCount")
def total_vm_count_resource() -> str:
    """Get the total number of VMs in ZStack"""
    return f"ZStack Total VM Count: {get_metric_value(zstack_total_vm_count)}"

@mcp.resource("zstack://runningVmCount")
def running_vm_count_resource() -> str:
    """Get the number of running VMs in ZStack"""
    return f"ZStack Running VM Count: {get_metric_value(zstack_running_vm_count)}"

# Prompts for ZStack metrics
@mcp.prompt("zstack_status_report")
def zstack_status_report() -> str:
    """Generate a status report for ZStack"""
    metrics = get_zstack_metrics()
    
    # Calculate percentages
    cpu_usage_percent = ((metrics["totalCpuCapacity"] - metrics["availableCpuCapacity"]) / metrics["totalCpuCapacity"]) * 100 if metrics["totalCpuCapacity"] > 0 else 0
    memory_usage_percent = ((metrics["totalMemoryCapacity"] - metrics["availableMemoryCapacity"]) / metrics["totalMemoryCapacity"]) * 100 if metrics["totalMemoryCapacity"] > 0 else 0
    storage_usage_percent = ((metrics["primaryStorageTotalCapacity"] - metrics["primaryStorageAvailableCapacity"]) / metrics["primaryStorageTotalCapacity"]) * 100 if metrics["primaryStorageTotalCapacity"] > 0 else 0
    
    return f"""
# ZStack Status Report

## Host Status
- Available Hosts: {metrics["availableHostCount"]} out of {metrics["totalHostCount"]} ({(metrics["availableHostCount"] / metrics["totalHostCount"] * 100):.1f}% availability)

## Resource Utilization
- CPU: {cpu_usage_percent:.1f}% used ({metrics["totalCpuCapacity"] - metrics["availableCpuCapacity"]} of {metrics["totalCpuCapacity"]})
- Memory: {memory_usage_percent:.1f}% used ({(metrics["totalMemoryCapacity"] - metrics["availableMemoryCapacity"]) / (1024 * 1024 * 1024):.1f} GB of {metrics["totalMemoryCapacity"] / (1024 * 1024 * 1024):.1f} GB)
- Storage: {storage_usage_percent:.1f}% used ({(metrics["primaryStorageTotalCapacity"] - metrics["primaryStorageAvailableCapacity"]) / (1024 * 1024 * 1024 * 1024):.1f} TB of {metrics["primaryStorageTotalCapacity"] / (1024 * 1024 * 1024 * 1024):.1f} TB)

## Virtual Machines
- Total VMs: {metrics["totalVmCount"]}
- Running VMs: {metrics["runningVmCount"]} ({(metrics["runningVmCount"] / metrics["totalVmCount"] * 100):.1f}% of total)
"""

@mcp.prompt("zstack_alert_check")
def zstack_alert_check(cpu_threshold: float = 80.0, memory_threshold: float = 80.0, storage_threshold: float = 80.0) -> str:
    """
    Check if any ZStack metrics exceed specified thresholds
    
    Args:
        cpu_threshold: CPU usage percentage threshold for alerts (default: 80.0)
        memory_threshold: Memory usage percentage threshold for alerts (default: 80.0)
        storage_threshold: Storage usage percentage threshold for alerts (default: 80.0)
        
    Returns:
        Alert messages for any metrics exceeding thresholds
    """
    metrics = get_zstack_metrics()
    
    # Calculate percentages
    cpu_usage_percent = ((metrics["totalCpuCapacity"] - metrics["availableCpuCapacity"]) / metrics["totalCpuCapacity"]) * 100 if metrics["totalCpuCapacity"] > 0 else 0
    memory_usage_percent = ((metrics["totalMemoryCapacity"] - metrics["availableMemoryCapacity"]) / metrics["totalMemoryCapacity"]) * 100 if metrics["totalMemoryCapacity"] > 0 else 0
    storage_usage_percent = ((metrics["primaryStorageTotalCapacity"] - metrics["primaryStorageAvailableCapacity"]) / metrics["primaryStorageTotalCapacity"]) * 100 if metrics["primaryStorageTotalCapacity"] > 0 else 0
    
    alerts = []
    
    if cpu_usage_percent >= cpu_threshold:
        alerts.append(f"⚠️ ALERT: CPU usage at {cpu_usage_percent:.1f}%, exceeding threshold of {cpu_threshold}%")
    
    if memory_usage_percent >= memory_threshold:
        alerts.append(f"⚠️ ALERT: Memory usage at {memory_usage_percent:.1f}%, exceeding threshold of {memory_threshold}%")
    
    if storage_usage_percent >= storage_threshold:
        alerts.append(f"⚠️ ALERT: Storage usage at {storage_usage_percent:.1f}%, exceeding threshold of {storage_threshold}%")
    
    if not alerts:
        return "✅ All ZStack metrics are within acceptable thresholds."
    
    return "\n".join(alerts)