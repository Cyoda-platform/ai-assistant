#!/usr/bin/env python3
"""
Script to identify unused agents, tools, and messages in workflow configurations.

This script scans all workflow config files and identifies which agents, tools, 
and messages are not imported/used in any workflow.
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
                            component_type = module_parts[1]  # agents, tools, messages
                            component_name = module_parts[2]  # the specific component
                            imports.add(f"{component_type}/{component_name}")
            
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('workflow_config_code.'):
                        module_parts = alias.name.split('.')
                        if len(module_parts) >= 3:
                            component_type = module_parts[1]
                            component_name = module_parts[2]
                            imports.add(f"{component_type}/{component_name}")
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return imports


def get_all_workflow_imports(workflows_dir: Path) -> Set[str]:
    """Get all imports from all workflow config files."""
    all_imports = set()
    
    for workflow_dir in workflows_dir.iterdir():
        if workflow_dir.is_dir() and not workflow_dir.name.startswith('__'):
            config_file = workflow_dir / 'config.py'
            if config_file.exists():
                imports = extract_imports_from_file(config_file)
                all_imports.update(imports)
                print(f"Found {len(imports)} imports in {workflow_dir.name}")
    
    return all_imports


def get_all_available_components(base_dir: Path) -> Dict[str, Set[str]]:
    """Get all available components (agents, tools, messages) from the filesystem."""
    components = {
        'agents': set(),
        'tools': set(),
        'messages': set()
    }
    
    for component_type in components.keys():
        component_dir = base_dir / component_type
        if component_dir.exists():
            for item in component_dir.iterdir():
                if item.is_dir() and not item.name.startswith('__'):
                    components[component_type].add(f"{component_type}/{item.name}")
    
    return components


def find_unused_components(workflows_dir: Path, base_dir: Path) -> Dict[str, List[str]]:
    """Find unused components by comparing available vs imported."""
    
    print("Scanning workflow imports...")
    used_imports = get_all_workflow_imports(workflows_dir)
    
    print(f"Total imports found: {len(used_imports)}")
    print("\nSample imports:")
    for imp in sorted(list(used_imports))[:10]:
        print(f"  - {imp}")
    
    print("\nScanning available components...")
    available_components = get_all_available_components(base_dir)
    
    unused = {}
    
    for component_type, available in available_components.items():
        print(f"\nAnalyzing {component_type}:")
        print(f"  Available: {len(available)}")
        
        unused_in_type = []
        for component in available:
            if component not in used_imports:
                unused_in_type.append(component.split('/', 1)[1])  # Remove type prefix
        
        unused[component_type] = sorted(unused_in_type)
        print(f"  Used: {len(available) - len(unused_in_type)}")
        print(f"  Unused: {len(unused_in_type)}")
    
    return unused


def analyze_component_usage_patterns(used_imports: Set[str]) -> Dict[str, List[str]]:
    """Analyze patterns in component usage to identify potential duplicates."""
    patterns = defaultdict(list)

    for import_path in used_imports:
        if '/' in import_path:
            component_type, component_name = import_path.split('/', 1)

            # Look for similar names (potential duplicates)
            base_name = re.sub(r'_[a-f0-9]{4}(_py)?$', '', component_name)
            patterns[f"{component_type}:{base_name}"].append(component_name)

    # Filter to only show patterns with multiple components
    duplicates = {k: v for k, v in patterns.items() if len(v) > 1}
    return duplicates


def generate_detailed_statistics(used_imports: Set[str], available_components: Dict[str, Set[str]]) -> Dict[str, any]:
    """Generate detailed statistics about component usage."""
    stats = {}

    for component_type, available in available_components.items():
        used_count = len([imp for imp in used_imports if imp.startswith(f"{component_type}/")])
        total_count = len(available)
        usage_percentage = (used_count / total_count * 100) if total_count > 0 else 0

        stats[component_type] = {
            'total': total_count,
            'used': used_count,
            'unused': total_count - used_count,
            'usage_percentage': round(usage_percentage, 1)
        }

    return stats


def generate_report(unused_components: Dict[str, List[str]], used_imports: Set[str],
                   available_components: Dict[str, Set[str]], output_file: str = None):
    """Generate a detailed report of unused components."""

    report_lines = []
    report_lines.append("# Unused Workflow Components Report")
    report_lines.append("=" * 50)
    report_lines.append("")

    # Summary statistics
    stats = generate_detailed_statistics(used_imports, available_components)
    total_unused = sum(len(components) for components in unused_components.values())
    total_available = sum(stats[t]['total'] for t in stats)

    report_lines.append("## Summary Statistics")
    report_lines.append("")
    report_lines.append(f"**Total components: {total_available}**")
    report_lines.append(f"**Total unused components: {total_unused}**")
    report_lines.append(f"**Overall usage rate: {round((total_available - total_unused) / total_available * 100, 1)}%**")
    report_lines.append("")

    # Per-type statistics
    report_lines.append("| Component Type | Total | Used | Unused | Usage Rate |")
    report_lines.append("|----------------|-------|------|--------|------------|")
    for component_type, stat in stats.items():
        report_lines.append(f"| {component_type.title()} | {stat['total']} | {stat['used']} | {stat['unused']} | {stat['usage_percentage']}% |")
    report_lines.append("")

    # Potential duplicates analysis
    duplicates = analyze_component_usage_patterns(used_imports)
    if duplicates:
        report_lines.append("## Potential Duplicate Components (Used)")
        report_lines.append("")
        report_lines.append("These components have similar names and might have duplicate functionality:")
        report_lines.append("")
        for pattern, components in sorted(duplicates.items()):
            component_type = pattern.split(':')[0]
            base_name = pattern.split(':')[1]
            report_lines.append(f"### {component_type.title()}: {base_name}")
            for comp in sorted(components):
                report_lines.append(f"- {comp}")
            report_lines.append("")

    # Unused components by type
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
    script_lines.append("# Auto-generated script to remove unused workflow components")
    script_lines.append("# WARNING: Review this script carefully before running!")
    script_lines.append("")
    script_lines.append("set -e  # Exit on any error")
    script_lines.append("")
    script_lines.append("echo 'Starting cleanup of unused workflow components...'")
    script_lines.append("")

    total_to_remove = sum(len(components) for components in unused_components.values())
    script_lines.append(f"echo 'Total components to remove: {total_to_remove}'")
    script_lines.append("")

    for component_type, unused_list in unused_components.items():
        if unused_list:
            script_lines.append(f"echo 'Removing {len(unused_list)} unused {component_type}...'")
            for component in unused_list:
                component_path = base_dir / component_type / component
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
    
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found at {workflows_dir}")
        return
    
    print(f"Analyzing workflow components in: {base_dir}")
    print(f"Workflows directory: {workflows_dir}")
    print("=" * 60)
    
    # Find unused components
    unused_components = find_unused_components(workflows_dir, base_dir)
    
    # Get used imports for additional analysis
    used_imports = get_all_workflow_imports(workflows_dir)
    available_components = get_all_available_components(base_dir)

    # Generate report
    output_file = script_dir / "unused_workflow_components_report.md"
    generate_report(unused_components, used_imports, available_components, str(output_file))

    # Generate cleanup script
    cleanup_script_file = script_dir / "cleanup_unused_components.sh"
    generate_cleanup_script(unused_components, base_dir, str(cleanup_script_file))


if __name__ == "__main__":
    main()
