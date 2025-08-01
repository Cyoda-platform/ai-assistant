# Tool Management Strategy

## Overview

We're implementing a **hybrid approach** that preserves your existing `tools_registry.json` while adding support for workflow-specific tools. This gives you the best of both worlds.

## 🏗️ Architecture

### Two-Tier Tool System

1. **Production Tools** (`tools/tools_registry.json`)
   - Stable, well-tested tools used across multiple workflows
   - Centralized management and versioning
   - Your existing 50+ tools remain unchanged

2. **Workflow-Specific Tools** (`tools/individual_files/`)
   - Tools generated during workflow migration
   - Experimental or workflow-specific functionality
   - Easy to modify and iterate on

## 📁 Directory Structure

```
tools/
├── tools_registry.json          # Production tools (existing)
├── cyoda_mcp_tools.json         # Cyoda-specific tools (existing)
├── individual_tool_1.json       # Workflow-specific tool
├── individual_tool_2.json       # Workflow-specific tool
└── workflow_specific/           # Optional: organize by workflow
    ├── api_edit_tools.json
    └── data_processing_tools.json
```

## 🔄 Tool Loading Priority

The `ToolLoader` searches in this order:

1. **tools_registry.json** (highest priority)
2. **Individual tool files** (fallback)

This means:
- Existing tools in registry are always used
- New workflow tools don't conflict with existing ones
- Easy migration path for promoting workflow tools to registry

## 📋 Migration Behavior

### Current Migration Script

```python
# When migrating workflows:
if tool_exists_in_registry(tool_name):
    print(f"Tool '{tool_name}' already exists in registry, skipping")
    # Uses existing registry tool
else:
    # Creates individual tool file
    create_individual_tool_file(tool_name, tool_config)
```

### Example Migration Results

**For your `generating_gen_app_workflow_java.json`:**

- ✅ `add_application_resource` - **Found in registry**, uses existing
- ✅ `convert_workflow_to_dto` - **Found in registry**, uses existing  
- ⚠️ `new_workflow_tool` - **Not in registry**, creates individual file

## 🛠️ Tool Format Compatibility

### Registry Format (Existing)
```json
{
  "tools": [
    {
      "name": "add_application_resource",
      "description": "Add application resource file",
      "parameters": {
        "type": "object",
        "properties": { ... }
      }
    }
  ]
}
```

### Individual Tool Format (New)
```json
{
  "type": "function",
  "function": {
    "name": "workflow_specific_tool",
    "description": "Tool description",
    "parameters": {
      "type": "object",
      "properties": { ... }
    }
  }
}
```

### Automatic Conversion

The `ToolLoader` automatically converts between formats:

```python
# Registry format → Standard format
registry_tool = {
  "name": "tool_name",
  "description": "...",
  "parameters": {...}
}

# Becomes:
standard_tool = {
  "type": "function", 
  "function": {
    "name": "tool_name",
    "description": "...",
    "parameters": {...}
  }
}
```

## 🎯 Benefits

### ✅ **Preserves Existing Investment**
- Your 50+ tools in `tools_registry.json` remain unchanged
- No disruption to existing workflows
- Existing tool loading logic continues to work

### ✅ **Enables New Architecture**  
- Workflow-specific tools for specialized use cases
- Easy experimentation with new tools
- Clean separation between stable and experimental tools

### ✅ **Migration Path**
- Workflow tools can be promoted to registry when stable
- Easy to identify which tools are workflow-specific
- Gradual migration without breaking changes

### ✅ **Flexibility**
- Mix registry tools and individual tools in same workflow
- Override registry tools with workflow-specific versions if needed
- Easy tool discovery and management

## 🔧 Usage Examples

### Agent Configuration
```json
{
  "type": "agent",
  "tools": [
    {"name": "web_search"},              // From registry
    {"name": "add_application_resource"}, // From registry  
    {"name": "workflow_specific_tool"}   // From individual file
  ]
}
```

### Tool Loading in Code
```python
from processors.loaders.tool_loader import ToolLoader

loader = ToolLoader(".")

# Loads from registry if available, falls back to individual file
tool = loader.load_tool("add_application_resource")

# Lists all tools from both sources
all_tools = loader.list_tools()
```

## 📈 Recommended Workflow

### 1. **Migration Phase**
```bash
# Migrate existing workflows
python migrate_workflows.py workflow.json

# Result: Uses registry tools, creates individual files for new tools
```

### 2. **Development Phase**
- Test workflows with mix of registry and individual tools
- Iterate on workflow-specific tools as needed
- Validate tool functionality

### 3. **Promotion Phase** (Optional)
```python
# When workflow tool is stable, promote to registry
def promote_tool_to_registry(tool_name):
    individual_tool = load_individual_tool(tool_name)
    add_to_registry(individual_tool)
    remove_individual_file(tool_name)
```

## 🚀 Implementation Status

### ✅ **Completed**
- Hybrid ToolLoader with registry + individual file support
- Migration script respects existing registry
- Automatic format conversion
- Tool discovery across both sources

### 🔄 **Next Steps**
1. Test migration with your existing workflows
2. Validate tool loading works with existing registry
3. Review generated individual tool files
4. Consider promoting stable workflow tools to registry

## 💡 **Recommendation**

**Keep your existing `tools_registry.json` approach** - it's working well for you! The new architecture simply adds workflow-specific tools as a complement, not a replacement.

This hybrid approach gives you:
- **Stability** for production tools
- **Flexibility** for workflow experimentation  
- **Zero disruption** to existing systems
- **Easy migration path** for the future
