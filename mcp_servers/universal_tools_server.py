#!/usr/bin/env python3
"""
Universal MCP server that exposes ALL tools from the ChatWorkflow registry.
This uses the elegant registry pattern to automatically discover and expose tools.
"""

import asyncio
import json
import logging
import sys
import os
import inspect
import time
from typing import Any, Dict, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
import httpx
import secrets
import urllib.parse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your project imports
from entity.chat.workflow import ChatWorkflow
from entity.chat.chat import ChatEntity
from entity.model import AgenticFlowEntity
from services.factory import ServicesFactory
from common.utils.auth_utils import get_user_id
from common.utils.request_utils import extract_bearer_token, validate_with_cyoda
from common.exception.exceptions import InvalidTokenException
from common.config.config import config
from services.cyoda_proxy_service import cyoda_proxy
from common.utils.cyoda_utils import build_cyoda_environment_url, get_user_cyoda_info

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Universal Tools MCP Server", description="HTTP/WebSocket MCP server for all workflow tools")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# MCP Request/Response models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: int
    result: Any = None
    error: Dict[str, Any] = None

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

# Security
security = HTTPBearer(auto_error=False)

# OAuth state management (in production, use Redis or database)
oauth_states = {}  # {state: {client_id, redirect_uri, timestamp}}
user_tokens = {}   # {session_id: {token, user_id, expires_at}}


async def get_current_user_for_workflow_tools(credentials: HTTPAuthorizationCredentials = Depends(security)) -> tuple:
    """Extract and validate user from token for workflow tools - validate against user's environment"""
    if not config.ENABLE_AUTH:
        return "mcp_user", None  # Default user when auth is disabled

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        # Extract user ID from token
        user_id = await get_user_id(f"Bearer {credentials.credentials}")
        if user_id.startswith('guest.'):
            raise HTTPException(status_code=403, detail="Please sign in to proceed")

        # For workflow tools: validate token against user's specific environment
        cyoda_url = build_cyoda_environment_url(credentials.credentials)
        if cyoda_url:
            # Validate with user's specific Cyoda environment
            await validate_with_cyoda_environment(credentials.credentials, cyoda_url)
            logger.debug(f"Token validated against user environment: {cyoda_url}")
        else:
            # Fallback to standard validation if no environment detected
            await validate_with_cyoda(credentials.credentials)
            logger.debug("Token validated against standard endpoint")

        return user_id, credentials.credentials
    except InvalidTokenException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_for_cyoda_tools(credentials: HTTPAuthorizationCredentials = Depends(security)) -> tuple:
    """Extract user from token for Cyoda tools - no validation, let Cyoda API validate"""
    if not config.ENABLE_AUTH:
        return "mcp_user", None  # Default user when auth is disabled

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        # For Cyoda tools: just extract user ID, don't validate token
        # Let Cyoda API validate the token directly
        user_id = await get_user_id(f"Bearer {credentials.credentials}")
        if user_id.startswith('guest.'):
            raise HTTPException(status_code=403, detail="Please sign in to proceed")

        logger.debug("Token extracted for Cyoda API - validation will be done by Cyoda")
        return user_id, credentials.credentials
    except InvalidTokenException as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error extracting user for Cyoda tools: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def validate_with_cyoda_environment(token: str, cyoda_url: str):
    """Validate token with specific Cyoda environment"""
    try:
        # Use the environment-specific validation endpoint
        validation_url = f"{cyoda_url}/api/auth/validate"  # Adjust endpoint as needed

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            response = await client.get(validation_url, headers=headers, timeout=10.0)

            if response.status_code == 401:
                raise InvalidTokenException(f"Token validation failed against {cyoda_url}")

        logger.debug(f"Token successfully validated against {cyoda_url}")

    except httpx.TimeoutException:
        logger.error(f"Timeout validating token against {cyoda_url}")
        raise InvalidTokenException("Token validation timeout")
    except Exception as e:
        logger.error(f"Error validating token against {cyoda_url}: {e}")
        raise InvalidTokenException(f"Token validation failed: {str(e)}")


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> tuple:
    """Extract user from token, but don't require auth if disabled"""
    if not config.ENABLE_AUTH:
        return "mcp_user", None

    if not credentials:
        return "anonymous_user", None

    try:
        return await get_current_user_for_workflow_tools(credentials)
    except HTTPException:
        return "anonymous_user", None


