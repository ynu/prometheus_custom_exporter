from . import mcp
from metrics.custom_metrics_1 import custom_metric_1

@mcp.tool("get_metric_value")
def get_metric_value(label: str = "example") -> float:
    """
    Get the current value of custom_metric_1 for the specified label
    
    Args:
        label: The label value to query (default: "example")
        
    Returns:
        The current value of the metric
    """
    try:
        # Get the current value of the metric for the specified label
        value = custom_metric_1.labels(label1=label)._value.get()
        return value
    except Exception as e:
        return f"Error retrieving metric: {str(e)}"

@mcp.resource("metric://custom_metric_1/{label}")
def get_metric_resource(label: str = "example") -> str:
    """
    Get the current value of custom_metric_1 as a formatted string
    
    Args:
        label: The label value to query (default: "example")
        
    Returns:
        A formatted string with the metric value
    """
    try:
        # Get the current value of the metric for the specified label
        value = custom_metric_1.labels(label1=label)._value.get()
        return f"custom_metric_1{{label1=\"{label}\"}} = {value}"
    except Exception as e:
        return f"Error retrieving metric: {str(e)}"

@mcp.prompt("metric_alert")
def metric_alert_prompt(label: str = "example", threshold: float = 50.0) -> str:
    """
    Generate a prompt for alerting when the metric exceeds a threshold
    
    Args:
        label: The label value to check (default: "example")
        threshold: The threshold value to compare against (default: 50.0)
        
    Returns:
        A formatted prompt for alerting
    """
    try:
        # Get the current value of the metric for the specified label
        value = custom_metric_1.labels(label1=label)._value.get()
        
        if value > threshold:
            return f"ALERT: custom_metric_1 with label '{label}' has value {value}, which exceeds the threshold of {threshold}."
        else:
            return f"INFO: custom_metric_1 with label '{label}' has value {value}, which is below the threshold of {threshold}."
    except Exception as e:
        return f"Error retrieving metric: {str(e)}"