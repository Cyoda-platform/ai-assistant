"""
Export Utilities

Utilities for exporting Python configurations to JSON format
and managing the hybrid JSON+Python workflow system.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def export_to_json(component_config: Dict[str, Any], output_path: Path) -> bool:
    """Export a component configuration to JSON file"""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(component_config, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Failed to export {output_path}: {e}")
        return False


def export_workflow_to_json(workflow_config, output_dir: Path) -> bool:
    """Export workflow configuration to JSON"""
    try:
        json_config = workflow_config.workflow.to_json_dict()
        output_path = output_dir / "workflow.json"
        return export_to_json(json_config, output_path)
    except Exception as e:
        print(f"❌ Failed to export workflow: {e}")
        return False


def export_agent_to_json(agent_config, output_dir: Path) -> bool:
    """Export agent configuration to JSON"""
    try:
        json_config = agent_config.to_json_dict()
        output_path = output_dir / "agent.json"
        return export_to_json(json_config, output_path)
    except Exception as e:
        print(f"❌ Failed to export agent: {e}")
        return False


def export_tool_to_json(tool_config, output_dir: Path) -> bool:
    """Export tool configuration to JSON"""
    try:
        json_config = tool_config.to_json_dict()
        # Add metadata section for JSON compatibility
        if "metadata" not in json_config:
            json_config["metadata"] = {
                "category": getattr(tool_config, 'category', 'general'),
                "tags": getattr(tool_config, 'tags', []),
                "usage_examples": getattr(tool_config, 'usage_examples', []),
                "related_tools": getattr(tool_config, 'related_tools', [])
            }
        
        output_path = output_dir / "tool.json"
        return export_to_json(json_config, output_path)
    except Exception as e:
        print(f"❌ Failed to export tool: {e}")
        return False


def export_all_to_json(output_base_dir: Path = None) -> Dict[str, bool]:
    """Export all components to JSON format"""
    if output_base_dir is None:
        output_base_dir = Path(__file__).parent.parent / "exported_json"
    
    results = {}
    
    try:
        # Import components
        from workflow_best_ux.workflows.simple_chat_workflow.workflow import simple_chat_workflow
        from workflow_best_ux.agents.chat_assistant.agent import chat_assistant_agent
        from workflow_best_ux.tools.web_search.tool import web_search_tool
        from workflow_best_ux.tools.get_user_info.tool import get_user_info_tool
        
        # Export workflow
        workflow_config = simple_chat_workflow()
        workflow_dir = output_base_dir / "workflows" / "simple_chat_workflow"
        results["workflow"] = export_workflow_to_json(workflow_config, workflow_dir)
        
        # Export agent
        agent_config = chat_assistant_agent()
        agent_dir = output_base_dir / "agents" / "chat_assistant"
        results["agent"] = export_agent_to_json(agent_config, agent_dir)
        
        # Export tools
        tools_results = {}
        
        # Web search tool
        web_search_dir = output_base_dir / "tools" / "web_search"
        tools_results["web_search"] = export_tool_to_json(web_search_tool, web_search_dir)
        
        # User info tool
        user_info_dir = output_base_dir / "tools" / "get_user_info"
        tools_results["get_user_info"] = export_tool_to_json(get_user_info_tool, user_info_dir)
        
        results["tools"] = all(tools_results.values())
        
        # Export prompts and messages (copy JSON files)
        base_path = Path(__file__).parent.parent
        
        # Copy prompt files
        prompt_src = base_path / "prompts" / "assistant_prompt"
        prompt_dst = output_base_dir / "prompts" / "assistant_prompt"
        results["prompts"] = copy_component_files(prompt_src, prompt_dst)
        
        # Copy message files
        message_src = base_path / "messages" / "welcome_message"
        message_dst = output_base_dir / "messages" / "welcome_message"
        results["messages"] = copy_component_files(message_src, message_dst)
        
    except Exception as e:
        print(f"❌ Failed to export components: {e}")
        results["error"] = str(e)
    
    return results


def copy_component_files(src_dir: Path, dst_dir: Path) -> bool:
    """Copy component files (JSON and Markdown) to destination"""
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy JSON file
        json_files = list(src_dir.glob("*.json"))
        for json_file in json_files:
            dst_json = dst_dir / json_file.name
            dst_json.write_text(json_file.read_text())
        
        # Copy Markdown files
        md_files = list(src_dir.glob("*.md"))
        for md_file in md_files:
            dst_md = dst_dir / md_file.name
            dst_md.write_text(md_file.read_text())
        
        return True
    except Exception as e:
        print(f"❌ Failed to copy files from {src_dir} to {dst_dir}: {e}")
        return False


def show_export_report(results: Dict[str, bool]):
    """Show export results report"""
    print("📦 Export Report")
    print("=" * 20)
    
    total_components = 0
    successful_exports = 0
    
    for component, success in results.items():
        if component == "error":
            continue
            
        status = "✅" if success else "❌"
        print(f"  {status} {component}")
        total_components += 1
        if success:
            successful_exports += 1
    
    if "error" in results:
        print(f"\n❌ Export error: {results['error']}")
    
    print(f"\n📊 Summary: {successful_exports}/{total_components} components exported successfully")
    
    if successful_exports == total_components:
        print("🎉 All components exported successfully!")
    else:
        print("⚠️ Some components failed to export")


def create_deployment_package(output_dir: Path = None) -> bool:
    """Create a complete deployment package with all JSON files"""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "deployment_package"
    
    print("📦 Creating Deployment Package")
    print("=" * 35)
    
    # Export all components
    results = export_all_to_json(output_dir)
    
    # Show results
    show_export_report(results)
    
    # Create deployment info
    deployment_info = {
        "package_type": "workflow_best_ux_deployment",
        "created_at": "2024-01-15T10:00:00Z",
        "components": {
            "workflows": ["simple_chat_workflow"],
            "agents": ["chat_assistant"],
            "tools": ["web_search", "get_user_info"],
            "prompts": ["assistant_prompt"],
            "messages": ["welcome_message"]
        },
        "format": "hybrid_json_python",
        "navigation_support": True,
        "type_safety": True
    }
    
    info_path = output_dir / "deployment_info.json"
    export_to_json(deployment_info, info_path)
    
    print(f"\n📁 Deployment package created at: {output_dir}")
    print("🚀 Ready for deployment!")
    
    return all(results.values())


if __name__ == "__main__":
    # Create deployment package
    success = create_deployment_package()
    
    if success:
        print("\n✅ Deployment package created successfully!")
    else:
        print("\n❌ Some components failed to export")
