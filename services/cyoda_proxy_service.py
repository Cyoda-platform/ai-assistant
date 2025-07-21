#!/usr/bin/env python3
"""
Cyoda API Proxy Service for MCP Tools
Forwards MCP tool calls to user's Cyoda environment
"""

import json
import logging
import httpx
import os
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from common.utils.cyoda_utils import build_cyoda_environment_url, get_user_cyoda_info

logger = logging.getLogger(__name__)


class CyodaProxyService:
    """Service to proxy MCP tool calls to Cyoda API"""
    
    def __init__(self):
        self.cyoda_tools_registry = self._load_cyoda_tools()
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def _load_cyoda_tools(self) -> Dict[str, Dict[str, Any]]:
        """Load Cyoda tools registry"""
        try:
            # Get the project root and construct path to tools directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cyoda_tools_path = os.path.join(project_root, "tools", "cyoda_mcp_tools.json")

            with open(cyoda_tools_path, 'r') as f:
                cyoda_data = json.load(f)
            
            tools_dict = {}
            for tool in cyoda_data.get("tools", []):
                tools_dict[tool["name"]] = tool
            
            logger.info(f"Loaded {len(tools_dict)} Cyoda tools")
            return tools_dict
        except Exception as e:
            logger.error(f"Failed to load Cyoda tools: {e}")
            return {}
    
    def is_cyoda_tool(self, tool_name: str) -> bool:
        """Check if tool is a Cyoda API tool"""
        return tool_name in self.cyoda_tools_registry
    
    def get_cyoda_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all Cyoda tools"""
        return self.cyoda_tools_registry
    
    async def execute_cyoda_tool(self, tool_name: str, arguments: Dict[str, Any],
                                user_token: str) -> str:
        """Execute Cyoda API tool via proxy"""

        if tool_name not in self.cyoda_tools_registry:
            raise ValueError(f"Unknown Cyoda tool: {tool_name}")

        # Get user's Cyoda environment from token
        cyoda_base_url = build_cyoda_environment_url(user_token)
        if not cyoda_base_url:
            return "Error: Cannot determine Cyoda environment from token. Missing or invalid caas_org_id."

        tool_def = self.cyoda_tools_registry[tool_name]
        openapi_info = tool_def["openapi_info"]

        # Extract OpenAPI info
        method = openapi_info["method"].upper()
        path = openapi_info["path"]

        # Remove MCP-specific parameters
        api_arguments = {k: v for k, v in arguments.items()
                        if k not in ['technical_id', 'user_id', 'workflow_cache']}

        # Build Cyoda API URL - add /api prefix if not present
        if not path.startswith('/api/'):
            api_path = f"/api{path}"
        else:
            api_path = path

        cyoda_url = urljoin(cyoda_base_url, api_path)
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # Make a copy of arguments to avoid modifying the original
            api_arguments_copy = api_arguments.copy()

            # Handle path parameters
            final_url = self._substitute_path_parameters(cyoda_url, api_arguments_copy)

            # Separate query parameters and body parameters
            query_params, body_params = self._separate_parameters(tool_def, api_arguments_copy)

            # Get user Cyoda info for logging
            cyoda_info = get_user_cyoda_info(user_token)
            org_id = cyoda_info.get('caas_org_id', 'unknown')

            logger.info(f"Proxying {method} {final_url} to Cyoda environment: {org_id}")
            logger.debug(f"Query params: {query_params}")
            logger.debug(f"Body params: {body_params}")
            
            # Make API call based on method
            if method == "GET":
                response = await self.http_client.get(
                    final_url, 
                    headers=headers, 
                    params=query_params
                )
            elif method == "POST":
                response = await self.http_client.post(
                    final_url, 
                    headers=headers, 
                    params=query_params,
                    json=body_params if body_params else None
                )
            elif method == "PUT":
                response = await self.http_client.put(
                    final_url, 
                    headers=headers, 
                    params=query_params,
                    json=body_params if body_params else None
                )
            elif method == "DELETE":
                response = await self.http_client.delete(
                    final_url, 
                    headers=headers, 
                    params=query_params
                )
            elif method == "PATCH":
                response = await self.http_client.patch(
                    final_url, 
                    headers=headers, 
                    params=query_params,
                    json=body_params if body_params else None
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle response
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    # Try to parse as JSON
                    result_data = response.json()
                    return json.dumps(result_data, indent=2)
                except:
                    # Return as text if not JSON
                    return response.text
            else:
                # Handle error response with more details
                error_msg = f"Cyoda API error {response.status_code}: {response.text}"
                logger.error(f"HTTP {method} {final_url} failed: {error_msg}")
                logger.error(f"Request query params: {query_params}")
                logger.error(f"Request body params: {body_params}")

                # Try to parse error response as JSON for better error messages
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "message" in error_data:
                        return f"Cyoda API Error ({response.status_code}): {error_data['message']}"
                except:
                    pass

                return f"Cyoda API Error ({response.status_code}): {response.text}"
                
        except httpx.TimeoutException:
            error_msg = f"Timeout calling Cyoda API: {final_url}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Error calling Cyoda API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def _substitute_path_parameters(self, url: str, arguments: Dict[str, Any]) -> str:
        """Substitute path parameters in URL"""
        final_url = url

        # Find path parameters in URL (e.g., {entityId})
        import re
        path_params = re.findall(r'\{([^}]+)\}', url)

        for param in path_params:
            if param in arguments:
                param_value = str(arguments[param])
                final_url = final_url.replace(f"{{{param}}}", param_value)
                # Remove from arguments so it's not used as query param
                del arguments[param]
                logger.debug(f"Substituted path parameter {param} = {param_value}")
            else:
                logger.warning(f"Missing required path parameter: {param}")
                # Don't fail here, let the API return the error

        return final_url
    
    def _separate_parameters(self, tool_def: Dict[str, Any], arguments: Dict[str, Any]) -> tuple:
        """Separate query parameters from body parameters based on OpenAPI spec"""

        # Get parameter definitions from the tool
        parameters_schema = tool_def.get("parameters", {})
        properties = parameters_schema.get("properties", {})

        query_params = {}
        body_params = {}

        # Separate parameters based on their intended use
        for param_name, param_value in arguments.items():
            param_def = properties.get(param_name, {})
            param_description = param_def.get("description", "").lower()

            # Heuristics to determine parameter type:
            # 1. If description mentions "query", it's a query parameter
            # 2. If it's a simple type (string, number, boolean) and not entity data, likely query
            # 3. If it's complex data or mentions "entity", likely body
            # 4. Common query parameter names

            is_query_param = (
                "query" in param_description or
                "parameter" in param_description or
                param_name in [
                    "transactionWindow", "transactionTimeoutMillis", "waitForConsistencyAfter",
                    "limit", "offset", "page", "size", "sort", "filter", "search",
                    "modelVersion", "pointInTime", "includeDeleted", "format"
                ] or
                (param_def.get("type") in ["integer", "boolean", "string"] and
                 "entity" not in param_description and
                 "data" not in param_description and
                 len(str(param_value)) < 1000)  # Simple values, not large data
            )

            if is_query_param:
                query_params[param_name] = param_value
            else:
                body_params[param_name] = param_value

        return query_params, body_params
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Global instance
cyoda_proxy = CyodaProxyService()
