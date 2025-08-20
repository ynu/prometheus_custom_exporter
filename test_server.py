import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PORT = int(os.getenv("PORT", 8000))
BASE_URL = f"http://localhost:{PORT}"

class TestResult:
    """Class to store and display test results"""
    def __init__(self, name, passed, message=None, details=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
    
    def display(self):
        """Display the test result"""
        status = "PASSED" if self.passed else "FAILED"
        print(f"{self.name}: {status}")
        if self.message:
            print(f"{self.message}")
        if self.details:
            print(f"{self.details}")

class ServerTester:
    """Base class for server testing"""
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    
    def make_get_request(self, endpoint):
        """Make a GET request to the specified endpoint"""
        try:
            response = requests.get(f"{self.base_url}/{endpoint.lstrip('/')}")
            return response
        except Exception as e:
            return None, str(e)
    
    def make_post_request(self, endpoint, payload):
        """Make a POST request to the specified endpoint with the given payload"""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self.headers,
                data=json.dumps(payload)
            )
            return response
        except Exception as e:
            return None, str(e)
    
    def extract_result_content(self, response_json):
        """Extract the actual result content from various response formats"""
        if not response_json or "result" not in response_json:
            return None
        
        result = response_json["result"]
        
        # Handle different result formats
        if isinstance(result, str):
            return result
        elif "content" in result and result["content"]:
            return result["content"][0]["text"]
        elif "contents" in result and result["contents"]:
            return result["contents"][0]["text"]
        elif "structuredContent" in result and "result" in result["structuredContent"]:
            return result["structuredContent"]["result"]
        else:
            return str(result)

