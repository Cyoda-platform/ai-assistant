#!/usr/bin/env python3
"""
MCP Server entry point for command-line execution
This allows the MCP server to be launched as: python -m mcp_servers.universal_tools_server
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("PROJECT_ROOT", str(project_root))
os.environ.setdefault("PYTHONPATH", str(project_root))

def main():
    """Main entry point for MCP server"""
    try:
        # Import the FastAPI app
        from mcp_servers.universal_tools_server import app
        
        # Get configuration from environment
        host = os.getenv("MCP_HOST", "127.0.0.1")
        port = int(os.getenv("MCP_SERVER_PORT", "8002"))
        log_level = os.getenv("MCP_LOG_LEVEL", "info")
        
        print(f"🚀 Starting Universal MCP Server on {host}:{port}")
        print(f"📁 Project root: {project_root}")
        print(f"🔐 Authentication: {'enabled' if os.getenv('ENABLE_AUTH', 'false').lower() == 'true' else 'disabled'}")
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
