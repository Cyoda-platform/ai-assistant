#!/usr/bin/env python3
"""
Test runner script for the AI Assistant project.

This script provides various options for running tests:
- Run all tests
- Run tests for specific components (tools, dispatcher)
- Run tests with different verbosity levels
- Generate coverage reports
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    if description:
        print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for AI Assistant project")
    
    parser.add_argument(
        "--component",
        choices=["all", "tools", "dispatcher", "base", "migration", "processors"],
        default="all",
        help="Which component to test (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (use -v, -vv, or -vvv)"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--html-coverage",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    parser.add_argument(
        "--markers", "-m",
        help="Run tests with specific markers (e.g., 'unit', 'integration', 'not slow')"
    )
    
    parser.add_argument(
        "--pattern", "-k",
        help="Run tests matching pattern"
    )
    
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--failfast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "--lf",
        action="store_true",
        help="Run last failed tests only"
    )
    
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Only collect tests, don't run them"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test paths based on component
    if args.component == "all":
        cmd.append("tests/")
    elif args.component == "tools":
        cmd.append("tests/tools/")
    elif args.component == "dispatcher":
        cmd.append("tests/workflow/dispatcher/")
    elif args.component == "base":
        cmd.append("tests/tools/test_base_service.py")
    elif args.component == "migration":
        cmd.append("tests/test_workflow_migration.py")
    elif args.component == "processors":
        cmd.extend(["tests/test_function_processor.py", "tests/test_workflow_orchestration.py"])
    
    # Add verbosity
    if args.verbose > 0:
        cmd.append("-" + "v" * min(args.verbose, 3))
    
    # Add coverage options
    if args.coverage or args.html_coverage:
        cmd.extend([
            "--cov=tools",
            "--cov=workflow/dispatcher",
            "--cov=processors",
            "--cov-report=term-missing"
        ])
        
        if args.html_coverage:
            cmd.extend(["--cov-report=html:htmlcov"])
    
    # Add markers
    if args.markers:
        cmd.extend(["-m", args.markers])
    
    # Add pattern matching
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add fail fast
    if args.failfast:
        cmd.append("-x")
    
    # Add last failed
    if args.lf:
        cmd.append("--lf")
    
    # Add collect only
    if args.collect_only:
        cmd.append("--collect-only")
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings",  # Disable warnings for cleaner output
    ])
    
    # Run the tests
    success = run_command(cmd, f"Running {args.component} tests")
    
    if success:
        print(f"\n✅ All {args.component} tests passed!")
        
        if args.html_coverage:
            print(f"\n📊 HTML coverage report generated in: {project_root}/htmlcov/index.html")
            
    else:
        print(f"\n❌ Some {args.component} tests failed!")
        sys.exit(1)


def run_specific_tests():
    """Run specific test scenarios."""
    print("Available test scenarios:")
    print("1. Quick unit tests (tools only)")
    print("2. Dispatcher tests")
    print("3. All tests with coverage")
    print("4. Integration tests")
    print("5. Failed tests only")
    print("6. Migration tests")
    print("7. Processor tests")
    
    scenarios = {
        "1": {
            "cmd": ["python", "-m", "pytest", "tests/tools/", "-v", "--tb=short"],
            "desc": "Quick unit tests for tools"
        },
        "2": {
            "cmd": ["python", "-m", "pytest", "tests/workflow/dispatcher/", "-v", "--tb=short"],
            "desc": "Dispatcher tests"
        },
        "3": {
            "cmd": [
                "python", "-m", "pytest", "tests/", 
                "--cov=tools", "--cov=workflow/dispatcher",
                "--cov-report=term-missing", "--cov-report=html:htmlcov",
                "-v"
            ],
            "desc": "All tests with coverage report"
        },
        "4": {
            "cmd": ["python", "-m", "pytest", "tests/", "-m", "integration", "-v"],
            "desc": "Integration tests only"
        },
        "5": {
            "cmd": ["python", "-m", "pytest", "--lf", "-v"],
            "desc": "Last failed tests only"
        },
        "6": {
            "cmd": ["python", "-m", "pytest", "tests/test_workflow_migration.py", "-v", "--tb=short"],
            "desc": "Migration tests"
        },
        "7": {
            "cmd": [
                "python", "-m", "pytest",
                "tests/test_function_processor.py",
                "tests/test_workflow_orchestration.py",
                "-v", "--tb=short"
            ],
            "desc": "Processor tests"
        }
    }
    
    choice = input("\nEnter scenario number (1-7): ").strip()
    
    if choice in scenarios:
        scenario = scenarios[choice]
        run_command(scenario["cmd"], scenario["desc"])
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode
        print("AI Assistant Test Runner")
        print("=" * 40)
        print("No arguments provided. Running in interactive mode.")
        print()
        
        run_specific_tests()
    else:
        # Command line mode
        main()
