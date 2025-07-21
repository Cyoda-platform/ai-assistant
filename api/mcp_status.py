"""
MCP Status API endpoints
"""

from quart import Blueprint, jsonify
from services.mcp_server_manager import mcp_manager, get_mcp_server_info, check_mcp_server_health

mcp_status_bp = Blueprint('mcp_status', __name__, url_prefix='/api/mcp')


@mcp_status_bp.route('/status', methods=['GET'])
async def get_mcp_status():
    """Get MCP servers status"""
    try:
        status = mcp_manager.get_server_status()
        server_info = get_mcp_server_info()
        health = check_mcp_server_health()
        
        return jsonify({
            "status": "success",
            "mcp_servers": {
                "manager_running": status["manager_running"],
                "http_server_status": status["http_server"],
                "stdio_servers_count": status["stdio_servers"],
                "health_check": health,
                "endpoints": {
                    "http": server_info["http_url"],
                    "websocket": server_info["websocket_url"],
                    "tools": server_info["tools_endpoint"],
                    "call": server_info["call_endpoint"]
                }
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@mcp_status_bp.route('/health', methods=['GET'])
async def mcp_health_check():
    """Simple health check for MCP servers"""
    try:
        health = check_mcp_server_health()
        if health:
            return jsonify({
                "status": "healthy",
                "mcp_server": "running",
                "endpoint": "http://localhost:8002"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "mcp_server": "not responding",
                "endpoint": "http://localhost:8002"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@mcp_status_bp.route('/tools', methods=['GET'])
async def list_mcp_tools():
    """List available MCP tools"""
    try:
        import requests
        response = requests.get("http://localhost:8002/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools = data.get('result', {}).get('tools', [])
            
            return jsonify({
                "status": "success",
                "tools_count": len(tools),
                "tools": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": list(tool.get("inputSchema", {}).get("properties", {}).keys())
                    }
                    for tool in tools
                ]
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"MCP server responded with status {response.status_code}"
            }), 502
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
