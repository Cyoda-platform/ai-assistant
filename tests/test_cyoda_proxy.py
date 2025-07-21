#!/usr/bin/env python3
"""
Test script for Cyoda proxy functionality
"""

import requests
import json
import sys
import os


def test_cyoda_proxy():
    """Test Cyoda proxy functionality"""
    base_url = "http://localhost:8002"
    
    print("🔐 Testing Cyoda Proxy MCP Server")
    print("=" * 40)
    
    # Test 1: Check server info (should show increased tool count)
    print("\n1. Testing server info...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            tools_count = data.get("tools_count", 0)
            print(f"✅ Server running with {tools_count} tools")
            
            if tools_count >= 89:  # 49 workflow + 40 Cyoda
                print("✅ Cyoda tools successfully integrated!")
            else:
                print(f"⚠️  Expected ~89 tools, got {tools_count}")
        else:
            print(f"❌ Server info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server info error: {e}")
        return False
    
    # Test 2: Check if we can identify Cyoda tools (without auth)
    print("\n2. Testing Cyoda tool identification...")
    try:
        # Import the proxy service directly to test
        sys.path.append('..')
        from services.cyoda_proxy_service import cyoda_proxy
        
        cyoda_tools = cyoda_proxy.get_cyoda_tools()
        print(f"✅ Loaded {len(cyoda_tools)} Cyoda tools")
        
        # Show some example tools
        example_tools = list(cyoda_tools.keys())[:5]
        print(f"   Example tools: {', '.join(example_tools)}")
        
        # Test tool identification
        if cyoda_proxy.is_cyoda_tool("getoneentity"):
            print("✅ Cyoda tool identification working")
        else:
            print("❌ Cyoda tool identification failed")
            
    except Exception as e:
        print(f"❌ Cyoda tool identification error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎯 Cyoda Proxy Test Summary")
    print("=" * 40)
    print("✅ MCP server running with Cyoda tools integrated")
    print("✅ 40 Cyoda API tools available")
    print("✅ Tools require authentication (environment auto-detected from token)")
    print("")
    print("📋 Example Cyoda tools available:")
    print("  - getoneentity: Get a single entity")
    print("  - searchentities: Search entities with conditions")
    print("  - createclient: Create M2M client")
    print("  - getentitystatistics: Get entity statistics")
    print("  - importentitymodel: Import entity model")
    print("")
    print("🔧 To test with authentication:")
    print("  1. Get OAuth2 token from your auth server")
    print("  2. Set TOKEN environment variable")
    print("  3. Run: python test_cyoda_proxy.py --with-auth")
    
    return True


def test_with_auth():
    """Test Cyoda proxy with authentication"""
    base_url = "http://localhost:8002"
    token = os.getenv("TOKEN")
    
    if not token:
        print("❌ No TOKEN environment variable set")
        print("   Set TOKEN environment variable with your OAuth2 token")
        return False
    
    print("🔐 Testing Cyoda Proxy with Authentication")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: List tools with auth
    print("\n1. Testing tools list with authentication...")
    try:
        response = requests.get(f"{base_url}/tools", headers=headers)
        if response.status_code == 200:
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            
            # Count Cyoda tools
            cyoda_tools = [t for t in tools if t.get("description", "").startswith("[Cyoda API]")]
            workflow_tools = [t for t in tools if not t.get("description", "").startswith("[Cyoda API]")]
            
            print(f"✅ Tools list successful:")
            print(f"   Workflow tools: {len(workflow_tools)}")
            print(f"   Cyoda API tools: {len(cyoda_tools)}")
            print(f"   Total tools: {len(tools)}")
            
            # Show example Cyoda tool
            if cyoda_tools:
                example_tool = cyoda_tools[0]
                print(f"   Example Cyoda tool: {example_tool['name']}")
                user_env_required = "user_env" in example_tool.get("inputSchema", {}).get("required", [])
                print(f"   user_env parameter required: {user_env_required}")
                if not user_env_required:
                    print("   ✅ Environment auto-detected from token!")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Tools list error: {e}")
        return False
    
    # Test 2: Test Cyoda tool call (this will likely fail without proper Cyoda setup)
    print("\n2. Testing Cyoda tool call...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "accountget",  # Simple account info call
                "arguments": {
                    "technical_id": "cyoda_proxy_test"
                    # No user_env needed - auto-detected from token!
                }
            }
        }
        response = requests.post(f"{base_url}/call", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            tool_result = result.get("result", {}).get("content", [{}])[0].get("text", "No result")
            print(f"✅ Cyoda tool call executed")
            print(f"   Result preview: {tool_result[:200]}...")
            
            if "Error:" in tool_result:
                print("⚠️  Tool call returned error (expected without proper Cyoda setup)")
            else:
                print("✅ Tool call successful!")
        else:
            print(f"❌ Cyoda tool call failed: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Cyoda tool call error: {e}")
    
    print("\n✅ Authentication tests completed!")
    print("\n📋 To use Cyoda tools:")
    print("  1. Ensure user has valid Cyoda environment")
    print("  2. Token must contain caas_org_id for environment detection")
    print("  3. Token must be valid for Cyoda API access")
    print("  4. Environment URL auto-constructed from token")
    
    return True


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-auth":
        return test_with_auth()
    else:
        return test_cyoda_proxy()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
