#!/usr/bin/env python3
"""
Script to properly remove duplicate transitions from workflow config files.
This version modifies the config in memory and writes it back correctly.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple


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


def process_workflow(workflow_path: Path) -> Dict[str, Any]:
    """Process a single workflow and remove duplicates."""
    workflow_name = workflow_path.name
    print(f"\nProcessing: {workflow_name}")
    
    # Import the workflow module
    config_file = workflow_path / "config.py"
    if not config_file.exists():
        print(f"  ⚠️  No config.py found")
        return {"file": str(workflow_path), "duplicates_removed": 0}
    
    # Load the module
    spec = importlib.util.spec_from_file_location("config_module", config_file)
    module = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(module)
        config_factory = module.get_config()
        config = config_factory({})
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return {"file": str(workflow_path), "error": str(e), "duplicates_removed": 0}
    
    states = config.get("states", {})
    total_duplicates = 0
    states_with_duplicates = []
    
    # Remove duplicates from each state
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
        # Save the cleaned config back to the file
        save_config_to_file(config_file, config)
        print(f"  ✅ Removed {total_duplicates} duplicate transition(s) from {len(states_with_duplicates)} state(s)")
    else:
        print(f"  ✓  No duplicates found")
    
    return {
        "file": str(workflow_path),
        "duplicates_removed": total_duplicates,
        "states_processed": len(states),
        "states_with_duplicates": states_with_duplicates
    }


def save_config_to_file(config_file: Path, config: Dict[str, Any]):
    """Save the cleaned config back to the Python file."""
    # Read the original file to preserve imports and structure
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the line where the lambda starts
    lambda_line_idx = None
    for i, line in enumerate(lines):
        if 'return lambda params=None:' in line:
            lambda_line_idx = i
            break

    if lambda_line_idx is None:
        print(f"  ⚠️  Could not find lambda definition")
        return

    # Keep everything before the lambda line (not including it)
    header_lines = lines[:lambda_line_idx]

    # Format the config as Python dict
    config_str = format_dict_as_python(config, indent_level=1)

    # Write the file
    with open(config_file, 'w', encoding='utf-8') as f:
        # Write header
        for line in header_lines:
            f.write(line)

        # Write the lambda line with the config
        f.write(f'    return lambda params=None: {config_str}\n')


def format_dict_as_python(obj: Any, indent_level: int = 0) -> str:
    """Format a Python object as properly indented Python code."""
    indent = '    ' * indent_level
    next_indent = '    ' * (indent_level + 1)
    
    if isinstance(obj, dict):
        if not obj:
            return '{}'
        
        lines = ['{']
        items = list(obj.items())
        for i, (key, value) in enumerate(items):
            formatted_value = format_dict_as_python(value, indent_level + 1)
            
            # Handle multi-line values
            if '\n' in formatted_value:
                lines.append(f'{next_indent}"{key}": {formatted_value},')
            else:
                lines.append(f'{next_indent}"{key}": {formatted_value},')
        
        lines.append(f'{indent}}}')
        return '\n'.join(lines)
    
    elif isinstance(obj, list):
        if not obj:
            return '[]'
        
        lines = ['[']
        for item in obj:
            formatted_item = format_dict_as_python(item, indent_level + 1)
            if '\n' in formatted_item:
                lines.append(f'{next_indent}{formatted_item},')
            else:
                lines.append(f'{next_indent}{formatted_item},')
        
        lines.append(f'{indent}]')
        return '\n'.join(lines)
    
    elif isinstance(obj, str):
        # Check if it's a config reference (ends with .get_name())
        if 'Config.get_name()' in obj:
            return obj
        else:
            return f'"{obj}"'
    
    elif isinstance(obj, bool):
        return str(obj)
    
    elif obj is None:
        return 'None'
    
    else:
        return str(obj)


def main():
    """Main function to process all workflow config files."""
    base_path = Path('/home/kseniia/PycharmProjects/ai_assistant/workflow_config_code/workflows/configs')
    
    print("=" * 80)
    print("Duplicate Transition Removal Script (Proper Version)")
    print("=" * 80)
    print(f"Scanning: {base_path}")
    
    # Find all workflow directories
    workflow_dirs = [d for d in base_path.iterdir() 
                     if d.is_dir() and not d.name.startswith('__') and d.name != 'functions']
    
    print(f"\nFound {len(workflow_dirs)} workflow directories")
    
    results = []
    for workflow_dir in sorted(workflow_dirs):
        result = process_workflow(workflow_dir)
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
            workflow_name = Path(r["file"]).name
            print(f"  • {workflow_name}: {r['duplicates_removed']} duplicate(s)")
    
    if files_with_errors:
        print("\n❌ Files with errors:")
        for r in files_with_errors:
            workflow_name = Path(r["file"]).name
            print(f"  • {workflow_name}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("✅ Processing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

