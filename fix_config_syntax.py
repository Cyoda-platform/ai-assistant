#!/usr/bin/env python3
"""
Script to fix syntax errors in workflow config files caused by duplicate removal.
Fixes the double '{ {' issue on the lambda line.
"""

import os
from pathlib import Path


def fix_config_file(config_path: Path) -> bool:
    """Fix syntax error in a config file."""
    print(f"Fixing: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file has the double brace issue
    if 'return lambda params=None: { {' in content:
        # Fix the double brace
        fixed_content = content.replace('return lambda params=None: { {', 'return lambda params=None: {')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"  ✅ Fixed double brace issue")
        return True
    else:
        print(f"  ✓  No issues found")
        return False


def main():
    """Main function to fix all problematic config files."""
    base_path = '/home/kseniia/PycharmProjects/ai_assistant/workflow_config_code/workflows/configs'
    
    print("=" * 80)
    print("Config Syntax Fix Script")
    print("=" * 80)
    
    # List of files that need fixing based on the error message
    files_to_fix = [
        'build_general_application_python/config.py',
        'init_setup_workflow_python/config.py',
        'init_setup_workflow_java/config.py',
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        full_path = Path(base_path) / file_path
        if full_path.exists():
            if fix_config_file(full_path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {full_path}")
    
    print("\n" + "=" * 80)
    print(f"✅ Fixed {fixed_count} file(s)")
    print("=" * 80)


if __name__ == "__main__":
    main()