async def get_current_user_smart(tool_name: str, credentials: HTTPAuthorizationCredentials) -> tuple:
    """Smart authentication based on tool type"""
    if not config.ENABLE_AUTH:
        return "mcp_user", None

    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    # Check if this is a Cyoda API tool
    if cyoda_proxy.is_cyoda_tool(tool_name):
        # For Cyoda tools: minimal validation, let Cyoda API handle it
        return await get_current_user_for_cyoda_tools(credentials)
    else:
        # For workflow tools: validate against user's environment
        return await get_current_user_for_workflow_tools(credentials)


def create_chat_entity(user_id: str, workflow_cache: dict = None) -> ChatEntity:
    """Create a ChatEntity for tool calls"""
    return ChatEntity(
        user_id=user_id,
        memory_id=f"mcp_memory_{user_id}",
        workflow_cache=workflow_cache or {},
        scheduled_entities=[]
    )


def create_agentic_flow_entity(user_id: str, workflow_cache: dict = None) -> AgenticFlowEntity:
    """Create an AgenticFlowEntity for tool calls"""
    return AgenticFlowEntity(
        user_id=user_id,
        memory_id=f"mcp_memory_{user_id}",
        workflow_cache=workflow_cache or {}
    )


def load_tools_registry() -> Dict[str, Dict[str, Any]]:
    """Load tools registry from JSON file"""
    try:
        # Use environment variable or default path
        project_root = os.getenv("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        registry_path = os.path.join(project_root, "tools", "tools_registry.json")

        with open(registry_path, 'r') as f:
            registry_data = json.load(f)

        # Convert to dict keyed by tool name for easy lookup
        tools_dict = {}
        for tool in registry_data.get("tools", []):
            tools_dict[tool["name"]] = tool

        logger.info(f"Loaded {len(tools_dict)} tools from registry at {registry_path}")
        return tools_dict
    except Exception as e:
        logger.error(f"Failed to load tools registry: {e}")
        return {}


def discover_tools() -> List[Dict[str, Any]]:
    """Discover tools from workflow registry, tools registry, and Cyoda API"""
    tools = []
    tools_registry = load_tools_registry()

    # Add workflow tools
    for func_name, func in workflow._function_registry.items():
        try:
            if func_name in tools_registry:
                # Use detailed schema from tools registry
                registry_tool = tools_registry[func_name]
                tool = {
                    "name": func_name,
                    "description": registry_tool["description"],
                    "inputSchema": registry_tool["parameters"]
                }
            else:
                # Fallback to basic schema from function
                description = func.__doc__ or f"Execute {func_name} function"
                description = description.strip().split('\n')[0]  # First line only

                tool = {
                    "name": func_name,
                    "description": description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
                logger.warning(f"Tool {func_name} not found in registry, using basic schema")

            tools.append(tool)

        except Exception as e:
            logger.warning(f"Could not process function {func_name}: {e}")

    # Add Cyoda API tools
    cyoda_tools = cyoda_proxy.get_cyoda_tools()
    for tool_name, tool_def in cyoda_tools.items():
        try:
            # Use original Cyoda tool parameters (no user_env needed)
            cyoda_tool = {
                "name": tool_name,
                "description": f"[Cyoda API] {tool_def['description']}",
                "inputSchema": tool_def["parameters"]
            }
            tools.append(cyoda_tool)

        except Exception as e:
            logger.warning(f"Could not process Cyoda tool {tool_name}: {e}")

    workflow_count = len([t for t in tools if not t['description'].startswith('[Cyoda API]')])
    cyoda_count = len([t for t in tools if t['description'].startswith('[Cyoda API]')])

    logger.info(f"Discovered {len(tools)} tools ({workflow_count} workflow + {cyoda_count} Cyoda API)")
    return tools


# Discover all tools automatically
DISCOVERED_TOOLS = discover_tools()


async def execute_tool(name: str, arguments: Dict[str, Any], user_id: str = "mcp_user",
                      user_token: str = None) -> str:
    """Execute any tool from the workflow registry or Cyoda API"""

    # Check if this is a Cyoda API tool
    if cyoda_proxy.is_cyoda_tool(name):
        return await execute_cyoda_tool(name, arguments, user_id, user_token)

    # Handle workflow tools
    return await execute_workflow_tool(name, arguments, user_id)


async def execute_cyoda_tool(name: str, arguments: Dict[str, Any], user_id: str,
                           user_token: str) -> str:
    """Execute Cyoda API tool via proxy"""

    if not user_token:
        return "Error: Authentication token required for Cyoda API calls"

    try:
        result = await cyoda_proxy.execute_cyoda_tool(name, arguments, user_token)
        return result
    except Exception as e:
        logger.exception(f"Error executing Cyoda tool {name}: {e}")
        return f"Error executing Cyoda tool {name}: {str(e)}"


async def execute_workflow_tool(name: str, arguments: Dict[str, Any], user_id: str) -> str:
    """Execute workflow tool from the registry"""

    # Get standard parameters
    technical_id = arguments.pop("technical_id", f"mcp_call_{name}")
    workflow_cache = arguments.pop("workflow_cache", {})

    # Check if function exists in registry
    if name not in workflow._function_registry:
        return f"Unknown tool: {name}"

    try:
        func = workflow._function_registry[name]

        # Determine entity type based on function signature
        sig = inspect.signature(func)
        entity_param = sig.parameters.get('entity')

        if entity_param and entity_param.annotation == AgenticFlowEntity:
            entity = create_agentic_flow_entity(user_id, workflow_cache)
        else:
            entity = create_chat_entity(user_id, workflow_cache)

        # Add repository info to workflow cache if provided
        if "repository_name" in arguments:
            entity.workflow_cache["repository_name"] = arguments.pop("repository_name")
        if "git_branch" in arguments:
            entity.workflow_cache["git_branch"] = arguments.pop("git_branch")

        # Call the function
        result = await func(technical_id=technical_id, entity=entity, **arguments)

        return str(result)

    except Exception as e:
        logger.exception(f"Error executing workflow tool {name}: {e}")
        return f"Error executing workflow tool {name}: {str(e)}"


# HTTP endpoints
# OAuth endpoints
@app.get("/auth/login")
async def oauth_login(request: Request, client_id: str = None, redirect_uri: str = None):
    """Initiate OAuth login flow"""

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store OAuth state
    oauth_states[state] = {
        "client_id": client_id or "mcp_client",
        "redirect_uri": redirect_uri or "http://localhost:3000/callback",
        "timestamp": time.time()
    }

    # Build OAuth authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": os.getenv("OAUTH2_CLIENT_ID", "your_client_id"),
        "redirect_uri": f"{request.url.scheme}://{request.url.netloc}/auth/callback",
        "scope": "openid profile email",
        "state": state
    }

    auth_url = f"{os.getenv('OAUTH2_ISSUER', 'https://your-auth-server.com')}/oauth/authorize"
    full_auth_url = f"{auth_url}?{urllib.parse.urlencode(auth_params)}"

    # Return login page with redirect
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Assistant MCP - Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .container {{ max-width: 400px; margin: 0 auto; }}
            .btn {{ background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 20px 0; }}
            .btn:hover {{ background: #005a87; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Assistant MCP</h1>
            <p>Access to 95+ tools including workflow automation and Cyoda API integration.</p>
            <p>Please login to continue:</p>
            <a href="{full_auth_url}" class="btn">Login with OAuth2</a>
            <p><small>You will be redirected to your authentication provider.</small></p>
        </div>
        <script>
            // Auto-redirect after 3 seconds
            setTimeout(() => {{
                window.location.href = "{full_auth_url}";
            }}, 3000);
        </script>
    </body>
    </html>
    """)


@app.get("/auth/callback")
async def oauth_callback(code: str, state: str, error: str = None):
    """Handle OAuth callback"""

    if error:
        return HTMLResponse(f"""
        <html><body>
            <h1>Authentication Error</h1>
            <p>Error: {error}</p>
            <p><a href="/auth/login">Try again</a></p>
        </body></html>
        """, status_code=400)

    # Verify state
    if state not in oauth_states:
        return HTMLResponse("""
        <html><body>
            <h1>Invalid State</h1>
            <p>Invalid or expired authentication state.</p>
            <p><a href="/auth/login">Start over</a></p>
        </body></html>
        """, status_code=400)

    oauth_state = oauth_states.pop(state)

    try:
        # Exchange code for token
        token_data = await exchange_code_for_token(code)

        # Generate session ID
        session_id = secrets.token_urlsafe(32)

        # Store user session
        user_tokens[session_id] = {
            "token": token_data["access_token"],
            "user_id": token_data.get("user_id", "unknown"),
            "expires_at": time.time() + token_data.get("expires_in", 3600)
        }

        # Return success page with session info
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .container {{ max-width: 500px; margin: 0 auto; }}
                .success {{ color: #28a745; }}
                .code {{ background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">✅ Login Successful!</h1>
                <p>You are now authenticated with AI Assistant MCP.</p>
                <p>Session ID:</p>
                <div class="code">{session_id}</div>
                <p><small>Your IDE should automatically detect this authentication.</small></p>
                <p><a href="/">Return to MCP Server</a></p>
            </div>
        </body>
        </html>
        """)

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return HTMLResponse(f"""
        <html><body>
            <h1>Authentication Failed</h1>
            <p>Error: {str(e)}</p>
            <p><a href="/auth/login">Try again</a></p>
        </body></html>
        """, status_code=500)


async def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""

    token_url = f"{os.getenv('OAUTH2_ISSUER', 'https://your-auth-server.com')}/oauth/token"

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("OAUTH2_CLIENT_ID", "your_client_id"),
        "client_secret": os.getenv("OAUTH2_CLIENT_SECRET", "your_client_secret"),
        "redirect_uri": f"http://localhost:8002/auth/callback"  # This should match the registered redirect URI
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            token_url,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")

        return response.json()


@app.get("/auth/status")
async def auth_status(session_id: str = None):
    """Check authentication status"""

    if not session_id or session_id not in user_tokens:
        return {"authenticated": False, "message": "No valid session"}

    session = user_tokens[session_id]

    if time.time() > session["expires_at"]:
        del user_tokens[session_id]
        return {"authenticated": False, "message": "Session expired"}

    return {
        "authenticated": True,
        "user_id": session["user_id"],
        "expires_at": session["expires_at"]
    }


@app.get("/")
async def root(user_info: tuple = Depends(get_current_user_optional)):
    """Root endpoint with server info"""
    user_id, user_token = user_info
    return {
        "name": "Universal Tools MCP Server",
        "version": "1.0.0",
        "protocol": "mcp",
        "authentication": {
            "required": config.ENABLE_AUTH,
            "type": "Bearer Token",
            "description": "OAuth2 Bearer token required for authenticated endpoints"
        },
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        },
        "endpoints": {
            "http": "http://localhost:8002",
            "websocket": "ws://localhost:8002/ws",
            "tools": "/tools",
            "call": "/call"
        },
        "tools_count": len(DISCOVERED_TOOLS),
        "authenticated_user": user_id if user_id != "anonymous_user" else None,
        "tool_categories": get_detailed_tool_categories()
    }


def get_detailed_tool_categories() -> dict:
    """Get detailed tool categories including Cyoda API tools"""

    # Separate workflow and Cyoda tools
    workflow_tools = [t for t in DISCOVERED_TOOLS if not t["description"].startswith("[Cyoda API]")]
    cyoda_tools = [t for t in DISCOVERED_TOOLS if t["description"].startswith("[Cyoda API]")]

    # Get Cyoda tool categories from the proxy
    cyoda_categories = {}
    cyoda_tools_registry = cyoda_proxy.get_cyoda_tools()

    for tool_name, tool_def in cyoda_tools_registry.items():
        tags = tool_def.get("openapi_info", {}).get("tags", ["Uncategorized"])
        for tag in tags:
            # Clean up tag name for category
            category_name = f"cyoda_{tag.lower().replace(' ', '_').replace(',', '').replace('-', '_')}"
            if category_name not in cyoda_categories:
                cyoda_categories[category_name] = 0
            cyoda_categories[category_name] += 1

    # Build complete categories
    categories = {
        # High-level categories
        "workflow_tools": len(workflow_tools),
        "cyoda_api_tools": len(cyoda_tools),

        # Workflow tool categories
        "workflow_deployment": len([t for t in workflow_tools if "deploy" in t["name"].lower()]),
        "workflow_application": len([t for t in workflow_tools if "app" in t["name"].lower()]),
        "workflow_web": len([t for t in workflow_tools if "web" in t["name"].lower()]),
        "workflow_utility": len([t for t in workflow_tools if t["name"] in ["get_weather", "get_humidity", "get_user_info"]]),

        # Add Cyoda categories
        **cyoda_categories
    }

    return categories


@app.get("/tools")
async def list_tools(user_info: tuple = Depends(get_current_user_for_workflow_tools)):
    """List all discovered tools"""
    user_id, user_token = user_info
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": DISCOVERED_TOOLS
        }
    }


