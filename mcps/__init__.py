# This file makes the mcps directory a Python package

from fastmcp import FastMCP

# Create a FastMCP instance with resource_prefix to enable direct resource access
mcp = FastMCP(
    name="PrometheusCustomExporter", 
    stateless_http=True, 
    json_response=True,
)
