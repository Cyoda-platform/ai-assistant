"""
Navigation Utilities

Utilities for showing navigation maps and component references
throughout the workflow configuration system.
"""

from pathlib import Path
from typing import Dict, List, Any


def get_component_file_paths() -> Dict[str, Dict[str, str]]:
    """Get file paths for all components"""
    base_path = Path(__file__).parent.parent
    
    return {
        "workflows": {
            "simple_chat_workflow": {
                "python": str(base_path / "workflows/simple_chat_workflow/workflow.py"),
                "json": str(base_path / "workflows/simple_chat_workflow/workflow.json")
            }
        },
        "agents": {
            "chat_assistant": {
                "python": str(base_path / "agents/chat_assistant/agent.py"),
                "json": str(base_path / "agents/chat_assistant/agent.json")
            }
        },
        "tools": {
            "web_search": {
                "python": str(base_path / "tools/web_search/tool.py"),
                "json": str(base_path / "tools/web_search/tool.json")
            },
            "get_user_info": {
                "python": str(base_path / "tools/get_user_info/tool.py"),
                "json": str(base_path / "tools/get_user_info/tool.json")
            }
        },
        "prompts": {
            "assistant_prompt": {
                "python": str(base_path / "prompts/assistant_prompt/prompt.py"),
                "json": str(base_path / "prompts/assistant_prompt/prompt.json"),
                "markdown": str(base_path / "prompts/assistant_prompt/prompt.md")
            }
        },
        "messages": {
            "welcome_message": {
                "python": str(base_path / "messages/welcome_message/message.py"),
                "json": str(base_path / "messages/welcome_message/message.json"),
                "markdown": str(base_path / "messages/welcome_message/message.md")
            }
        }
    }


def get_component_references() -> Dict[str, List[str]]:
    """Get navigation references between components"""
    return {
        "workflow → processors": [
            "simple_chat_workflow → AgentProcessor.chat_assistant",
            "simple_chat_workflow → MessageProcessor.welcome_message",
            "simple_chat_workflow → MessageProcessor.completion_message",
            "simple_chat_workflow → MessageProcessor.error_message",
            "simple_chat_workflow → FunctionProcessor.check_error_condition"
        ],
        "processors → agents": [
            "AgentProcessor.chat_assistant → chat_assistant_agent"
        ],
        "agents → tools": [
            "chat_assistant_agent → web_search_tool",
            "chat_assistant_agent → get_user_info_tool"
        ],
        "agents → prompts": [
            "chat_assistant_agent → assistant_prompt"
        ],
        "processors → messages": [
            "MessageProcessor.welcome_message → welcome_message",
            "MessageProcessor.completion_message → completion_message",
            "MessageProcessor.error_message → error_message"
        ]
    }


def show_navigation_map():
    """Show the complete navigation map"""
    print("🧭 Complete Navigation Map")
    print("=" * 30)
    
    # Show file structure
    print("\n📁 File Structure:")
    file_paths = get_component_file_paths()
    
    for component_type, components in file_paths.items():
        print(f"\n{component_type.title()}:")
        for component_name, files in components.items():
            print(f"  📂 {component_name}/")
            for file_type, file_path in files.items():
                print(f"    📄 {file_type}: {Path(file_path).name}")
    
    # Show navigation references
    print("\n🔗 Navigation References:")
    references = get_component_references()
    
    for ref_type, ref_list in references.items():
        print(f"\n{ref_type}:")
        for ref in ref_list:
            print(f"  • {ref}")
    
    print("\n🎯 Navigation Benefits:")
    print("  ✅ Ctrl+Click on any reference navigates to definition")
    print("  ✅ Find All References shows usage across components")
    print("  ✅ Refactoring support with automatic propagation")
    print("  ✅ IDE auto-completion throughout the chain")


def show_component_details(component_type: str, component_name: str):
    """Show details for a specific component"""
    file_paths = get_component_file_paths()
    
    if component_type not in file_paths:
        print(f"❌ Unknown component type: {component_type}")
        return
    
    if component_name not in file_paths[component_type]:
        print(f"❌ Unknown component: {component_name}")
        return
    
    component = file_paths[component_type][component_name]
    
    print(f"📋 {component_name} Details")
    print("=" * (len(component_name) + 10))
    
    print(f"Type: {component_type}")
    print("Files:")
    for file_type, file_path in component.items():
        exists = "✅" if Path(file_path).exists() else "❌"
        print(f"  {exists} {file_type}: {file_path}")
    
    # Show what references this component
    references = get_component_references()
    referencing = []
    referenced_by = []
    
    for ref_type, ref_list in references.items():
        for ref in ref_list:
            if component_name in ref:
                if ref.startswith(component_name):
                    referencing.append(ref)
                else:
                    referenced_by.append(ref)
    
    if referencing:
        print("\nReferences:")
        for ref in referencing:
            print(f"  → {ref}")
    
    if referenced_by:
        print("\nReferenced by:")
        for ref in referenced_by:
            print(f"  ← {ref}")


def show_navigation_examples():
    """Show practical navigation examples"""
    print("💡 Navigation Examples")
    print("=" * 25)
    
    examples = [
        {
            "scenario": "Workflow Development",
            "steps": [
                "1. Open workflow_best_ux/workflows/simple_chat_workflow/workflow.py",
                "2. Ctrl+Click on 'AgentProcessor.chat_assistant'",
                "3. Navigate to processor definition in processors.py",
                "4. Ctrl+Click on 'chat_assistant_agent.build_agent()'",
                "5. Navigate to agent definition in agents/chat_assistant/agent.py",
                "6. Ctrl+Click on 'web_search_tool.build_tool()'",
                "7. Navigate to tool definition in tools/web_search/tool.py"
            ]
        },
        {
            "scenario": "Content Editing",
            "steps": [
                "1. Open workflow_best_ux/prompts/assistant_prompt/prompt.py",
                "2. See template variables and their defaults",
                "3. Edit workflow_best_ux/prompts/assistant_prompt/prompt.md",
                "4. Use template variables like {platform_name} in content",
                "5. Python automatically handles variable substitution"
            ]
        },
        {
            "scenario": "Tool Development",
            "steps": [
                "1. Open workflow_best_ux/tools/web_search/tool.py",
                "2. See type-safe parameter definitions",
                "3. Modify parameters with full IDE support",
                "4. Auto-generate tool.json with sync utilities",
                "5. All agents using this tool get updated automatically"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['scenario']}:")
        for step in example['steps']:
            print(f"  {step}")


if __name__ == "__main__":
    show_navigation_map()
    print()
    show_navigation_examples()
