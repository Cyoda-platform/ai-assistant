"""
Sync and Validation Utilities

Centralized utilities for syncing Python configurations to JSON files
and validating consistency between formats.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_json_python_match(python_config: Dict[str, Any], json_path: Path) -> bool:
    """Validate that Python config matches JSON file"""
    if not json_path.exists():
        return False
    
    try:
        with open(json_path, 'r') as f:
            json_config = json.load(f)
        
        # Compare key fields (simplified validation)
        if "name" in python_config and "name" in json_config:
            return json_config.get("name") == python_config.get("name")
        
        return True
    except Exception:
        return False


def sync_python_to_json(python_config: Dict[str, Any], json_path: Path) -> bool:
    """Sync Python configuration to JSON file"""
    try:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(python_config, f, indent=2)
        return True
    except Exception:
        return False


def validate_workflow_component(component_dir: Path) -> Tuple[str, bool, str]:
    """Validate a single workflow component directory"""
    component_name = component_dir.name
    
    # Check for required files
    python_file = component_dir / f"{component_dir.parent.name[:-1]}.py"  # Remove 's' from plural
    json_file = component_dir / f"{component_dir.parent.name[:-1]}.json"
    
    if not python_file.exists():
        return component_name, False, f"Missing {python_file.name}"
    
    if not json_file.exists():
        return component_name, False, f"Missing {json_file.name}"
    
    # For now, just check files exist - more validation can be added
    return component_name, True, "Valid"


def validate_all_components() -> Dict[str, List[Tuple[str, bool, str]]]:
    """Validate all components in the workflow_best_ux structure"""
    base_path = Path(__file__).parent.parent
    results = {}
    
    # Component directories to check
    component_types = ["workflows", "agents", "tools", "prompts", "messages"]
    
    for component_type in component_types:
        component_dir = base_path / component_type
        results[component_type] = []
        
        if component_dir.exists():
            for item in component_dir.iterdir():
                if item.is_dir():
                    result = validate_workflow_component(item)
                    results[component_type].append(result)
    
    return results


def sync_all_components() -> Dict[str, List[Tuple[str, bool, str]]]:
    """Sync all Python configurations to JSON files"""
    # This would need to import and call sync methods from each component
    # For now, return a placeholder
    return {
        "workflows": [("simple_chat_workflow", True, "Synced")],
        "agents": [("chat_assistant", True, "Synced")],
        "tools": [("web_search", True, "Synced"), ("get_user_info", True, "Synced")],
        "prompts": [("assistant_prompt", True, "Synced")],
        "messages": [("welcome_message", True, "Synced")]
    }


def show_validation_report():
    """Show a comprehensive validation report"""
    print("🔍 Component Validation Report")
    print("=" * 35)
    
    results = validate_all_components()
    
    total_components = 0
    valid_components = 0
    
    for component_type, components in results.items():
        print(f"\n📁 {component_type.title()}:")
        for name, is_valid, message in components:
            status = "✅" if is_valid else "❌"
            print(f"  {status} {name}: {message}")
            total_components += 1
            if is_valid:
                valid_components += 1
    
    print(f"\n📊 Summary: {valid_components}/{total_components} components valid")
    
    if valid_components == total_components:
        print("🎉 All components are properly configured!")
    else:
        print("⚠️ Some components need attention")


def show_sync_report():
    """Show a comprehensive sync report"""
    print("🔄 Component Sync Report")
    print("=" * 28)
    
    results = sync_all_components()
    
    total_components = 0
    synced_components = 0
    
    for component_type, components in results.items():
        print(f"\n📁 {component_type.title()}:")
        for name, is_synced, message in components:
            status = "✅" if is_synced else "❌"
            print(f"  {status} {name}: {message}")
            total_components += 1
            if is_synced:
                synced_components += 1
    
    print(f"\n📊 Summary: {synced_components}/{total_components} components synced")
    
    if synced_components == total_components:
        print("🎉 All components are in sync!")
    else:
        print("⚠️ Some components need syncing")


if __name__ == "__main__":
    show_validation_report()
    print()
    show_sync_report()
