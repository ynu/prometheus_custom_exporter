import requests
import json
import time

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get("http://localhost:8000/")
        print("Root endpoint test:", "PASSED" if response.status_code == 200 else "FAILED")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Root endpoint test FAILED: {e}")

def test_metrics_endpoint():
    """Test the metrics endpoint"""
    try:
        response = requests.get("http://localhost:8000/metrics")
        print("Metrics endpoint test:", "PASSED" if response.status_code == 200 else "FAILED")
        print("Sample metrics:")
        # Print first few lines of metrics
        lines = response.text.split("\n")[:10]
        for line in lines:
            if line and not line.startswith("#"):
                print(f"  {line}")
    except Exception as e:
        print(f"Metrics endpoint test FAILED: {e}")

def test_mcp_endpoints():
    """Test the MCP endpoints with stateless HTTP and JSON response"""
    try:
        # Step 1: Test the add tool
        print("\n=== Testing MCP Add Tool ===\n")
        add_payload = {
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
        add_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(add_payload)
        )
        
        print(f"Add tool status code: {add_response.status_code}")
        print(f"Add tool response: {add_response.text}")
        
        if add_response.status_code == 200:
            add_result = add_response.json()
            if "result" in add_result and add_result.get("id") == 1:
                # Extract the actual result from the structured content
                if "structuredContent" in add_result["result"] and "result" in add_result["result"]["structuredContent"]:
                    actual_result = add_result["result"]["structuredContent"]["result"]
                    print("MCP add tool test:", "PASSED" if actual_result == 12 else "FAILED")
                    print(f"5 + 7 = {actual_result}")
                else:
                    print("MCP add tool test: FAILED - Unexpected result format")
                    print(f"Response: {add_result}")
            else:
                print("MCP add tool test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {add_result}")
        else:
            print(f"MCP add tool test FAILED: HTTP {add_response.status_code}")
        
        # Step 2: Test the multiply tool
        print("\n=== Testing MCP Multiply Tool ===\n")
        multiply_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "multiply",
                "arguments": {
                    "a": 6,
                    "b": 7
                }
            },
            "id": 2
        }
        multiply_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(multiply_payload)
        )
        
        print(f"Multiply tool status code: {multiply_response.status_code}")
        print(f"Multiply tool response: {multiply_response.text}")
        
        if multiply_response.status_code == 200:
            multiply_result = multiply_response.json()
            if "result" in multiply_result and multiply_result.get("id") == 2:
                # Extract the actual result from the structured content
                if "structuredContent" in multiply_result["result"] and "result" in multiply_result["result"]["structuredContent"]:
                    actual_result = multiply_result["result"]["structuredContent"]["result"]
                    print("MCP multiply tool test:", "PASSED" if actual_result == 42 else "FAILED")
                    print(f"6 * 7 = {actual_result}")
                else:
                    print("MCP multiply tool test: FAILED - Unexpected result format")
                    print(f"Response: {multiply_result}")
            else:
                print("MCP multiply tool test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {multiply_result}")
        else:
            print(f"MCP multiply tool test FAILED: HTTP {multiply_response.status_code}")
        
        # Step 3: Test the greeting resource with parameter
        print("\n=== Testing MCP Greeting Resource (Dynamic) ===\n")
        name = "CodeBuddy"
        # Use JSON-RPC 2.0 format for resource access
        greeting_payload = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {
                "uri": f"greeting://{name}"
            },
            "id": 3
        }
        greeting_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(greeting_payload)
        )
        
        print(f"Greeting resource status code: {greeting_response.status_code}")
        print(f"Greeting resource response: {greeting_response.text}")
        
        if greeting_response.status_code == 200:
            greeting_result = greeting_response.json()
            if "result" in greeting_result and greeting_result.get("id") == 3:
                # Extract the actual result from the response
                if "result" in greeting_result:
                    # The result could be directly in the result field or in content/structuredContent
                    if isinstance(greeting_result["result"], str):
                        actual_result = greeting_result["result"]
                    elif "content" in greeting_result["result"] and greeting_result["result"]["content"]:
                        actual_result = greeting_result["result"]["content"][0]["text"]
                    elif "structuredContent" in greeting_result["result"] and "result" in greeting_result["result"]["structuredContent"]:
                        actual_result = greeting_result["result"]["structuredContent"]["result"]
                    else:
                        actual_result = str(greeting_result["result"])
                    
                    expected = f"Hello, {name}!"
                    print("MCP greeting resource test:", "PASSED" if expected in actual_result else "FAILED")
                    print(f"Greeting: {actual_result}")
                else:
                    print("MCP greeting resource test: FAILED - No result in response")
                    print(f"Response: {greeting_result}")
            else:
                print("MCP greeting resource test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {greeting_result}")
        else:
            print(f"MCP greeting resource test FAILED: HTTP {greeting_response.status_code}")
        
        # Step 4: Test the static greeting resource
        print("\n=== Testing MCP Greeting Resource (Static) ===\n")
        # Use JSON-RPC 2.0 format for resource access
        static_greeting_payload = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {
                "uri": "greeting://hello"
            },
            "id": 4
        }
        static_greeting_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(static_greeting_payload)
        )
        
        print(f"Static greeting resource status code: {static_greeting_response.status_code}")
        print(f"Static greeting resource response: {static_greeting_response.text}")
        
        if static_greeting_response.status_code == 200:
            static_greeting_result = static_greeting_response.json()
            if "result" in static_greeting_result and static_greeting_result.get("id") == 4:
                # Extract the actual result from the response
                if "result" in static_greeting_result:
                    # The result could be directly in the result field or in content/structuredContent
                    if isinstance(static_greeting_result["result"], str):
                        actual_result = static_greeting_result["result"]
                    elif "content" in static_greeting_result["result"] and static_greeting_result["result"]["content"]:
                        actual_result = static_greeting_result["result"]["content"][0]["text"]
                    elif "structuredContent" in static_greeting_result["result"] and "result" in static_greeting_result["result"]["structuredContent"]:
                        actual_result = static_greeting_result["result"]["structuredContent"]["result"]
                    else:
                        actual_result = str(static_greeting_result["result"])
                    
                    expected = "Hello!"
                    print("MCP static greeting resource test:", "PASSED" if expected in actual_result else "FAILED")
                    print(f"Static Greeting: {actual_result}")
                else:
                    print("MCP static greeting resource test: FAILED - No result in response")
                    print(f"Response: {static_greeting_result}")
            else:
                print("MCP static greeting resource test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {static_greeting_result}")
        else:
            print(f"MCP static greeting resource test FAILED: HTTP {static_greeting_response.status_code}")
        
        # Step 5: Test the farewell resource
        print("\n=== Testing MCP Farewell Resource ===\n")
        name = "CodeBuddy"
        # Use JSON-RPC 2.0 format for resource access
        farewell_payload = {
            "jsonrpc": "2.0",
            "method": "resources/read",
            "params": {
                "uri": f"farewell://{name}"
            },
            "id": 5
        }
        farewell_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(farewell_payload)
        )
        
        print(f"Farewell resource status code: {farewell_response.status_code}")
        print(f"Farewell resource response: {farewell_response.text}")
        
        if farewell_response.status_code == 200:
            farewell_result = farewell_response.json()
            if "result" in farewell_result and farewell_result.get("id") == 5:
                # Extract the actual result from the response
                if "result" in farewell_result:
                    # The result could be directly in the result field or in content/structuredContent
                    if isinstance(farewell_result["result"], str):
                        actual_result = farewell_result["result"]
                    elif "content" in farewell_result["result"] and farewell_result["result"]["content"]:
                        actual_result = farewell_result["result"]["content"][0]["text"]
                    elif "structuredContent" in farewell_result["result"] and "result" in farewell_result["result"]["structuredContent"]:
                        actual_result = farewell_result["result"]["structuredContent"]["result"]
                    else:
                        actual_result = str(farewell_result["result"])
                    
                    expected = f"Goodbye, {name}! Have a great day!"
                    print("MCP farewell resource test:", "PASSED" if expected in actual_result else "FAILED")
                    print(f"Farewell: {actual_result}")
                else:
                    print("MCP farewell resource test: FAILED - No result in response")
                    print(f"Response: {farewell_result}")
            else:
                print("MCP farewell resource test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {farewell_result}")
        else:
            print(f"MCP farewell resource test FAILED: HTTP {farewell_response.status_code}")
        
        # Step 6: Test the weather prompt
        print("\n=== Testing MCP Weather Prompt ===\n")
        city = "Shanghai"
        date = "today"
        # Use JSON-RPC 2.0 format for prompt access
        prompt_payload = {
            "jsonrpc": "2.0",
            "method": "prompts/get",
            "params": {
                "name": "weather_report",
                "arguments": {
                    "city": city,
                    "date": date
                }
            },
            "id": 6
        }
        prompt_response = requests.post(
            "http://localhost:8000/mcp/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            data=json.dumps(prompt_payload)
        )
        
        print(f"Weather prompt status code: {prompt_response.status_code}")
        print(f"Weather prompt response: {prompt_response.text}")
        
        if prompt_response.status_code == 200:
            prompt_result = prompt_response.json()
            if "result" in prompt_result and prompt_result.get("id") == 6:
                # Extract the actual result from the response
                if "result" in prompt_result:
                    # The result could be directly in the result field or in content/structuredContent
                    if isinstance(prompt_result["result"], str):
                        actual_result = prompt_result["result"]
                    elif "content" in prompt_result["result"] and prompt_result["result"]["content"]:
                        actual_result = prompt_result["result"]["content"][0]["text"]
                    elif "structuredContent" in prompt_result["result"] and "result" in prompt_result["result"]["structuredContent"]:
                        actual_result = prompt_result["result"]["structuredContent"]["result"]
                    else:
                        actual_result = str(prompt_result["result"])
                    
                    expected = f"请告诉我{city}在{date}的天气情况："
                    print("MCP weather prompt test:", "PASSED" if expected in actual_result else "FAILED")
                    print(f"Weather Prompt: {actual_result}")
                else:
                    print("MCP weather prompt test: FAILED - No result in response")
                    print(f"Response: {prompt_result}")
            else:
                print("MCP weather prompt test: FAILED - Invalid JSON-RPC response")
                print(f"Response: {prompt_result}")
        else:
            print(f"MCP weather prompt test FAILED: HTTP {prompt_response.status_code}")
            
    except Exception as e:
        print(f"MCP endpoints test FAILED: {e}")

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(2)  # Give the server time to start
    
    print("\n=== Testing Server Endpoints ===\n")
    test_root_endpoint()
    
    print("\n=== Testing Prometheus Metrics ===\n")
    test_metrics_endpoint()
    
    print("\n=== Testing MCP Endpoints ===\n")
    test_mcp_endpoints()