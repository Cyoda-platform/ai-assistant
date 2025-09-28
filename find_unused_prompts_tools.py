#!/usr/bin/env python3
"""
Script to identify unused prompts and tools in workflow configurations.

This script scans all workflow config files AND agent files to identify which 
prompts and tools are not imported/used anywhere.
"""

import os
import re
import ast
from pathlib import Path
from typing import Set, Dict, List, Tuple
from collections import defaultdict


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to extract imports
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith('workflow_config_code.'):
                    for alias in node.names:
                        # Extract the component path from the import
                        module_parts = node.module.split('.')
                        if len(module_parts) >= 3:  # workflow_config_code.{type}.{name}
                            component_type = module_parts[1]  # prompts, tools
                            component_name = module_parts[2]  # the specific component
                            if component_type in ['prompts', 'tools']:
                                imports.add(f"{component_type}/{component_name}")
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('workflow_config_code.'):
                        module_parts = alias.name.split('.')
                        if len(module_parts) >= 3:
                            component_type = module_parts[1]
                            component_name = module_parts[2]
                            if component_type in ['prompts', 'tools']:
                                imports.add(f"{component_type}/{component_name}")
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return imports


def get_all_workflow_imports(workflows_dir: Path) -> Set[str]:
    """Get all prompts/tools imports from all workflow config files."""
    all_imports = set()
    
    for workflow_dir in workflows_dir.iterdir():
        if workflow_dir.is_dir() and not workflow_dir.name.startswith('__'):
            config_file = workflow_dir / 'config.py'
            if config_file.exists():
                imports = extract_imports_from_file(config_file)
                all_imports.update(imports)
                if imports:
                    print(f"Found {len(imports)} prompts/tools imports in workflow {workflow_dir.name}")
    
    return all_imports


def get_all_agent_imports(agents_dir: Path) -> Set[str]:
    """Get all prompts/tools imports from all agent files."""
    all_imports = set()

    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir() and not agent_dir.name.startswith('__'):
            # Check both agent.py and config.py files
            for file_name in ['agent.py', 'config.py']:
                agent_file = agent_dir / file_name
                if agent_file.exists():
                    imports = extract_imports_from_file(agent_file)
                    all_imports.update(imports)
                    if imports:
                        print(f"Found {len(imports)} prompts/tools imports in agent {agent_dir.name}/{file_name}")

    return all_imports


def get_all_available_components(base_dir: Path) -> Dict[str, Set[str]]:
    """Get all available components (prompts, tools) from the filesystem."""
    components = {
        'prompts': set(),
        'tools': set()
    }
    
    for component_type in components.keys():
        component_dir = base_dir / component_type
        if component_dir.exists():
            for item in component_dir.iterdir():
                if item.is_dir() and not item.name.startswith('__'):
                    components[component_type].add(f"{component_type}/{item.name}")
    
    return components


def find_unused_components(workflows_dir: Path, agents_dir: Path, base_dir: Path) -> Dict[str, List[str]]:
    """Find unused components by comparing available vs imported."""
    
    print("Scanning workflow imports...")
    workflow_imports = get_all_workflow_imports(workflows_dir)
    print(f"Total workflow imports found: {len(workflow_imports)}")
    
    print("\nScanning agent imports...")
    agent_imports = get_all_agent_imports(agents_dir)
    print(f"Total agent imports found: {len(agent_imports)}")
    
    # Combine all imports
    all_used_imports = workflow_imports.union(agent_imports)
    print(f"Total unique imports found: {len(all_used_imports)}")
    
    print("\nSample imports:")
    for imp in sorted(list(all_used_imports))[:10]:
        print(f"  - {imp}")
    
    print("\nScanning available components...")
    available_components = get_all_available_components(base_dir)
    
    unused = {}
    
    for component_type, available in available_components.items():
        print(f"\nAnalyzing {component_type}:")
        print(f"  Available: {len(available)}")
        
        unused_in_type = []
        for component in available:
            if component not in all_used_imports:
                unused_in_type.append(component.split('/', 1)[1])  # Remove type prefix
        
        unused[component_type] = sorted(unused_in_type)
        print(f"  Used: {len(available) - len(unused_in_type)}")
        print(f"  Unused: {len(unused_in_type)}")
    
    return unused


def generate_report(unused_components: Dict[str, List[str]], output_file: str = None):
    """Generate a detailed report of unused components."""
    
    report_lines = []
    report_lines.append("# Unused Prompts and Tools Report")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    total_unused = sum(len(components) for components in unused_components.values())
    report_lines.append(f"**Total unused components: {total_unused}**")
    report_lines.append("")
    
    for component_type, unused_list in unused_components.items():
        if unused_list:
            report_lines.append(f"## Unused {component_type.title()} ({len(unused_list)})")
            report_lines.append("")
            for component in unused_list:
                report_lines.append(f"- {component}")
            report_lines.append("")
        else:
            report_lines.append(f"## {component_type.title()}")
            report_lines.append("✅ All components are used!")
            report_lines.append("")
    
    report_content = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\nReport saved to: {output_file}")
    
    print("\n" + report_content)
    
    return report_content


def generate_cleanup_script(unused_components: Dict[str, List[str]], base_dir: Path, output_file: str = None):
    """Generate a shell script to remove unused components."""
    
    script_lines = []
    script_lines.append("#!/bin/bash")
    script_lines.append("# Auto-generated script to remove unused prompts and tools")
    script_lines.append("# WARNING: Review this script carefully before running!")
    script_lines.append("")
    script_lines.append("set -e  # Exit on any error")
    script_lines.append("")
    script_lines.append("echo 'Starting cleanup of unused prompts and tools...'")
    script_lines.append("")
    
    total_to_remove = sum(len(components) for components in unused_components.values())
    script_lines.append(f"echo 'Total components to remove: {total_to_remove}'")
    script_lines.append("")
    
    for component_type, unused_list in unused_components.items():
        if unused_list:
            script_lines.append(f"echo 'Removing {len(unused_list)} unused {component_type}...'")
            for component in unused_list:
                component_path = f"workflow_config_code/{component_type}/{component}"
                script_lines.append(f"rm -rf '{component_path}'")
            script_lines.append("")
    
    script_lines.append("echo 'Cleanup completed!'")
    script_lines.append("echo 'Remember to test your workflows after cleanup.'")
    
    script_content = "\n".join(script_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        # Make the script executable
        os.chmod(output_file, 0o755)
        print(f"Cleanup script saved to: {output_file}")
    
    return script_content


def main():
    """Main function to run the unused component analysis."""
    
    # Set up paths
    script_dir = Path(__file__).parent
    base_dir = script_dir / "workflow_config_code"
    workflows_dir = base_dir / "workflows"
    agents_dir = base_dir / "agents"
    
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found at {workflows_dir}")
        return
        
    if not agents_dir.exists():
        print(f"Error: Agents directory not found at {agents_dir}")
        return
    
    print(f"Analyzing prompts and tools in: {base_dir}")
    print(f"Workflows directory: {workflows_dir}")
    print(f"Agents directory: {agents_dir}")
    print("=" * 60)
    
    # Find unused components
    unused_components = find_unused_components(workflows_dir, agents_dir, base_dir)
    
    # Generate report
    output_file = script_dir / "unused_prompts_tools_report.md"
    generate_report(unused_components, str(output_file))
    
    # Generate cleanup script
    cleanup_script_file = script_dir / "cleanup_unused_prompts_tools.sh"
    generate_cleanup_script(unused_components, base_dir, str(cleanup_script_file))


if __name__ == "__main__":
    main()
