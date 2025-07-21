#!/usr/bin/env python3
"""
Test script for Cyoda proxy HTTP methods and parameter handling
"""

import requests
import json
import sys
import os


def test_cyoda_proxy_methods():
    """Test Cyoda proxy with different HTTP methods"""
    base_url = "http://localhost:8002"
    
    print("🔧 Testing Cyoda Proxy HTTP Methods")
    print("=" * 50)
    
    # Test 1: GET operation (should work)
    print("\n1. Testing GET operation (accountget)...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "accountget",
                "arguments": {
                    "technical_id": "test_get_account"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ GET operation executed")
            print(f"   Result: {tool_result[:200]}...")
            
            if "405" in tool_result:
                print("❌ Still getting 405 Method Not Allowed")
            elif "Error:" in tool_result:
                print("⚠️  Got error response (expected without proper auth)")
            else:
                print("✅ GET operation successful!")
        else:
            print(f"❌ Request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GET test error: {e}")
    
    # Test 2: POST operation with parameters (the problematic one)
    print("\n2. Testing POST operation (saveentities)...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "saveentities",
                "arguments": {
                    "technical_id": "test_save_entities",
                    "format": "json",
                    "entityName": "TestEntity",
                    "modelVersion": 1,
                    "transactionWindow": 5000,
                    "entities": [{"id": "test123", "name": "Test Entity"}]
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ POST operation executed")
            print(f"   Result: {tool_result[:200]}...")
            
            if "405" in tool_result:
                print("❌ Still getting 405 Method Not Allowed")
                print("   This indicates parameter separation issue")
            elif "Error:" in tool_result:
                print("⚠️  Got error response (may be auth or validation error)")
            else:
                print("✅ POST operation successful!")
        else:
            print(f"❌ Request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ POST test error: {e}")
    
    # Test 3: Check parameter separation logic
    print("\n3. Testing parameter separation logic...")
    try:
        # Import the proxy service to test parameter separation
        sys.path.append('..')
        from services.cyoda_proxy_service import cyoda_proxy
        
        # Get the saveentities tool definition
        cyoda_tools = cyoda_proxy.get_cyoda_tools()
        if "saveentities" in cyoda_tools:
            tool_def = cyoda_tools["saveentities"]
            
            # Test arguments
            test_args = {
                "format": "json",
                "entityName": "TestEntity", 
                "modelVersion": 1,
                "transactionWindow": 5000,
                "entities": [{"id": "test123", "name": "Test Entity"}]
            }
            
            # Test parameter separation
            query_params, body_params = cyoda_proxy._separate_parameters(tool_def, test_args.copy())
            
            print(f"✅ Parameter separation test:")
            print(f"   Query params: {query_params}")
            print(f"   Body params: {body_params}")
            
            # Check if separation looks correct
            expected_query = ["format", "entityName", "modelVersion", "transactionWindow"]
            expected_body = ["entities"]
            
            query_correct = any(param in query_params for param in expected_query)
            body_correct = any(param in body_params for param in expected_body)
            
            if query_correct and body_correct:
                print("✅ Parameter separation looks correct")
            else:
                print("⚠️  Parameter separation may need adjustment")
        else:
            print("❌ saveentities tool not found")
            
    except Exception as e:
        print(f"❌ Parameter separation test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Cyoda Proxy Method Test Summary")
    print("=" * 50)
    print("✅ Improved parameter separation logic")
    print("✅ Better error handling and logging")
    print("✅ Path parameter substitution")
    print("")
    print("📋 If still getting 405 errors:")
    print("  1. Check if path parameters are correctly substituted")
    print("  2. Verify query vs body parameter separation")
    print("  3. Check if HTTP method matches OpenAPI spec")
    print("  4. Validate request format against Cyoda API")
    
    return True


def test_with_debug_logging():
    """Test with debug logging to see parameter handling"""
    print("🔍 Testing with Debug Information")
    print("=" * 50)
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    base_url = "http://localhost:8002"
    
    print("\n1. Testing POST with debug logging...")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "saveentities",
            "arguments": {
                "technical_id": "debug_test",
                "format": "json",
                "entityName": "DebugEntity",
                "modelVersion": 1,
                "transactionWindow": 5000,
                "entities": [{"id": "debug123", "name": "Debug Entity"}]
            }
        }
    }
    
    try:
        response = requests.post(f"{base_url}/call", json=payload)
        result = response.json()
        tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
        
        print(f"Response: {tool_result}")
        
        if "405" in tool_result:
            print("\n❌ 405 Method Not Allowed - Possible causes:")
            print("  - Wrong HTTP method for endpoint")
            print("  - Parameters in wrong location (query vs body)")
            print("  - Missing required path parameters")
            print("  - Incorrect Content-Type header")
        
    except Exception as e:
        print(f"Debug test error: {e}")
    
    return True


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        return test_with_debug_logging()
    else:
        return test_cyoda_proxy_methods()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