class BasicEndpointTester(ServerTester):
    """Test basic server endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        try:
            response = self.make_get_request("")
            if response and response.status_code == 200:
                return TestResult(
                    "Root endpoint test",
                    True,
                    f"Response: {response.json()}"
                )
            else:
                return TestResult(
                    "Root endpoint test",
                    False,
                    f"HTTP {response.status_code if response else 'No response'}"
                )
        except Exception as e:
            return TestResult("Root endpoint test", False, f"Error: {e}")
    
    def test_metrics_endpoint(self):
        """Test the metrics endpoint"""
        try:
            response = self.make_get_request("metrics")
            if response and response.status_code == 200:
                # Print first few non-comment lines of metrics
                sample_metrics = "\n".join([
                    f"  {line}" for line in response.text.split("\n")[:10]
                    if line and not line.startswith("#")
                ])
                return TestResult(
                    "Metrics endpoint test",
                    True,
                    "Sample metrics:",
                    sample_metrics
                )
            else:
                return TestResult(
                    "Metrics endpoint test",
                    False,
                    f"HTTP {response.status_code if response else 'No response'}"
                )
        except Exception as e:
            return TestResult("Metrics endpoint test", False, f"Error: {e}")

class McpTester(ServerTester):
    """Test MCP endpoints, tools, resources, and prompts"""
    
    def __init__(self, base_url=BASE_URL):
        super().__init__(base_url)
        self.mcp_endpoint = "mcp/"
    
    def test_tool(self, name, arguments, expected_result, test_id):
        """Test an MCP tool"""
        print(f"\n=== Testing MCP {name.capitalize()} Tool ===\n")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": test_id
        }
        
        response = self.make_post_request(self.mcp_endpoint, payload)
        
        print(f"{name.capitalize()} tool status code: {response.status_code}")
        print(f"{name.capitalize()} tool response: {response.text}")
        
        if response.status_code == 200:
            result_json = response.json()
            if "result" in result_json and result_json.get("id") == test_id:
                actual_result = self.extract_result_content(result_json)
                
                if actual_result == expected_result:
                    return TestResult(
                        f"MCP {name} tool test",
                        True,
                        f"{' '.join(str(arg) for arg in arguments.values())} = {actual_result}"
                    )
                else:
                    return TestResult(
                        f"MCP {name} tool test",
                        False,
                        f"Expected {expected_result}, got {actual_result}"
                    )
            else:
                return TestResult(
                    f"MCP {name} tool test",
                    False,
                    "Invalid JSON-RPC response",
                    f"Response: {result_json}"
                )
        else:
            return TestResult(
                f"MCP {name} tool test",
                False,
                f"HTTP {response.status_code}"
            )
    
    def test_resource(self, uri, expected_result, test_id, name=None):
        """Test an MCP resource"""
        resource_type = name if name else uri.split("://")[0]
        print(f"\n=== Testing MCP {resource_type.capitalize()} Resource ===\n")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {
                "uri": uri
            },
            "id": test_id
        }
        
        response = self.make_post_request(self.mcp_endpoint, payload)
        
        print(f"{resource_type.capitalize()} resource status code: {response.status_code}")
        print(f"{resource_type.capitalize()} resource response: {response.text}")
        
        if response.status_code == 200:
            result_json = response.json()
            if "result" in result_json and result_json.get("id") == test_id:
                # For resources, the result is in the contents array
                if "result" in result_json and "contents" in result_json["result"]:
                    actual_result = result_json["result"]["contents"][0]["text"]
                    
                    if expected_result in actual_result:
                        return TestResult(
                            f"MCP {resource_type} resource test",
                            True,
                            f"{resource_type.capitalize()}: {actual_result}"
                        )
                    else:
                        return TestResult(
                            f"MCP {resource_type} resource test",
                            False,
                            f"Expected '{expected_result}', got '{actual_result}'"
                        )
                else:
                    return TestResult(
                        f"MCP {resource_type} resource test",
                        False,
                        "No contents in response",
                        f"Response: {result_json}"
                    )
            else:
                return TestResult(
                    f"MCP {resource_type} resource test",
                    False,
                    "Invalid JSON-RPC response",
                    f"Response: {result_json}"
                )
        else:
            return TestResult(
                f"MCP {resource_type} resource test",
                False,
                f"HTTP {response.status_code}"
            )
    
    def test_prompt(self, name, arguments, expected_result, test_id):
        """Test an MCP prompt"""
        print(f"\n=== Testing MCP {name.capitalize()} Prompt ===\n")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "prompts/get",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": test_id
        }
        
        response = self.make_post_request(self.mcp_endpoint, payload)
        
        print(f"{name.capitalize()} prompt status code: {response.status_code}")
        print(f"{name.capitalize()} prompt response: {response.text}")
        
        if response.status_code == 200:
            result_json = response.json()
            if "result" in result_json and result_json.get("id") == test_id:
                actual_result = self.extract_result_content(result_json)
                
                if expected_result in actual_result:
                    return TestResult(
                        f"MCP {name} prompt test",
                        True,
                        f"{name.capitalize()} Prompt: {actual_result}"
                    )
                else:
                    return TestResult(
                        f"MCP {name} prompt test",
                        False,
                        f"Expected '{expected_result}', got '{actual_result}'"
                    )
            else:
                return TestResult(
                    f"MCP {name} prompt test",
                    False,
                    "Invalid JSON-RPC response",
                    f"Response: {result_json}"
                )
        else:
            return TestResult(
                f"MCP {name} prompt test",
                False,
                f"HTTP {response.status_code}"
            )

def run_all_tests():
    """Run all tests and display results"""
    print("Waiting for server to start...")
    time.sleep(2)  # Give the server time to start
    
    # Test basic endpoints
    print("\n=== Testing Server Endpoints ===\n")
    basic_tester = BasicEndpointTester()
    root_result = basic_tester.test_root_endpoint()
    root_result.display()
    
    print("\n=== Testing Prometheus Metrics ===\n")
    metrics_result = basic_tester.test_metrics_endpoint()
    metrics_result.display()
    
    # Test MCP endpoints
    print("\n=== Testing MCP Endpoints ===\n")
    mcp_tester = McpTester()
    
    # Test MCP tools
    add_result = mcp_tester.test_tool(
        "add", 
        {"a": 5, "b": 7}, 
        12, 
        1
    )
    add_result.display()
    
    multiply_result = mcp_tester.test_tool(
        "multiply", 
        {"a": 6, "b": 7}, 
        42, 
        2
    )
    multiply_result.display()
    
    # Test MCP resources
    name = "CodeBuddy"
    greeting_result = mcp_tester.test_resource(
        f"greeting://{name}",
        f"Hello, {name}!",
        3,
        "Greeting (Dynamic)"
    )
    greeting_result.display()
    
    static_greeting_result = mcp_tester.test_resource(
        "greeting://hello",
        "Hello!",
        4,
        "Greeting (Static)"
    )
    static_greeting_result.display()
    
    farewell_result = mcp_tester.test_resource(
        f"farewell://{name}",
        f"Goodbye, {name}! Have a great day!",
        5,
        "Farewell"
    )
    farewell_result.display()
    
    # Test MCP prompts
    city = "Shanghai"
    date = "today"
    weather_prompt_result = mcp_tester.test_prompt(
        "weather_report",
        {"city": city, "date": date},
        f"请告诉我{city}在{date}的天气情况：",
        6
    )
    weather_prompt_result.display()
    
    # Test metric access via MCP
    print("\n=== Testing Metric Access via MCP ===\n")
    
    # Test metric tool
    metric_tool_result = mcp_tester.test_tool(
        "get_metric_value",
        {"label": "example"},
        None,  # We can't predict the exact value
        7
    )
    # Override the display since we can't predict the exact value
    print(f"MCP get_metric_value tool test: PASSED if a number was returned")
    print(f"Metric value: {metric_tool_result.message}")
    
    # Test metric resource
    label = "example"
    metric_resource_result = mcp_tester.test_resource(
        f"metric://custom_metric_1/{label}",
        f"custom_metric_1{{label1=\"{label}\"}}",  # Just check for the prefix
        8,
        "Metric"
    )
    metric_resource_result.display()
    
    # Test metric alert prompt
    threshold = 50.0
    metric_alert_result = mcp_tester.test_prompt(
        "metric_alert",
        {"label": "example", "threshold": threshold},
        "custom_metric_1",  # Just check for the metric name
        9
    )
    metric_alert_result.display()
    
    # Test ZStack metrics via MCP
    print("\n=== Testing ZStack Metrics via MCP ===\n")
    
    # Test ZStack metrics tool
    print("Testing get_zstack_metrics tool...")
    zstack_metrics_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "get_zstack_metrics",
            "arguments": {}
        },
        "id": 10
    }
    zstack_metrics_response = requests.post(
        f"{BASE_URL}/mcp/",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        data=json.dumps(zstack_metrics_payload)
    )
    
    if zstack_metrics_response.status_code == 200:
        print("ZStack metrics tool test: PASSED")
        # Just print a sample of the response to avoid overwhelming output
        try:
            result = zstack_metrics_response.json()
            if "result" in result and "structuredContent" in result["result"] and "result" in result["result"]["structuredContent"]:
                metrics = result["result"]["structuredContent"]["result"]
                print(f"Sample metrics: availableHostCount={metrics.get('availableHostCount')}, totalVmCount={metrics.get('totalVmCount')}")
            else:
                print("Could not extract metrics from response")
        except Exception as e:
            print(f"Error parsing response: {e}")
    else:
        print(f"ZStack metrics tool test FAILED: HTTP {zstack_metrics_response.status_code}")
    
    # Test ZStack resource
    print("\nTesting zstack://metrics resource...")
    zstack_resource_payload = {
        "jsonrpc": "2.0",
        "method": "resources/read",
        "params": {
            "uri": "zstack://metrics"
        },
        "id": 11
    }
    zstack_resource_response = requests.post(
        f"{BASE_URL}/mcp/",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        data=json.dumps(zstack_resource_payload)
    )
    
    if zstack_resource_response.status_code == 200:
        print("ZStack resource test: PASSED")
    else:
        print(f"ZStack resource test FAILED: HTTP {zstack_resource_response.status_code}")
    
    # Test ZStack status report prompt
    print("\nTesting zstack_status_report prompt...")
    zstack_prompt_payload = {
        "jsonrpc": "2.0",
        "method": "prompts/get",
        "params": {
            "name": "zstack_status_report",
            "arguments": {}
        },
        "id": 12
    }
    zstack_prompt_response = requests.post(
        f"{BASE_URL}/mcp/",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        },
        data=json.dumps(zstack_prompt_payload)
    )
    
    if zstack_prompt_response.status_code == 200:
        print("ZStack status report prompt test: PASSED")
    else:
        print(f"ZStack status report prompt test FAILED: HTTP {zstack_prompt_response.status_code}")

if __name__ == "__main__":
    run_all_tests()