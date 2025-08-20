from . import mcp

# Add a multiplication tool
@mcp.tool("multiply")
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Add a division tool
@mcp.tool("divide")
def divide_numbers(a: float, b: float) -> float:
    """Divide first number by second number"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Add a farewell resource
@mcp.resource("farewell://{name}")
def get_farewell(name: str) -> str:
    """Get a personalized farewell message"""
    return f"Goodbye, {name}! Have a great day!"
