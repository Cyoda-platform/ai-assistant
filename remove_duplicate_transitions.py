#!/usr/bin/env python3
"""
Script to remove duplicate transitions from workflow config files.
Scans all config.py files in workflow_config_code/workflows/configs and removes duplicate transitions.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple


def find_config_files(base_path: str) -> List[Path]:
    """Find all config.py files in the workflows/configs directory."""
    config_files = []
    base = Path(base_path)
    
    for item in base.iterdir():
        if item.is_dir() and not item.name.startswith('__') and item.name != 'functions':
            config_file = item / 'config.py'
            if config_file.exists():
                config_files.append(config_file)
    
    return sorted(config_files)


def serialize_transition(transition: Dict[str, Any]) -> str:
    """Create a unique string representation of a transition for comparison."""
    return json.dumps(transition, sort_keys=True)


def remove_duplicates_from_transitions(transitions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """Remove duplicate transitions from a list, keeping the first occurrence."""
    seen = set()
    unique_transitions = []
    duplicates_count = 0
    
    for transition in transitions:
        serialized = serialize_transition(transition)
        if serialized not in seen:
            seen.add(serialized)
            unique_transitions.append(transition)
        else:
            duplicates_count += 1
    
    return unique_transitions, duplicates_count


def process_config_file(config_path: Path) -> Dict[str, Any]:
    """Process a single config file and remove duplicate transitions."""
    print(f"\nProcessing: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the file to extract the states dictionary
    # We need to find the "states": { ... } section
    states_match = re.search(r'"states":\s*\{', content)
    if not states_match:
        print(f"  ⚠️  No states found in {config_path}")
        return {"file": str(config_path), "duplicates_removed": 0, "states_processed": 0}
    
    # Load the module to get the actual config
    import importlib.util
    spec = importlib.util.spec_from_file_location("config_module", config_path)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        config_factory = module.get_config()
        config = config_factory({})
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return {"file": str(config_path), "error": str(e), "duplicates_removed": 0, "states_processed": 0}
    
    states = config.get("states", {})
    total_duplicates = 0
    states_with_duplicates = []
    
    for state_name, state_data in states.items():
        if "transitions" in state_data:
            original_count = len(state_data["transitions"])
            unique_transitions, duplicates = remove_duplicates_from_transitions(state_data["transitions"])
            
            if duplicates > 0:
                print(f"  🔍 State '{state_name}': Found {duplicates} duplicate(s) out of {original_count} transitions")
                states_with_duplicates.append(state_name)
                total_duplicates += duplicates
                state_data["transitions"] = unique_transitions
    
    if total_duplicates > 0:
        # Rebuild the config file with deduplicated transitions
        rebuild_config_file(config_path, content, config)
        print(f"  ✅ Removed {total_duplicates} duplicate transition(s) from {len(states_with_duplicates)} state(s)")
    else:
        print(f"  ✓  No duplicates found")
    
    return {
        "file": str(config_path),
        "duplicates_removed": total_duplicates,
        "states_processed": len(states),
        "states_with_duplicates": states_with_duplicates
    }


def rebuild_config_file(config_path: Path, original_content: str, updated_config: Dict[str, Any]):
    """Rebuild the config file with deduplicated transitions."""
    # Read the original file
    lines = original_content.split('\n')
    
    # Find where the lambda starts
    lambda_start = None
    for i, line in enumerate(lines):
        if 'return lambda params=None:' in line:
            lambda_start = i
            break
    
    if lambda_start is None:
        print(f"  ⚠️  Could not find lambda definition in {config_path}")
        return
    
    # Keep everything before the lambda return statement
    header = '\n'.join(lines[:lambda_start + 1])
    
    # Format the updated config
    config_str = format_config_dict(updated_config, indent=2)
    
    # Rebuild the file
    new_content = f"{header} {config_str}\n"
    
    # Write back to file
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def format_config_dict(config: Dict[str, Any], indent: int = 0) -> str:
    """Format config dictionary as Python code."""
    indent_str = ' ' * indent
    lines = ['{']
    
    for key, value in config.items():
        if isinstance(value, dict):
            formatted_value = format_config_dict(value, indent + 8)
            lines.append(f'{indent_str}        "{key}": {formatted_value},')
        elif isinstance(value, list):
            formatted_value = format_list(value, indent + 8)
            lines.append(f'{indent_str}        "{key}": {formatted_value},')
        elif isinstance(value, bool):
            lines.append(f'{indent_str}        "{key}": {str(value)},')
        elif isinstance(value, str):
            # Check if it's a config reference
            if value.endswith('Config.get_name()'):
                lines.append(f'{indent_str}        "{key}": {value},')
            else:
                lines.append(f'{indent_str}        "{key}": "{value}",')
        else:
            lines.append(f'{indent_str}        "{key}": {value},')
    
    lines.append(f'{indent_str}}}')
    return '\n'.join(lines)


def format_list(lst: List[Any], indent: int = 0) -> str:
    """Format list as Python code."""
    if not lst:
        return '[]'
    
    indent_str = ' ' * indent
    lines = ['[']
    
    for item in lst:
        if isinstance(item, dict):
            formatted_item = format_config_dict(item, indent + 8)
            lines.append(f'{indent_str}        {formatted_item},')
        elif isinstance(item, str):
            lines.append(f'{indent_str}        "{item}",')
        else:
            lines.append(f'{indent_str}        {item},')
    
    lines.append(f'{indent_str}]')
    return '\n'.join(lines)


def main():
    """Main function to process all workflow config files."""
    base_path = '/home/kseniia/PycharmProjects/ai_assistant/workflow_config_code/workflows/configs'
    
    print("=" * 80)
    print("Duplicate Transition Removal Script")
    print("=" * 80)
    print(f"Scanning: {base_path}")
    
    config_files = find_config_files(base_path)
    print(f"\nFound {len(config_files)} workflow config files")
    
    results = []
    for config_file in config_files:
        result = process_config_file(config_file)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_duplicates = sum(r.get("duplicates_removed", 0) for r in results)
    files_with_duplicates = [r for r in results if r.get("duplicates_removed", 0) > 0]
    files_with_errors = [r for r in results if "error" in r]
    
    print(f"\nTotal files processed: {len(results)}")
    print(f"Files with duplicates: {len(files_with_duplicates)}")
    print(f"Total duplicates removed: {total_duplicates}")
    print(f"Files with errors: {len(files_with_errors)}")
    
    if files_with_duplicates:
        print("\n📋 Files with duplicates removed:")
        for r in files_with_duplicates:
            workflow_name = Path(r["file"]).parent.name
            print(f"  • {workflow_name}: {r['duplicates_removed']} duplicate(s) in states: {', '.join(r.get('states_with_duplicates', []))}")
    
    if files_with_errors:
        print("\n❌ Files with errors:")
        for r in files_with_errors:
            workflow_name = Path(r["file"]).parent.name
            print(f"  • {workflow_name}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("✅ Processing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

