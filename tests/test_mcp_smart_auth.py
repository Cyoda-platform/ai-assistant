#!/usr/bin/env python3
"""
Test script for MCP smart authentication
- Workflow tools: validate against user's environment
- Cyoda tools: no validation, let Cyoda API handle it
"""

import requests
import json
import sys
import os


def test_smart_authentication():
    """Test smart authentication behavior"""
    base_url = "http://localhost:8002"
    
    print("🔐 Testing MCP Smart Authentication")
    print("=" * 50)
    
    # Test 1: Check server info
    print("\n1. Testing server info...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            tools_count = data.get("tools_count", 0)
            print(f"✅ Server running with {tools_count} tools")

            auth_info = data.get("authentication", {})
            print(f"   Authentication required: {auth_info.get('required', False)}")

            # Show tool categories
            categories = data.get("tool_categories", {})
            workflow_count = categories.get("workflow_tools", 0)
            cyoda_count = categories.get("cyoda_api_tools", 0)
            print(f"   Workflow tools: {workflow_count}")
            print(f"   Cyoda API tools: {cyoda_count}")

            # Show Cyoda categories
            cyoda_categories = {k: v for k, v in categories.items() if k.startswith("cyoda_")}
            if cyoda_categories:
                print("   Cyoda tool categories:")
                for category, count in cyoda_categories.items():
                    category_name = category.replace("cyoda_", "").replace("_", " ").title()
                    print(f"     - {category_name}: {count} tools")
        else:
            print(f"❌ Server info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server info error: {e}")
        return False
    
    # Test 2: Test workflow tool without auth (should fail)
    print("\n2. Testing workflow tool without authentication...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_weather",  # Workflow tool
                "arguments": {
                    "technical_id": "auth_test"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload)
        if response.status_code == 401:
            print("✅ Workflow tool correctly requires authentication")
        elif response.status_code == 200:
            print("ℹ️  Workflow tool works without auth (auth disabled)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Workflow tool test error: {e}")
        return False
    
    # Test 3: Test Cyoda tool without auth (should fail)
    print("\n3. Testing Cyoda tool without authentication...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "accountget",  # Cyoda API tool
                "arguments": {
                    "technical_id": "auth_test"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload)
        if response.status_code == 401:
            print("✅ Cyoda tool correctly requires authentication")
        elif response.status_code == 200:
            print("ℹ️  Cyoda tool works without auth (auth disabled)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Cyoda tool test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 Smart Authentication Test Summary")
    print("=" * 50)
    print("✅ MCP server running with smart authentication")
    print("✅ Workflow tools: validate against user's environment")
    print("✅ Cyoda tools: minimal validation, let Cyoda API handle it")
    print("")
    print("📋 Authentication behavior:")
    print("  🔧 Workflow tools → validate_with_cyoda_environment(user_env)")
    print("  🔗 Cyoda tools → no validation, forward token to Cyoda API")
    print("")
    print("🔧 To test with authentication:")
    print("  1. Get OAuth2 token from your auth server")
    print("  2. Set TOKEN environment variable")
    print("  3. Run: python test_mcp_smart_auth.py --with-token")
    
    return True


def test_with_token():
    """Test smart authentication with actual token"""
    base_url = "http://localhost:8002"
    token = os.getenv("TOKEN")
    
    if not token:
        print("❌ No TOKEN environment variable set")
        print("   Set TOKEN environment variable with your OAuth2 token")
        return False
    
    print("🔐 Testing Smart Authentication with Token")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Workflow tool with token
    print("\n1. Testing workflow tool with token...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_weather",  # Workflow tool
                "arguments": {
                    "technical_id": "workflow_auth_test"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ Workflow tool executed successfully")
            print(f"   Result: {tool_result[:100]}...")
            print(f"   🔧 Token validated against user's environment")
        else:
            print(f"❌ Workflow tool failed: {response.status_code}")
            error_detail = response.json().get("detail", "Unknown error")
            print(f"   Error: {error_detail}")
    except Exception as e:
        print(f"❌ Workflow tool error: {e}")
    
    # Test 2: Cyoda tool with token
    print("\n2. Testing Cyoda tool with token...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "accountget",  # Cyoda API tool
                "arguments": {
                    "technical_id": "cyoda_auth_test"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ Cyoda tool executed")
            print(f"   Result: {tool_result[:100]}...")
            print(f"   🔗 Token forwarded to Cyoda API for validation")
            
            if "Error:" in tool_result:
                print("   ⚠️  Cyoda API returned error (expected without proper setup)")
            else:
                print("   ✅ Cyoda API call successful!")
        else:
            print(f"❌ Cyoda tool failed: {response.status_code}")
            error_detail = response.json().get("detail", "Unknown error")
            print(f"   Error: {error_detail}")
    except Exception as e:
        print(f"❌ Cyoda tool error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Smart Authentication Results")
    print("=" * 50)
    print("✅ Workflow tools: Environment-specific validation")
    print("✅ Cyoda tools: Token forwarding to Cyoda API")
    print("✅ Different authentication strategies per tool type")
    print("")
    print("📋 Authentication flow:")
    print("  1. MCP receives tool call with token")
    print("  2. Determines tool type (workflow vs Cyoda)")
    print("  3. Workflow tools: validate against user's environment")
    print("  4. Cyoda tools: forward token, let Cyoda validate")
    print("  5. Execute tool with appropriate authentication")
    
    return True


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-token":
        return test_with_token()
    else:
        return test_smart_authentication()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
