#!/usr/bin/env python3
"""
Convert OpenAPI specification to MCP tools registry format
"""

import json
import sys
from typing import Dict, List, Any


def convert_openapi_type(openapi_type: str, format_type: str = None) -> str:
    """Convert OpenAPI type to JSON Schema type"""
    type_mapping = {
        "string": "string",
        "integer": "integer", 
        "number": "number",
        "boolean": "boolean",
        "array": "array",
        "object": "object"
    }
    
    # Handle format-specific types
    if openapi_type == "string" and format_type:
        if format_type in ["date", "date-time"]:
            return "string"
        elif format_type == "binary":
            return "string"
    
    return type_mapping.get(openapi_type, "string")


def extract_parameters_from_schema(schema: Dict[str, Any], required: List[str] = None) -> Dict[str, Any]:
    """Extract parameters from OpenAPI schema"""
    if not schema:
        return {"type": "object", "properties": {}, "required": []}
    
    properties = {}
    schema_required = required or schema.get("required", [])
    
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            prop_type = convert_openapi_type(
                prop_schema.get("type", "string"),
                prop_schema.get("format")
            )
            
            param = {
                "type": prop_type,
                "description": prop_schema.get("description", f"Parameter {prop_name}")
            }
            
            # Add enum if present
            if "enum" in prop_schema:
                param["enum"] = prop_schema["enum"]
            
            # Add default if present
            if "default" in prop_schema:
                param["default"] = prop_schema["default"]
            
            # Handle array items
            if prop_type == "array" and "items" in prop_schema:
                param["items"] = {
                    "type": convert_openapi_type(
                        prop_schema["items"].get("type", "string")
                    )
                }
            
            properties[prop_name] = param
    
    return {
        "type": "object",
        "properties": properties,
        "required": schema_required,
        "additionalProperties": False
    }


def convert_path_to_mcp_tool(path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    """Convert OpenAPI path operation to MCP tool"""
    
    # Generate tool name from operationId or path
    tool_name = operation.get("operationId")
    if not tool_name:
        # Generate from path and method
        clean_path = path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
        tool_name = f"{method}_{clean_path}"
    
    # Clean up tool name
    tool_name = tool_name.replace("-", "_").lower()
    
    # Get description
    description = operation.get("summary", operation.get("description", f"{method.upper()} {path}"))
    
    # Combine all parameters
    all_properties = {}
    all_required = []
    
    # Path parameters
    path_params = [p for p in operation.get("parameters", []) if p.get("in") == "path"]
    for param in path_params:
        param_name = param["name"]
        param_schema = param.get("schema", {})
        all_properties[param_name] = {
            "type": convert_openapi_type(param_schema.get("type", "string")),
            "description": param.get("description", f"Path parameter {param_name}")
        }
        if param.get("required", False):
            all_required.append(param_name)
    
    # Query parameters
    query_params = [p for p in operation.get("parameters", []) if p.get("in") == "query"]
    for param in query_params:
        param_name = param["name"]
        param_schema = param.get("schema", {})
        all_properties[param_name] = {
            "type": convert_openapi_type(param_schema.get("type", "string")),
            "description": param.get("description", f"Query parameter {param_name}")
        }
        if param.get("required", False):
            all_required.append(param_name)
    
    # Request body parameters
    request_body = operation.get("requestBody", {})
    if request_body:
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        if json_content and "schema" in json_content:
            body_schema = extract_parameters_from_schema(
                json_content["schema"],
                json_content["schema"].get("required", [])
            )
            # Merge body properties
            all_properties.update(body_schema["properties"])
            all_required.extend(body_schema["required"])
    
    # Add standard MCP parameters
    all_properties["technical_id"] = {
        "type": "string",
        "description": "Technical identifier for the operation",
        "default": f"cyoda_{tool_name}"
    }
    
    # Create MCP tool
    mcp_tool = {
        "name": tool_name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": all_properties,
            "required": all_required,
            "additionalProperties": False
        },
        "openapi_info": {
            "path": path,
            "method": method.upper(),
            "operationId": operation.get("operationId"),
            "tags": operation.get("tags", [])
        }
    }
    
    return mcp_tool


def convert_openapi_to_mcp(openapi_file: str, output_file: str):
    """Convert OpenAPI specification to MCP tools registry"""
    
    print(f"🔄 Converting {openapi_file} to MCP tools registry...")
    
    # Load OpenAPI spec
    with open(openapi_file, 'r') as f:
        openapi_spec = json.load(f)
    
    # Extract info
    info = openapi_spec.get("info", {})
    paths = openapi_spec.get("paths", {})
    
    # Convert paths to MCP tools
    mcp_tools = []
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                try:
                    mcp_tool = convert_path_to_mcp_tool(path, method, operation)
                    mcp_tools.append(mcp_tool)
                except Exception as e:
                    print(f"⚠️  Failed to convert {method.upper()} {path}: {e}")
    
    # Create MCP registry
    mcp_registry = {
        "info": {
            "title": f"{info.get('title', 'API')} MCP Tools",
            "description": f"MCP tools generated from {info.get('title', 'API')} OpenAPI specification",
            "version": info.get("version", "1.0"),
            "source": {
                "type": "openapi",
                "title": info.get("title"),
                "version": info.get("version"),
                "description": info.get("description")
            }
        },
        "tools": mcp_tools
    }
    
    # Save MCP registry
    with open(output_file, 'w') as f:
        json.dump(mcp_registry, f, indent=2)
    
    print(f"✅ Converted {len(mcp_tools)} tools to {output_file}")
    
    # Print summary by tags
    tags_summary = {}
    for tool in mcp_tools:
        tags = tool.get("openapi_info", {}).get("tags", ["Untagged"])
        for tag in tags:
            tags_summary[tag] = tags_summary.get(tag, 0) + 1
    
    print("\n📊 Tools by category:")
    for tag, count in sorted(tags_summary.items()):
        print(f"  📂 {tag}: {count} tools")
    
    return mcp_registry


def main():
    """Main function"""
    if len(sys.argv) != 3:
        print("Usage: python convert_openapi_to_mcp.py <openapi_file> <output_file>")
        print("Example: python convert_openapi_to_mcp.py cyoda_openapi_doc.json cyoda_mcp_tools.json")
        sys.exit(1)
    
    openapi_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        mcp_registry = convert_openapi_to_mcp(openapi_file, output_file)
        
        print(f"\n🎉 Successfully converted OpenAPI to MCP tools!")
        print(f"📁 Output file: {output_file}")
        print(f"🛠️  Total tools: {len(mcp_registry['tools'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
