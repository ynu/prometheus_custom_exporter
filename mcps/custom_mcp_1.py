from . import mcp

# Add an addition tool
@mcp.tool("add")
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting message"""
    return f"Hello, {name}!"



@mcp.resource("greeting://hello")
def get_greeting_hello() -> str:
    """Simple greeting"""
    return f"Hello!"


@mcp.prompt("weather_report")
def weather_prompt(city: str, date: str) -> str:
    """生成天气查询提示词模板"""
    return f"请告诉我{city}在{date}的天气情况："
