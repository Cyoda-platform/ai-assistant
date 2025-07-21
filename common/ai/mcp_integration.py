"""
MCP (Model Context Protocol) integration for Google ADK
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from google.adk.tools.mcp_tool import MCPTool
from google.adk.agents import Agent

logger = logging.getLogger(__name__)


class McpServerConfig:
    """Configuration for MCP servers"""
    
    def __init__(self, name: str, command: List[str], args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}


class AdkMcpIntegration:
    """
    Integration class for adding MCP servers to Google ADK agents
    """
    
    def __init__(self):
        self.mcp_servers: Dict[str, McpServerConfig] = {}
        self.mcp_tools: List[MCPTool] = []
    
    def add_mcp_server(self, config: McpServerConfig):
        """Add an MCP server configuration"""
        self.mcp_servers[config.name] = config
        logger.info(f"Added MCP server configuration: {config.name}")
    
    def create_mcp_tools(self) -> List:
        """Create MCP tools from configured servers"""
        tools = []

        # Note: MCP tool creation requires proper session management setup
        # For now, we'll prepare the configuration but not create actual tools

        for server_name, config in self.mcp_servers.items():
            logger.info(f"MCP server configured: {server_name}")
            logger.info(f"  Command: {config.command}")
            logger.info(f"  Args: {config.args}")
            logger.info(f"  Env: {list(config.env.keys())}")

            # TODO: Create actual MCPTool when session management is implemented
            # This would require:
            # 1. Setting up MCP session manager
            # 2. Creating MCP base tool for the server
            # 3. Wrapping in MCPTool with proper parameters

        logger.info(f"MCP integration prepared for {len(self.mcp_servers)} servers")
        logger.info("Actual MCP tool creation will be implemented in future version")

        self.mcp_tools = tools
        return tools
    
    def get_predefined_servers(self) -> Dict[str, McpServerConfig]:
        """Get predefined MCP server configurations"""
        return {
            # File system operations
            "filesystem": McpServerConfig(
                name="filesystem",
                command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                args=["/path/to/allowed/directory"]
            ),
            
            # Git operations
            "git": McpServerConfig(
                name="git",
                command=["npx", "-y", "@modelcontextprotocol/server-git"],
                args=["--repository", "/path/to/git/repo"]
            ),
            
            # SQLite database
            "sqlite": McpServerConfig(
                name="sqlite",
                command=["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                args=["/path/to/database.db"]
            ),
            
            # Web search (Brave)
            "brave_search": McpServerConfig(
                name="brave_search",
                command=["npx", "-y", "@modelcontextprotocol/server-brave-search"],
                env={"BRAVE_API_KEY": "your-brave-api-key"}
            ),
            
            # GitHub integration
            "github": McpServerConfig(
                name="github",
                command=["npx", "-y", "@modelcontextprotocol/server-github"],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"}
            ),
            
            # Google Drive
            "gdrive": McpServerConfig(
                name="gdrive",
                command=["npx", "-y", "@modelcontextprotocol/server-gdrive"],
                env={"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json"}
            ),
            
            # Slack integration
            "slack": McpServerConfig(
                name="slack",
                command=["npx", "-y", "@modelcontextprotocol/server-slack"],
                env={
                    "SLACK_BOT_TOKEN": "your-slack-bot-token",
                    "SLACK_APP_TOKEN": "your-slack-app-token"
                }
            ),
            
            # PostgreSQL database
            "postgres": McpServerConfig(
                name="postgres",
                command=["npx", "-y", "@modelcontextprotocol/server-postgres"],
                env={"DATABASE_URL": "postgresql://user:password@localhost:5432/dbname"}
            ),
            
            # Puppeteer for web automation
            "puppeteer": McpServerConfig(
                name="puppeteer",
                command=["npx", "-y", "@modelcontextprotocol/server-puppeteer"]
            ),
            
            # Memory server for persistent context
            "memory": McpServerConfig(
                name="memory",
                command=["npx", "-y", "@modelcontextprotocol/server-memory"]
            )
        }
    
    def setup_common_servers(self, server_names: List[str], custom_configs: Optional[Dict[str, Dict[str, Any]]] = None):
        """Setup commonly used MCP servers"""
        predefined = self.get_predefined_servers()
        custom_configs = custom_configs or {}
        
        for server_name in server_names:
            if server_name in predefined:
                config = predefined[server_name]
                
                # Apply custom configurations if provided
                if server_name in custom_configs:
                    custom = custom_configs[server_name]
                    if "args" in custom:
                        config.args = custom["args"]
                    if "env" in custom:
                        config.env.update(custom["env"])
                
                self.add_mcp_server(config)
            else:
                logger.warning(f"Unknown predefined server: {server_name}")


def create_agent_with_mcp(
    model: str = "gemini-2.0-flash",
    name: str = "mcp_agent",
    instruction: str = "You are a helpful assistant with access to various tools and services.",
    mcp_servers: Optional[List[str]] = None,
    custom_mcp_configs: Optional[Dict[str, Dict[str, Any]]] = None,
    additional_tools: Optional[List] = None
) -> Agent:
    """
    Create an ADK agent with MCP server integration
    
    Args:
        model: The model to use
        name: Agent name
        instruction: Agent instruction
        mcp_servers: List of predefined MCP server names to include
        custom_mcp_configs: Custom configurations for MCP servers
        additional_tools: Additional non-MCP tools to include
    
    Returns:
        Configured Agent with MCP tools
    """
    
    # Initialize MCP integration
    mcp_integration = AdkMcpIntegration()
    
    # Setup MCP servers
    if mcp_servers:
        mcp_integration.setup_common_servers(mcp_servers, custom_mcp_configs)
    
    # Create MCP tools
    mcp_tools = mcp_integration.create_mcp_tools()
    
    # Combine with additional tools
    all_tools = mcp_tools + (additional_tools or [])
    
    # Create agent
    agent = Agent(
        model=model,
        name=name,
        instruction=instruction,
        tools=all_tools
    )
    
    logger.info(f"Created agent '{name}' with {len(mcp_tools)} MCP tools and {len(additional_tools or [])} additional tools")
    
    return agent


# Example configurations for your specific use case
def create_workflow_agent_with_mcp(existing_tools: List = None) -> Agent:
    """
    Create a workflow agent that combines your existing tools with MCP servers
    """
    
    # MCP servers that might be useful for your workflow system
    useful_servers = [
        "filesystem",  # File operations
        "memory",      # Persistent context
        "sqlite",      # Database operations
    ]
    
    # Custom configurations for your environment
    custom_configs = {
        "filesystem": {
            "args": ["/app/data"]  # Restrict to your app data directory
        },
        "sqlite": {
            "args": ["/app/data/workflow.db"]  # Your workflow database
        }
    }
    
    return create_agent_with_mcp(
        model="gemini-2.0-flash",
        name="workflow_mcp_agent",
        instruction="""
        You are a workflow assistant with access to file operations, memory, and database tools.
        You can help users manage workflows, store information persistently, and perform file operations.
        Always use the appropriate tools for the task at hand.
        """,
        mcp_servers=useful_servers,
        custom_mcp_configs=custom_configs,
        additional_tools=existing_tools
    )


# Integration with your existing GoogleAdkAgent
def enhance_adk_agent_with_mcp(agent_class):
    """
    Decorator to enhance your existing GoogleAdkAgent with MCP capabilities
    """
    
    class EnhancedAdkAgent(agent_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.mcp_integration = AdkMcpIntegration()
        
        def add_mcp_servers(self, server_names: List[str], custom_configs: Optional[Dict[str, Dict[str, Any]]] = None):
            """Add MCP servers to the agent"""
            self.mcp_integration.setup_common_servers(server_names, custom_configs)
        
        async def run_agent_with_mcp(self, methods_dict, technical_id, cls_instance, entity, tools, model, messages, mcp_servers=None, **kwargs):
            """Run agent with both existing tools and MCP tools"""
            
            # Create MCP tools if servers are specified
            mcp_tools = []
            if mcp_servers:
                self.add_mcp_servers(mcp_servers)
                mcp_tools = self.mcp_integration.create_mcp_tools()
            
            # Combine existing tools with MCP tools
            all_tools = (tools or []) + mcp_tools
            
            # Call the original run_agent method with combined tools
            return await super().run_agent(
                methods_dict, technical_id, cls_instance, entity, 
                all_tools, model, messages, **kwargs
            )
    
    return EnhancedAdkAgent
