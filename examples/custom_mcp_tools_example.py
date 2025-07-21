#!/usr/bin/env python3
"""
Example showing how to create custom MCP tools and integrate them with Google ADK.
This demonstrates the complete workflow from creating MCP servers to using them in agents.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ai.adk_agent import AdkAgent
from entity.model import AIMessage, ModelConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomMcpToolsExample:
    """Example class showing custom MCP tools integration"""
    
    def __init__(self):
        self.agent = None
    
    async def create_agent_with_custom_mcp(self):
        """Create ADK agent with custom MCP tools"""
        print("🤖 Creating ADK agent with custom MCP tools...")
        
        # Create agent with our test server
        self.agent = AdkAgent(mcp_servers=['test_server'])
        
        print(f"✅ Agent created with MCP servers: {self.agent.mcp_servers}")
        return self.agent
    
    def create_workflow_with_mcp_tools(self):
        """Create a workflow configuration that uses MCP tools"""
        print("📝 Creating workflow with MCP tools...")
        
        # Define tools that combine function tools and MCP tools
        tools = [
            # Regular function tool
            {
                "type": "function",
                "function": {
                    "name": "get_user_info",
                    "description": "Get user information like environment URL, branch name etc",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_request": {
                                "type": "string",
                                "description": "The user's request for information"
                            }
                        },
                        "required": ["user_request"],
                        "additionalProperties": False
                    }
                }
            },
            # Custom MCP tool
            {
                "type": "mcp",
                "mcp": {
                    "server_name": "test_server",
                    "description": "Custom test server with calculation, time, and analysis functions",
                    "command": ["python", "mcp_servers/test_server.py"],
                    "args": [],
                    "env": {}
                }
            }
        ]
        
        # Mock methods for function tools
        methods_dict = {
            "get_user_info": self.mock_get_user_info
        }
        
        return tools, methods_dict
    
    async def mock_get_user_info(self, cls_instance, technical_id, entity, **kwargs):
        """Mock implementation of get_user_info"""
        user_request = kwargs.get('user_request', 'general info')
        return f"User info for '{user_request}': Environment=dev, Branch=main, User=test_user"
    
    async def test_tool_parsing(self):
        """Test how tools are parsed and configured"""
        print("🔧 Testing tool parsing...")
        
        if not self.agent:
            await self.create_agent_with_custom_mcp()
        
        tools, methods_dict = self.create_workflow_with_mcp_tools()
        
        # Test tool parsing
        parsed_tools = self.agent._create_function_tools(tools, methods_dict)
        
        print(f"✅ Parsed {len(parsed_tools)} tools:")
        
        for tool in parsed_tools:
            if tool.get('type') == 'function':
                print(f"  📋 Function tool: {tool['name']}")
            elif tool.get('type') == 'mcp':
                print(f"  🔌 MCP tool: {tool['server_name']} - {tool['description']}")
        
        return parsed_tools
    
    async def test_mcp_server_configuration(self):
        """Test MCP server configuration"""
        print("⚙️  Testing MCP server configuration...")
        
        if not self.agent:
            await self.create_agent_with_custom_mcp()
        
        # Test MCP tool creation
        mcp_tools = self.agent._create_mcp_tools()
        
        print(f"✅ Configured {len(mcp_tools)} MCP servers:")
        
        for tool in mcp_tools:
            if isinstance(tool, dict):
                print(f"  🔌 {tool.get('server_name', 'unknown')}: {tool.get('description', 'no description')}")
                print(f"    Command: {tool.get('command', [])}")
            else:
                print(f"  🔌 MCPTool instance: {type(tool).__name__}")
        
        return mcp_tools
    
    def create_example_messages(self):
        """Create example messages that would use MCP tools"""
        return [
            AIMessage(
                role="user",
                content="Please calculate the sum of 25 and 17, then tell me the current time."
            ),
            AIMessage(
                role="user", 
                content="Can you analyze this text: 'The quick brown fox jumps over the lazy dog' and give me statistics?"
            ),
            AIMessage(
                role="user",
                content="Create a greeting for 'John' in Spanish, then check the status of workflow 'WF-123'."
            )
        ]
    
    async def simulate_agent_workflow(self):
        """Simulate how the agent would handle MCP tool requests"""
        print("🎭 Simulating agent workflow with MCP tools...")
        
        if not self.agent:
            await self.create_agent_with_custom_mcp()
        
        tools, methods_dict = self.create_workflow_with_mcp_tools()
        messages = self.create_example_messages()
        model = ModelConfig(model_name="gemini-2.0-flash")
        
        print(f"✅ Workflow simulation setup:")
        print(f"  - Agent: {type(self.agent).__name__}")
        print(f"  - Tools: {len(tools)} (function + MCP)")
        print(f"  - Messages: {len(messages)}")
        print(f"  - Model: {model.model_name}")
        
        # Test tool configuration
        parsed_tools = self.agent._create_function_tools(tools, methods_dict)
        
        print(f"\n📋 Tool Configuration Results:")
        function_tools = [t for t in parsed_tools if t.get('type') == 'function']
        mcp_tools = [t for t in parsed_tools if t.get('type') == 'mcp']
        
        print(f"  - Function tools: {len(function_tools)}")
        print(f"  - MCP tools: {len(mcp_tools)}")
        
        # Show what each message would trigger
        print(f"\n💬 Message Analysis:")
        for i, message in enumerate(messages, 1):
            print(f"  {i}. '{message.content[:50]}...'")
            if "calculate" in message.content.lower():
                print(f"     → Would use MCP calculate_sum tool")
            if "time" in message.content.lower():
                print(f"     → Would use MCP get_current_time tool")
            if "analyze" in message.content.lower():
                print(f"     → Would use MCP analyze_text tool")
            if "greeting" in message.content.lower():
                print(f"     → Would use MCP create_greeting tool")
            if "workflow" in message.content.lower():
                print(f"     → Would use MCP workflow_status tool")
        
        return True
    
    def create_production_mcp_config(self):
        """Create a production-ready MCP configuration example"""
        print("🏭 Creating production MCP configuration...")
        
        config = {
            "mcp_servers": {
                "custom_tools": {
                    "command": ["python", "/app/mcp_servers/custom_tools_server.py"],
                    "description": "Custom business logic tools",
                    "env": {
                        "DATABASE_URL": "${DATABASE_URL}",
                        "API_KEY": "${CUSTOM_API_KEY}"
                    }
                },
                "filesystem": {
                    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                    "args": ["/app/data"],
                    "description": "File system operations"
                },
                "database": {
                    "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                    "args": ["/app/data/production.db"],
                    "description": "Production database access"
                }
            },
            "agent_config": {
                "default_mcp_servers": ["custom_tools", "filesystem"],
                "production_mcp_servers": ["custom_tools", "database"],
                "development_mcp_servers": ["custom_tools", "filesystem", "database"]
            }
        }
        
        # Save configuration
        with open("examples/production_mcp_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Production MCP configuration saved to examples/production_mcp_config.json")
        return config


async def run_custom_mcp_example():
    """Run the complete custom MCP tools example"""
    print("🚀 Starting Custom MCP Tools Example...")
    print("=" * 60)
    
    example = CustomMcpToolsExample()
    
    try:
        # Test 1: Create agent with MCP
        await example.create_agent_with_custom_mcp()
        
        # Test 2: Test tool parsing
        await example.test_tool_parsing()
        
        # Test 3: Test MCP server configuration
        await example.test_mcp_server_configuration()
        
        # Test 4: Simulate workflow
        await example.simulate_agent_workflow()
        
        # Test 5: Create production config
        example.create_production_mcp_config()
        
        print("\n" + "=" * 60)
        print("🎉 Custom MCP Tools Example Completed Successfully!")
        print("=" * 60)
        
        print("\n📋 What was demonstrated:")
        print("✅ Creating ADK agent with custom MCP servers")
        print("✅ Configuring MCP tools in workflow JSON")
        print("✅ Parsing and integrating MCP tools with function tools")
        print("✅ Simulating agent workflow with MCP tool usage")
        print("✅ Creating production-ready MCP configurations")
        
        print("\n🔄 Next steps:")
        print("1. Set up authentication for Google ADK")
        print("2. Deploy MCP servers in your environment")
        print("3. Test with real agent execution")
        print("4. Add more custom MCP tools as needed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        logger.exception("Custom MCP example error")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_custom_mcp_example())
    
    if success:
        print("\n✅ Custom MCP tools integration example completed!")
        print("Check the examples/ directory for configuration files.")
    else:
        print("\n❌ Example failed. Please check the errors above.")
