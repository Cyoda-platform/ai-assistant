#!/usr/bin/env python3
"""
Working MCP Server using FastMCP with SSE transport
Provides Cyoda proxy endpoints and deployment tools
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from services.factory import ServicesFactory
from services.cyoda_proxy_service import cyoda_proxy
from common.utils.auth_utils import get_user_id
from common.config.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services and workflow
factory = ServicesFactory()
workflow = ChatWorkflow(
    dataset=factory.dataset,
    workflow_helper_service=factory.workflow_helper_service,
    entity_service=factory.entity_service,
    cyoda_auth_service=factory.cyoda_auth_service,
    workflow_converter_service=factory.workflow_converter_service,
    scheduler_service=factory.scheduler,
    data_service=factory.data_service,
    mock=False
)

# Create FastMCP server
mcp = FastMCP(name="AI-Assistant-MCP-Server")

def load_tools_registry() -> Dict[str, Dict[str, Any]]:
    """Load tools registry from JSON file"""
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        registry_path = os.path.join(project_root, "tools", "tools_registry.json")

        with open(registry_path, 'r') as f:
            registry_data = json.load(f)

        tools_dict = {}
        for tool in registry_data.get("tools", []):
            tools_dict[tool["name"]] = tool

        logger.info(f"Loaded {len(tools_dict)} tools from registry")
        return tools_dict
    except Exception as e:
        logger.error(f"Failed to load tools registry: {e}")
        return {}

def create_chat_entity(user_id: str = "mcp_user", workflow_cache: dict = None) -> ChatEntity:
    """Create a ChatEntity for tool calls"""
    return ChatEntity(
        user_id=user_id,
        memory_id=f"mcp_memory_{user_id}",
        workflow_cache=workflow_cache or {},
        scheduled_entities=[]
    )

def create_agentic_flow_entity(user_id: str = "mcp_user", workflow_cache: dict = None) -> AgenticFlowEntity:
    """Create an AgenticFlowEntity for tool calls"""
    return AgenticFlowEntity(
        user_id=user_id,
        memory_id=f"mcp_memory_{user_id}",
        workflow_cache=workflow_cache or {}
    )

# Load tools registry
tools_registry = load_tools_registry()

# Get all available tools but don't register them yet
workflow_tools = workflow._function_registry
cyoda_tools = cyoda_proxy.get_cyoda_tools()

def categorize_tools():
    """Organize tools into logical categories"""
    categories = {
        "🚀 Deployment & Environment": {
            "description": "Deploy applications and manage environments",
            "tools": []
        },
        "🏗️ Application Building": {
            "description": "Build and modify applications",
            "tools": []
        },
        "📁 File Operations": {
            "description": "File and repository management",
            "tools": []
        },
        "🌐 Web Operations": {
            "description": "Web search and content scraping",
            "tools": []
        },
        "⚙️ Workflow Management": {
            "description": "Create and manage workflows",
            "tools": []
        },
        "💬 Chat & State": {
            "description": "Chat management and state control",
            "tools": []
        },
        "🔧 Utilities": {
            "description": "General utility functions",
            "tools": []
        },
        "🏢 Cyoda Account": {
            "description": "Cyoda account and user management (requires user_token)",
            "tools": []
        },
        "📊 Cyoda Entities": {
            "description": "Cyoda entity operations (requires user_token)",
            "tools": []
        },
        "🔍 Cyoda Search": {
            "description": "Cyoda search and data operations (requires user_token)",
            "tools": []
        }
    }

    # Categorize workflow tools
    for tool_name in workflow_tools.keys():
        if any(keyword in tool_name.lower() for keyword in ["deploy", "env", "schedule"]):
            categories["🚀 Deployment & Environment"]["tools"].append(tool_name)
        elif any(keyword in tool_name.lower() for keyword in ["build", "app", "application", "edit", "add"]):
            categories["🏗️ Application Building"]["tools"].append(tool_name)
        elif any(keyword in tool_name.lower() for keyword in ["file", "save", "read", "clone", "delete", "repo"]):
            categories["📁 File Operations"]["tools"].append(tool_name)
        elif any(keyword in tool_name.lower() for keyword in ["web", "search", "scrape", "link"]):
            categories["🌐 Web Operations"]["tools"].append(tool_name)
        elif any(keyword in tool_name.lower() for keyword in ["workflow", "diagram", "convert", "validate"]):
            categories["⚙️ Workflow Management"]["tools"].append(tool_name)
        elif any(keyword in tool_name.lower() for keyword in ["chat", "lock", "unlock", "stage", "finish"]):
            categories["💬 Chat & State"]["tools"].append(tool_name)
        else:
            categories["🔧 Utilities"]["tools"].append(tool_name)

    # Categorize Cyoda tools
    for tool_name, tool_def in cyoda_tools.items():
        tags = tool_def.get("openapi_info", {}).get("tags", [""])
        tag = tags[0].lower() if tags else ""

        if "account" in tag or "user" in tag:
            categories["🏢 Cyoda Account"]["tools"].append(tool_name)
        elif "entity" in tag or "model" in tag:
            categories["📊 Cyoda Entities"]["tools"].append(tool_name)
        else:
            categories["🔍 Cyoda Search"]["tools"].append(tool_name)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v["tools"]}

# Create tool catalog
tool_categories = categorize_tools()

@mcp.tool()
def get_catalog() -> str:
    """Get the complete catalog of available tools organized by category"""
    result = "🛠️ AI Assistant Tool Catalog\n"
    result += "=" * 50 + "\n\n"

    total_tools = 0
    for category, info in tool_categories.items():
        tool_count = len(info["tools"])
        total_tools += tool_count

        result += f"{category} ({tool_count} tools)\n"
        result += f"📝 {info['description']}\n"
        result += "Tools: " + ", ".join(info["tools"][:5])  # Show first 5 tools
        if tool_count > 5:
            result += f" ... and {tool_count - 5} more"
        result += "\n\n"

    result += f"📊 Total: {total_tools} tools across {len(tool_categories)} categories\n\n"
    result += "💡 To use a tool, call it directly by name with required parameters.\n"
    result += "💡 For Cyoda tools, include 'user_token' parameter for authentication.\n"
    result += "💡 Use 'get_tool_info(tool_name)' for detailed information about any tool."

    return result

@mcp.tool()
def get_tool_info(tool_name: str) -> str:
    """Get detailed information about a specific tool"""
    # Check workflow tools
    if tool_name in workflow_tools:
        func = workflow_tools[tool_name]
        doc = func.__doc__ or "No description available"

        # Get tool info from registry if available
        if tool_name in tools_registry:
            tool_info = tools_registry[tool_name]
            params = tool_info.get("parameters", {}).get("properties", {})
            param_list = list(params.keys())
            return f"🛠️ Workflow Tool: {tool_name}\n\nDescription: {doc}\n\nParameters: {param_list}"
        else:
            return f"🛠️ Workflow Tool: {tool_name}\n\nDescription: {doc}\n\nParameters: Not available in registry"

    # Check Cyoda tools
    elif tool_name in cyoda_tools:
        tool_def = cyoda_tools[tool_name]
        description = tool_def.get("description", "No description available")
        params = tool_def.get("parameters", {}).get("properties", {})
        param_list = list(params.keys())

        return f"🌐 Cyoda API Tool: {tool_name}\n\nDescription: {description}\n\nParameters: {param_list}\n\nNote: Requires user_token parameter"

    else:
        return f"❌ Tool '{tool_name}' not found. Use 'get_catalog()' to see all available tools."

# Dynamic tool execution function
async def execute_any_tool(tool_name: str, **kwargs) -> str:
    """Execute any tool dynamically"""

    # Check if it's a workflow tool
    if tool_name in workflow_tools:
        try:
            func = workflow_tools[tool_name]

            # Extract standard parameters
            technical_id = kwargs.pop("technical_id", f"mcp_call_{tool_name}")
            workflow_cache = kwargs.pop("workflow_cache", {})
            user_id = "mcp_user"  # Default user for MCP calls

            # Determine entity type based on function signature
            import inspect
            sig = inspect.signature(func)
            entity_param = sig.parameters.get('entity')

            if entity_param and entity_param.annotation == AgenticFlowEntity:
                entity = create_agentic_flow_entity(user_id, workflow_cache)
            else:
                entity = create_chat_entity(user_id, workflow_cache)

            # Add repository info to workflow cache if provided
            if "repository_name" in kwargs:
                entity.workflow_cache["repository_name"] = kwargs.pop("repository_name")
            if "git_branch" in kwargs:
                entity.workflow_cache["git_branch"] = kwargs.pop("git_branch")

            # Call the function
            result = await func(technical_id=technical_id, entity=entity, **kwargs)
            return str(result)

        except Exception as e:
            logger.exception(f"Error executing workflow tool {tool_name}: {e}")
            return f"Error executing workflow tool {tool_name}: {str(e)}"

    # Check if it's a Cyoda tool
    elif tool_name in cyoda_tools:
        try:
            # Extract user token if provided
            user_token = kwargs.pop("user_token", None)

            if not user_token:
                return f"Error: Cyoda API tool '{tool_name}' requires authentication. Please provide a user_token parameter with your Cyoda access token."

            # Execute the Cyoda tool via proxy
            result = await cyoda_proxy.execute_cyoda_tool(tool_name, kwargs, user_token)
            return result

        except Exception as e:
            logger.exception(f"Error executing Cyoda tool {tool_name}: {e}")
            return f"Error executing Cyoda tool {tool_name}: {str(e)}"

    else:
        return f"❌ Tool '{tool_name}' not found. Use 'get_catalog()' to see all available tools."

# Add a universal tool executor for any tool in the catalog
@mcp.tool()
async def run_tool(tool_name: str, **parameters) -> str:
    """Execute any tool from the catalog by name with its parameters"""
    if not tool_name:
        return "Error: tool_name parameter is required. Use get_catalog() to see available tools."

    return await execute_any_tool(tool_name, **parameters)

# Only register catalog tools with FastMCP - other tools are handled dynamically
logger.info("Registering only catalog tools with FastMCP")
logger.info(f"Available but not registered: {len(workflow_tools)} workflow + {len(cyoda_tools)} Cyoda tools")

if __name__ == "__main__":
    print("🚀 Starting AI Assistant MCP Server...")
    print("📡 SSE endpoint: http://localhost:8000/sse")
    print(f"🛠️  Workflow tools: {len(workflow._function_registry)}")
    print(f"🌐 Cyoda API tools: {len(cyoda_tools)}")
    print("✅ Ready for Cursor integration!")

    asyncio.run(mcp.run_sse_async(host="0.0.0.0", port=8000))