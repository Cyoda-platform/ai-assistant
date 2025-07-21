#!/usr/bin/env python3
"""
Tool to add MCP tools to existing workflow JSON configurations
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any


def get_mcp_tool_templates() -> Dict[str, Dict]:
    """Get predefined MCP tool templates"""
    return {
        "filesystem": {
            "type": "mcp",
            "mcp": {
                "server_name": "filesystem",
                "description": "Access file system operations - read, write, list files and directories",
                "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                "args": ["/app/data"],
                "env": {}
            }
        },
        "memory": {
            "type": "mcp",
            "mcp": {
                "server_name": "memory",
                "description": "Persistent memory storage for maintaining context between conversations",
                "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
                "args": [],
                "env": {}
            }
        },
        "sqlite": {
            "type": "mcp",
            "mcp": {
                "server_name": "sqlite",
                "description": "SQLite database operations - query and modify database",
                "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite"],
                "args": ["/app/data/workflow.db"],
                "env": {}
            }
        },
        "brave_search": {
            "type": "mcp",
            "mcp": {
                "server_name": "brave_search",
                "description": "Web search using Brave Search API",
                "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
                "args": [],
                "env": {
                    "BRAVE_API_KEY": "${BRAVE_API_KEY}"
                }
            }
        },
        "github": {
            "type": "mcp",
            "mcp": {
                "server_name": "github",
                "description": "GitHub integration - repository operations, issues, pull requests",
                "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
                "args": [],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
                }
            }
        }
    }


def add_mcp_tools_to_workflow(workflow_data: Dict, mcp_tools: List[str]) -> Dict:
    """Add MCP tools to workflow configuration"""
    templates = get_mcp_tool_templates()
    
    # Find all tool arrays in the workflow
    def add_tools_recursive(obj):
        if isinstance(obj, dict):
            if "tools" in obj and isinstance(obj["tools"], list):
                # Add MCP tools to this tools array
                for tool_name in mcp_tools:
                    if tool_name in templates:
                        # Check if tool already exists
                        existing_names = []
                        for tool in obj["tools"]:
                            if tool.get("type") == "mcp":
                                existing_names.append(tool.get("mcp", {}).get("server_name"))
                        
                        if tool_name not in existing_names:
                            obj["tools"].append(templates[tool_name])
                            print(f"  Added MCP tool: {tool_name}")
                        else:
                            print(f"  MCP tool already exists: {tool_name}")
            
            # Recursively process nested objects
            for value in obj.values():
                add_tools_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                add_tools_recursive(item)
    
    add_tools_recursive(workflow_data)
    return workflow_data


def process_workflow_file(file_path: Path, mcp_tools: List[str], backup: bool = True) -> bool:
    """Process a single workflow file"""
    try:
        print(f"Processing: {file_path}")
        
        # Read the workflow file
        with open(file_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2)
            print(f"  Backup created: {backup_path}")
        
        # Add MCP tools
        updated_workflow = add_mcp_tools_to_workflow(workflow_data, mcp_tools)
        
        # Write updated workflow
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_workflow, f, indent=2)
        
        print(f"  ✅ Updated successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False


def find_workflow_files(directory: Path) -> List[Path]:
    """Find all workflow JSON files in directory"""
    workflow_files = []
    
    for file_path in directory.rglob("*.json"):
        # Skip backup files
        if file_path.name.endswith('.backup'):
            continue
            
        # Check if it looks like a workflow file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and "workflow_name" in data and "states" in data:
                    workflow_files.append(file_path)
        except:
            continue
    
    return workflow_files


def main():
    """Main function"""
    print("🔧 MCP Tools Workflow Configuration Tool")
    print("=" * 50)
    
    # Available MCP tools
    available_tools = list(get_mcp_tool_templates().keys())
    print(f"Available MCP tools: {', '.join(available_tools)}")
    
    # Get command line arguments
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python tools/add_mcp_to_workflow.py <workflow_file_or_directory> [mcp_tools...]")
        print("\nExamples:")
        print("  # Add memory and filesystem to specific file")
        print("  python tools/add_mcp_to_workflow.py common/workflow/config/agentic_flow_entity/chat_entity/chat_entity.json memory filesystem")
        print("\n  # Add memory to all workflow files in directory")
        print("  python tools/add_mcp_to_workflow.py common/workflow/config/ memory")
        print("\n  # Add multiple tools to all workflows")
        print("  python tools/add_mcp_to_workflow.py common/workflow/config/ memory filesystem sqlite")
        return
    
    target_path = Path(sys.argv[1])
    mcp_tools = sys.argv[2:] if len(sys.argv) > 2 else ["memory", "filesystem"]
    
    # Validate MCP tools
    invalid_tools = [tool for tool in mcp_tools if tool not in available_tools]
    if invalid_tools:
        print(f"❌ Invalid MCP tools: {invalid_tools}")
        print(f"Available tools: {available_tools}")
        return
    
    print(f"Target: {target_path}")
    print(f"MCP tools to add: {mcp_tools}")
    print()
    
    # Process files
    if target_path.is_file():
        # Single file
        success = process_workflow_file(target_path, mcp_tools)
        if success:
            print("\n✅ File processed successfully!")
        else:
            print("\n❌ Failed to process file")
    
    elif target_path.is_dir():
        # Directory - find all workflow files
        workflow_files = find_workflow_files(target_path)
        
        if not workflow_files:
            print(f"❌ No workflow files found in {target_path}")
            return
        
        print(f"Found {len(workflow_files)} workflow files:")
        for file_path in workflow_files:
            print(f"  - {file_path}")
        
        print()
        
        # Process each file
        success_count = 0
        for file_path in workflow_files:
            if process_workflow_file(file_path, mcp_tools):
                success_count += 1
        
        print(f"\n📊 Results: {success_count}/{len(workflow_files)} files processed successfully")
        
        if success_count == len(workflow_files):
            print("✅ All files processed successfully!")
        else:
            print("⚠️  Some files failed to process")
    
    else:
        print(f"❌ Path not found: {target_path}")
    
    print("\n💡 Next steps:")
    print("1. Review the updated workflow files")
    print("2. Set up environment variables for MCP tools (if needed)")
    print("3. Test the workflows with MCP tools enabled")
    print("4. See MCP_WORKFLOW_CONFIGURATION_GUIDE.md for more details")


if __name__ == "__main__":
    main()
