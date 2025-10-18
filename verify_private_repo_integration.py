#!/usr/bin/env python3
"""
Verification Script for Private Repository Integration

This script verifies that all components of the private repository integration
are properly configured and in place.
"""

import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {file_path}")
        return False

def check_file_contains(file_path, search_strings, description):
    """Check if a file contains specific strings."""
    path = Path(file_path)
    if not path.exists():
        print(f"✗ {description}: File not found - {file_path}")
        return False
    
    content = path.read_text()
    missing = []
    for search_str in search_strings:
        if search_str not in content:
            missing.append(search_str)
    
    if missing:
        print(f"✗ {description}: Missing content in {file_path}")
        for item in missing:
            print(f"    Missing: {item}")
        return False
    else:
        print(f"✓ {description}: {file_path}")
        return True

def verify_prompt_config():
    """Verify prompt configuration."""
    print("\n" + "=" * 80)
    print("VERIFYING PROMPT CONFIGURATION")
    print("=" * 80)
    
    results = []
    
    # Check source file
    results.append(check_file_exists(
        "workflow_configs/agents/prompts/submit_answer_dca5/message_0.md",
        "Prompt source file exists"
    ))
    
    # Check generated file
    results.append(check_file_exists(
        "workflow_config_code/workflows/agents/prompts/submit_answer_dca5/config.py",
        "Prompt config file exists"
    ))
    
    # Check content
    results.append(check_file_contains(
        "workflow_configs/agents/prompts/submit_answer_dca5/message_0.md",
        [
            "Repository type",
            "public or private",
            "Private Repository Setup Instructions",
            "https://github.com/apps/cyoda-ai-assistant",
            "Installation ID",
            "repository_url"
        ],
        "Prompt contains private repo instructions"
    ))
    
    return all(results)

def verify_tool_config():
    """Verify tool configuration."""
    print("\n" + "=" * 80)
    print("VERIFYING TOOL CONFIGURATION")
    print("=" * 80)
    
    results = []
    
    # Check source file
    results.append(check_file_exists(
        "workflow_configs/agents/tools/build_general_application_f281/tool.json",
        "Tool source file exists"
    ))
    
    # Check generated file
    results.append(check_file_exists(
        "workflow_config_code/workflows/agents/tools/build_general_application_f281/config.py",
        "Tool config file exists"
    ))
    
    # Check JSON structure
    try:
        with open("workflow_configs/agents/tools/build_general_application_f281/tool.json", 'r') as f:
            tool_config = json.load(f)
        
        properties = tool_config['function']['parameters']['properties']
        required = tool_config['function']['parameters']['required']
        
        # Check installation_id parameter
        if 'installation_id' in properties:
            print("✓ Tool has installation_id parameter")
            results.append(True)
        else:
            print("✗ Tool missing installation_id parameter")
            results.append(False)
        
        # Check repository_url parameter
        if 'repository_url' in properties:
            print("✓ Tool has repository_url parameter")
            results.append(True)
        else:
            print("✗ Tool missing repository_url parameter")
            results.append(False)
        
        # Check they are optional
        if 'installation_id' not in required and 'repository_url' not in required:
            print("✓ installation_id and repository_url are optional")
            results.append(True)
        else:
            print("✗ installation_id and repository_url should be optional")
            results.append(False)
        
        # Check required parameters
        if all(p in required for p in ['user_request', 'programming_language', 'mode']):
            print("✓ Required parameters present: user_request, programming_language, mode")
            results.append(True)
        else:
            print("✗ Missing required parameters")
            results.append(False)
            
    except Exception as e:
        print(f"✗ Error reading tool.json: {e}")
        results.append(False)
    
    return all(results)

def verify_logging():
    """Verify logging in application_builder_service.py."""
    print("\n" + "=" * 80)
    print("VERIFYING LOGGING")
    print("=" * 80)
    
    results = []
    
    results.append(check_file_exists(
        "functions/application_builder_service.py",
        "ApplicationBuilderService file exists"
    ))
    
    results.append(check_file_contains(
        "functions/application_builder_service.py",
        [
            "logger.info(\"build_general_application called\")",
            "logger.info(\"Received parameters:\")",
            "for key, value in params.items():",
            "Private repository mode enabled",
            "Public repository mode"
        ],
        "Logging code present in build_general_application"
    ))
    
    return all(results)

def verify_documentation():
    """Verify documentation files."""
    print("\n" + "=" * 80)
    print("VERIFYING DOCUMENTATION")
    print("=" * 80)

    results = []

    results.append(check_file_exists(
        "PRIVATE_REPOSITORY_USER_GUIDE.md",
        "User guide exists"
    ))

    results.append(check_file_exists(
        "PRIVATE_REPO_INTEGRATION_SUMMARY.md",
        "Integration summary exists"
    ))

    return all(results)

def verify_tests():
    """Verify test files."""
    print("\n" + "=" * 80)
    print("VERIFYING TEST FILES")
    print("=" * 80)
    
    results = []
    
    results.append(check_file_exists(
        "tests/test_private_repo_build.py",
        "Private repo build test exists"
    ))
    
    results.append(check_file_exists(
        "tests/test_logging_params.py",
        "Logging params test exists"
    ))
    
    return all(results)

def main():
    """Run all verifications."""
    print("=" * 80)
    print("PRIVATE REPOSITORY INTEGRATION VERIFICATION")
    print("=" * 80)
    print("This script verifies that all components are properly configured.")
    print("")
    
    results = []
    
    # Run all verifications
    results.append(verify_prompt_config())
    results.append(verify_tool_config())
    results.append(verify_logging())
    results.append(verify_documentation())
    results.append(verify_tests())
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nCategories passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL VERIFICATIONS PASSED!")
        print("\nThe private repository integration is properly configured.")
        print("\nNext steps:")
        print("1. Restart the application")
        print("2. Test the complete flow with a user")
        print("3. Monitor logs to verify parameters are received")
        print("4. Test with an actual private repository")
        sys.exit(0)
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        print("\nPlease review the errors above and fix the issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()

