#!/usr/bin/env python3
"""
Test script for MCP (Model Context Protocol) integration with Google ADK
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_nodejs():
    """Check if Node.js is installed"""
    print("🔍 Checking Node.js installation...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js found: {version}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js not found")
        return False


def check_npx():
    """Check if npx is available"""
    print("🔍 Checking npx availability...")
    try:
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npx found: {version}")
            return True
        else:
            print("❌ npx not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ npx not found")
        return False


def test_mcp_server_availability():
    """Test if MCP servers can be installed"""
    print("🧪 Testing MCP server availability...")
    
    servers_to_test = [
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-filesystem"
    ]
    
    results = {}
    
    for server in servers_to_test:
        print(f"  Testing {server}...")
        try:
            # Test if we can get help from the server
            result = subprocess.run(
                ['npx', '-y', server, '--help'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                print(f"  ✅ {server} available")
                results[server] = True
            else:
                print(f"  ❌ {server} failed: {result.stderr}")
                results[server] = False
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {server} timeout")
            results[server] = False
        except Exception as e:
            print(f"  ❌ {server} error: {e}")
            results[server] = False
    
    return results


async def test_mcp_import():
    """Test if MCP tools can be imported"""
    print("📦 Testing MCP imports...")
    try:
        from google.adk.tools.mcp_tool import MCPTool
        print("✅ MCP tools import successful")
        return True
    except ImportError as e:
        print(f"❌ MCP tools import failed: {e}")
        print("💡 Make sure you have the latest version of google-adk")
        return False


async def test_mcp_agent_creation():
    """Test creating an agent with MCP tools"""
    print("🤖 Testing MCP agent creation...")
    try:
        from common.ai.ai_agent import GoogleAdkAgent
        
        # Create agent with MCP servers
        agent = GoogleAdkAgent(mcp_servers=['memory'])
        print("✅ MCP agent creation successful")
        return True
    except Exception as e:
        print(f"❌ MCP agent creation failed: {e}")
        logger.exception("MCP agent creation error")
        return False


async def test_mcp_integration():
    """Test the MCP integration module"""
    print("🔧 Testing MCP integration module...")
    try:
        from common.ai.mcp_integration import AdkMcpIntegration, create_agent_with_mcp
        
        # Test integration class
        integration = AdkMcpIntegration()
        predefined = integration.get_predefined_servers()
        
        print(f"✅ MCP integration module loaded")
        print(f"  Available predefined servers: {len(predefined)}")
        
        # Test agent creation with MCP
        agent = create_agent_with_mcp(
            mcp_servers=[],  # Empty list to avoid Node.js dependency in test
            additional_tools=[]
        )
        print("✅ MCP agent creation via integration successful")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        logger.exception("MCP integration test error")
        return False


async def test_environment_setup():
    """Test environment configuration for MCP"""
    print("🌍 Testing environment setup...")
    
    # Check for MCP-related environment variables
    mcp_vars = {
        'MCP_SERVERS': os.getenv('MCP_SERVERS'),
        'MCP_FILESYSTEM_PATH': os.getenv('MCP_FILESYSTEM_PATH'),
        'MCP_SQLITE_DB': os.getenv('MCP_SQLITE_DB'),
        'BRAVE_API_KEY': os.getenv('BRAVE_API_KEY'),
        'GITHUB_PERSONAL_ACCESS_TOKEN': os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    }
    
    configured_vars = {k: v for k, v in mcp_vars.items() if v is not None}
    
    if configured_vars:
        print("✅ MCP environment variables found:")
        for var, value in configured_vars.items():
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
    else:
        print("ℹ️  No MCP environment variables configured (this is optional)")
    
    return True


def create_mcp_env_template():
    """Create MCP environment template"""
    template = """# MCP (Model Context Protocol) Configuration

# Basic MCP servers (comma-separated list)
MCP_SERVERS=memory,filesystem

# Filesystem server configuration
MCP_FILESYSTEM_PATH=/app/data

# SQLite server configuration  
MCP_SQLITE_DB=/app/data/workflow.db

# Optional: Web search (requires API key)
# BRAVE_API_KEY=your-brave-api-key-here

# Optional: GitHub integration (requires personal access token)
# GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token-here

# Optional: Google Drive integration
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
"""
    
    filename = '.env.mcp.template'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write(template)
        print(f"✅ Created {filename}")
    else:
        print(f"ℹ️  {filename} already exists")


async def run_all_tests():
    """Run all MCP tests"""
    print("🚀 Starting MCP Integration Tests...")
    print("=" * 50)
    
    # System requirements tests
    system_tests = [
        ("Node.js Installation", check_nodejs),
        ("npx Availability", check_npx),
    ]
    
    # MCP-specific tests
    mcp_tests = [
        ("MCP Server Availability", test_mcp_server_availability),
        ("MCP Import Test", test_mcp_import),
        ("MCP Agent Creation", test_mcp_agent_creation),
        ("MCP Integration Module", test_mcp_integration),
        ("Environment Setup", test_environment_setup),
    ]
    
    all_tests = system_tests + mcp_tests
    results = []
    
    for test_name, test_func in all_tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Create environment template
    print(f"\n--- Creating MCP Environment Template ---")
    create_mcp_env_template()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MCP INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if isinstance(result, dict):
            # Handle server availability results
            server_passed = sum(1 for v in result.values() if v)
            server_total = len(result)
            status = "✅ PASS" if server_passed > 0 else "❌ FAIL"
            print(f"{status} {test_name} ({server_passed}/{server_total} servers)")
            if server_passed > 0:
                passed += 1
        else:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is ready to use.")
        print("\n🔄 Next steps:")
        print("1. Configure MCP servers in your environment (see .env.mcp.template)")
        print("2. Enable MCP servers in your agent configuration")
        print("3. Test with your actual workflow")
    else:
        print("⚠️  Some tests failed. Please address the issues:")
        
        # Check specific failures
        failed_tests = [name for name, result in results if not result]
        
        if "Node.js Installation" in failed_tests or "npx Availability" in failed_tests:
            print("\n🔧 Install Node.js:")
            print("  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -")
            print("  sudo apt-get install -y nodejs")
        
        if "MCP Import Test" in failed_tests:
            print("\n📦 Update Google ADK:")
            print("  pip install --upgrade google-adk")
        
        if "MCP Server Availability" in failed_tests:
            print("\n🌐 Check internet connection and npm registry access")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    
    print(f"\n{'='*60}")
    if success:
        print("✅ MCP integration is ready!")
        print("See MCP_SETUP_GUIDE.md for detailed usage instructions.")
    else:
        print("❌ Please fix the failing tests before using MCP integration.")
    
    sys.exit(0 if success else 1)
