"""
MCP Server Manager - Handles starting/stopping MCP servers alongside the main app
"""

import asyncio
import logging
import os
import signal
import subprocess
import threading
import time
from typing import Dict, List, Optional
import uvicorn
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class McpServerManager:
    """Manages MCP servers lifecycle alongside the main application"""
    
    def __init__(self):
        self.mcp_processes: Dict[str, subprocess.Popen] = {}
        self.http_server_task: Optional[asyncio.Task] = None
        self.is_running = False
        
    async def start_mcp_servers(self):
        """Start all configured MCP servers"""
        logger.info("🚀 Starting MCP servers...")
        
        # Start HTTP MCP server
        await self._start_http_mcp_server()
        
        # Start other MCP servers if needed
        await self._start_stdio_mcp_servers()
        
        self.is_running = True
        logger.info("✅ All MCP servers started successfully")
    
    async def _start_http_mcp_server(self):
        """Start the Universal MCP server in a separate task"""
        try:
            # Import here to avoid circular imports
            from mcp_servers.universal_tools_server import app as mcp_app

            # Create uvicorn config
            config = uvicorn.Config(
                mcp_app,
                host="0.0.0.0",
                port=8002,
                log_level="info",
                access_log=False  # Reduce noise in logs
            )

            # Start server in background task
            server = uvicorn.Server(config)
            self.http_server_task = asyncio.create_task(server.serve())

            # Give server time to start
            await asyncio.sleep(1)

            logger.info("✅ Universal MCP server started on http://localhost:8002")

        except Exception as e:
            logger.error(f"❌ Failed to start Universal MCP server: {e}")
            raise
    
    async def _start_stdio_mcp_servers(self):
        """Start stdio-based MCP servers if configured"""
        # This is where you could start additional MCP servers
        # For now, we'll just log that they're available
        
        # Get project root from environment or default
        project_root = os.getenv("PROJECT_ROOT", "/app")

        stdio_servers = {
            "filesystem": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "args": [project_root],
                "description": "File system operations"
            },
            "memory": {
                "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                "args": [],
                "description": "Persistent memory storage"
            }
        }
        
        logger.info(f"📋 Available stdio MCP servers: {list(stdio_servers.keys())}")
        logger.info("💡 Stdio servers will be started on-demand by ADK agent")
    
    async def stop_mcp_servers(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping MCP servers...")
        
        # Stop HTTP server
        if self.http_server_task and not self.http_server_task.done():
            self.http_server_task.cancel()
            try:
                await self.http_server_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ HTTP MCP server stopped")
        
        # Stop stdio processes
        for name, process in self.mcp_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ Stopped MCP server: {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️  Force killed MCP server: {name}")
            except Exception as e:
                logger.error(f"❌ Error stopping MCP server {name}: {e}")
        
        self.mcp_processes.clear()
        self.is_running = False
        logger.info("✅ All MCP servers stopped")
    
    def get_server_status(self) -> Dict[str, str]:
        """Get status of all MCP servers"""
        status = {
            "http_server": "running" if self.http_server_task and not self.http_server_task.done() else "stopped",
            "stdio_servers": len(self.mcp_processes),
            "manager_running": self.is_running
        }
        return status


# Global MCP server manager instance
mcp_manager = McpServerManager()


async def startup_mcp_servers():
    """Startup function for MCP servers"""
    try:
        await mcp_manager.start_mcp_servers()
    except Exception as e:
        logger.error(f"Failed to start MCP servers: {e}")
        raise


async def shutdown_mcp_servers():
    """Shutdown function for MCP servers"""
    try:
        await mcp_manager.stop_mcp_servers()
    except Exception as e:
        logger.error(f"Error stopping MCP servers: {e}")


@asynccontextmanager
async def mcp_lifespan():
    """Async context manager for MCP server lifecycle"""
    try:
        await startup_mcp_servers()
        yield
    finally:
        await shutdown_mcp_servers()


def check_mcp_server_health() -> bool:
    """Check if MCP servers are healthy"""
    try:
        import requests
        response = requests.get("http://localhost:8002/", timeout=2)
        return response.status_code == 200
    except:
        return False


# Convenience functions for integration
async def ensure_mcp_servers_running():
    """Ensure MCP servers are running, start if not"""
    if not mcp_manager.is_running:
        await startup_mcp_servers()


def get_mcp_server_info() -> Dict[str, str]:
    """Get MCP server connection information"""
    return {
        "http_url": "http://localhost:8002",
        "websocket_url": "ws://localhost:8002/ws",
        "tools_endpoint": "http://localhost:8002/tools",
        "call_endpoint": "http://localhost:8002/call",
        "status": "running" if mcp_manager.is_running else "stopped"
    }
