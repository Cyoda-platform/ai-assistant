#!/usr/bin/env python3
"""
Test script for MCP authentication
"""

import requests
import json
import sys
import os


def test_mcp_authentication():
    """Test MCP server authentication"""
    base_url = "http://localhost:8002"
    
    print("🔐 Testing MCP Authentication")
    print("=" * 40)
    
    # Test 1: Public endpoint (should work)
    print("\n1. Testing public endpoint (/)...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            auth_required = data.get("authentication", {}).get("required", False)
            print(f"✅ Public endpoint works")
            print(f"   Auth required: {auth_required}")
            print(f"   Authenticated user: {data.get('authenticated_user', 'None')}")
        else:
            print(f"❌ Public endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Public endpoint error: {e}")
        return False
    
    # Test 2: Protected endpoint without token (should fail if auth enabled)
    print("\n2. Testing protected endpoint without token...")
    try:
        response = requests.get(f"{base_url}/tools")
        if response.status_code == 401:
            print("✅ Protected endpoint correctly rejects unauthenticated requests")
        elif response.status_code == 200:
            print("ℹ️  Protected endpoint allows unauthenticated requests (auth disabled)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Protected endpoint test error: {e}")
        return False
    
    # Test 3: Protected endpoint with invalid token (should fail)
    print("\n3. Testing protected endpoint with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(f"{base_url}/tools", headers=headers)
        if response.status_code == 401:
            print("✅ Protected endpoint correctly rejects invalid tokens")
            error_detail = response.json().get("detail", "Unknown error")
            print(f"   Error: {error_detail}")
        elif response.status_code == 200:
            print("ℹ️  Protected endpoint allows invalid tokens (auth disabled)")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid token test error: {e}")
        return False
    
    # Test 4: Tool call without token (should fail if auth enabled)
    print("\n4. Testing tool call without authentication...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "technical_id": "auth_test"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload)
        if response.status_code == 401:
            print("✅ Tool calls correctly require authentication")
        elif response.status_code == 200:
            print("ℹ️  Tool calls work without authentication (auth disabled)")
            result = response.json()
            print(f"   Result: {result.get('result', {}).get('content', [{}])[0].get('text', 'No result')[:50]}...")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Tool call test error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🔐 Authentication Test Summary")
    print("=" * 40)
    
    # Check if auth is enabled
    try:
        response = requests.get(f"{base_url}/")
        data = response.json()
        auth_enabled = data.get("authentication", {}).get("required", False)
        
        if auth_enabled:
            print("✅ Authentication is ENABLED")
            print("📋 To test with valid token:")
            print("   1. Obtain OAuth2 token from your auth server")
            print("   2. Set TOKEN environment variable")
            print("   3. Run: python test_mcp_auth.py --with-token")
            print("")
            print("🔧 Example with token:")
            print('   export TOKEN="your_oauth2_token"')
            print("   python test_mcp_auth.py --with-token")
        else:
            print("ℹ️  Authentication is DISABLED")
            print("📋 All endpoints work without authentication")
            print("🔧 To enable authentication:")
            print("   Set ENABLE_AUTH=true in your environment")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not determine auth status: {e}")
        return False


def test_with_token():
    """Test MCP with actual token"""
    base_url = "http://localhost:8002"
    token = os.getenv("TOKEN")
    
    if not token:
        print("❌ No TOKEN environment variable set")
        print("   Set TOKEN environment variable with your OAuth2 token")
        return False
    
    print("🔐 Testing MCP with Authentication Token")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List tools with token
    print("\n1. Testing tools list with token...")
    try:
        response = requests.get(f"{base_url}/tools", headers=headers)
        if response.status_code == 200:
            data = response.json()
            tools_count = len(data.get("result", {}).get("tools", []))
            print(f"✅ Tools list successful: {tools_count} tools available")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        return False
    
    # Test 2: Call tool with token
    print("\n2. Testing tool call with token...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_weather",
                "arguments": {
                    "technical_id": "auth_test_with_token"
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ Tool call successful")
            print(f"   Result: {tool_result[:100]}...")
        else:
            print(f"❌ Tool call failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Tool call error: {e}")
        return False
    
    # Test 3: Check authenticated user
    print("\n3. Checking authenticated user...")
    try:
        response = requests.get(f"{base_url}/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            user = data.get("authenticated_user")
            print(f"✅ Authenticated as user: {user}")
        else:
            print(f"❌ User check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User check error: {e}")
    
    print("\n✅ All authenticated tests passed!")
    return True


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-token":
        return test_with_token()
    else:
        return test_mcp_authentication()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