@app.get("/tools/categories")
async def list_tools_by_category():
    """List tools organized by category"""
    categories = {
        "file_operations": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["file", "save", "read", "clone", "delete"])],
        "web_operations": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["web", "search", "link", "scrape"])],
        "deployment": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["deploy", "build", "schedule"])],
        "application": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["app", "application", "build_general"])],
        "workflow": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["workflow", "diagram", "convert"])],
        "state_management": [t for t in DISCOVERED_TOOLS if any(keyword in t["name"].lower() for keyword in ["stage", "chat", "lock", "unlock", "finish"])],
        "utility": [t for t in DISCOVERED_TOOLS if t["name"] in ["get_weather", "get_humidity", "get_user_info", "init_chats", "fail_workflow"]]
    }
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "categories": categories,
            "summary": {cat: len(tools) for cat, tools in categories.items()}
        }
    }


@app.post("/call")
async def call_tool(request: MCPRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Call any tool via HTTP POST"""
    try:
        if request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={"tools": DISCOVERED_TOOLS}
            )
        
        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32602, "message": "Missing tool name"}
                )

            # Use smart authentication based on tool type
            user_id, user_token = await get_current_user_smart(tool_name, credentials)

            result = await execute_tool(tool_name, arguments, user_id, user_token)

            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )
        
        else:
            return MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Unknown method: {request.method}"}
            )
    
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return MCPResponse(
            id=request.id,
            error={"code": -32603, "message": f"Internal error: {str(e)}"}
        )


@app.get("/sse")
async def sse_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Server-Sent Events endpoint for MCP communication"""

    async def event_stream():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"

        # Keep connection alive and handle MCP requests
        try:
            while True:
                # In a real implementation, this would handle incoming MCP requests
                # For now, just keep the connection alive
                await asyncio.sleep(1)
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': time.time()})}\n\n"
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Authorization"
        }
    )


@app.get("/mcp")
async def mcp_info(user_info: tuple = Depends(get_current_user_optional)):
    """MCP server information endpoint"""
    user_id, user_token = user_info

    return {
        "name": "Universal Tools MCP Server",
        "version": "1.0.0",
        "protocol": "mcp",
        "transport": "http",
        "authentication": {
            "required": config.ENABLE_AUTH,
            "type": "oauth2",
            "login_url": "/auth/login"
        },
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        },
        "endpoints": {
            "mcp": "/mcp (POST for requests, GET for info)",
            "login": "/auth/login",
            "callback": "/auth/callback",
            "status": "/auth/status"
        },
        "tools_count": len(DISCOVERED_TOOLS),
        "authenticated_user": user_id if user_id != "anonymous_user" else None
    }


@app.post("/mcp")
async def mcp_endpoint(
    request: MCPRequest,
    session_id: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Main MCP endpoint for IDE communication with OAuth session support (Cursor compatible)"""

    user_id = None
    user_token = None

    # Try session-based authentication first
    if session_id and session_id in user_tokens:
        session = user_tokens[session_id]
        if time.time() <= session["expires_at"]:
            user_id = session["user_id"]
            user_token = session["token"]
        else:
            del user_tokens[session_id]

    # Fallback to bearer token authentication
    if not user_id and credentials:
        try:
            user_id, user_token = await get_current_user_smart(
                request.params.get("name", "unknown"), credentials
            )
        except HTTPException:
            pass

    # If no authentication and auth is required, return auth challenge
    if not user_id and config.ENABLE_AUTH:
        return MCPResponse(
            id=request.id,
            error={
                "code": -32001,
                "message": "Authentication required",
                "data": {
                    "auth_url": "/auth/login",
                    "type": "oauth2"
                }
            }
        )

    # Use default user if auth is disabled
    if not user_id:
        user_id = "mcp_user"

    # Handle MCP request
    try:
        if request.method == "tools/list":
            tools = discover_tools()
            return MCPResponse(
                id=request.id,
                result={"tools": tools}
            )

        elif request.method == "tools/call":
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})

            if not tool_name:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32602, "message": "Missing tool name"}
                )

            result = await execute_tool(tool_name, arguments, user_id, user_token)

            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": result}]}
            )

        else:
            return MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Unknown method: {request.method}"}
            )

    except Exception as e:
        logger.exception(f"MCP endpoint error: {e}")
        return MCPResponse(
            id=request.id,
            error={"code": -32603, "message": f"Internal error: {str(e)}"}
        )


@app.options("/mcp")
async def mcp_options():
    """Handle CORS preflight for MCP endpoint"""
    return {"status": "ok"}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP communication"""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                request_data = json.loads(data)
                request = MCPRequest(**request_data)
                
                if request.method == "tools/list":
                    response = MCPResponse(
                        id=request.id,
                        result={"tools": DISCOVERED_TOOLS}
                    )
                
                elif request.method == "tools/call":
                    tool_name = request.params.get("name")
                    arguments = request.params.get("arguments", {})
                    
                    if not tool_name:
                        response = MCPResponse(
                            id=request.id,
                            error={"code": -32602, "message": "Missing tool name"}
                        )
                    else:
                        result = await execute_tool(tool_name, arguments)
                        response = MCPResponse(
                            id=request.id,
                            result={"content": [{"type": "text", "text": result}]}
                        )
                
                else:
                    response = MCPResponse(
                        id=request.id,
                        error={"code": -32601, "message": f"Unknown method: {request.method}"}
                    )
                
                await websocket.send_text(response.model_dump_json())
                
            except json.JSONDecodeError:
                error_response = MCPResponse(
                    id=0,
                    error={"code": -32700, "message": "Parse error"}
                )
                await websocket.send_text(error_response.model_dump_json())
            
            except Exception as e:
                logger.exception(f"Error processing WebSocket message: {e}")
                error_response = MCPResponse(
                    id=0,
                    error={"code": -32603, "message": f"Internal error: {str(e)}"}
                )
                await websocket.send_text(error_response.model_dump_json())
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    print("🚀 Starting Universal Tools MCP Server...")
    print("📡 HTTP endpoint: http://localhost:8002")
    print("🔌 WebSocket endpoint: ws://localhost:8002/ws")
    print("📋 Tools endpoint: http://localhost:8002/tools")
    print("🔧 Call endpoint: http://localhost:8002/call")
    print(f"🛠️  Discovered tools: {len(DISCOVERED_TOOLS)}")
    
    # Print tool categories
    categories = {}
    for tool in DISCOVERED_TOOLS:
        for keyword, category in [
            ("file", "File Operations"),
            ("web", "Web Operations"), 
            ("deploy", "Deployment"),
            ("app", "Application"),
            ("workflow", "Workflow"),
            ("stage", "State Management")
        ]:
            if keyword in tool["name"].lower():
                categories.setdefault(category, 0)
                categories[category] += 1
                break
        else:
            categories.setdefault("Utility", 0)
            categories["Utility"] += 1
    
    for category, count in categories.items():
        print(f"  📂 {category}: {count} tools")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
