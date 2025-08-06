#!/usr/bin/env python3
"""
Run configuration conversion tests

This script runs all the configuration conversion tests and provides a summary.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all configuration conversion tests"""
    print("🧪 RUNNING CONFIGURATION CONVERSION TESTS")
    print("=" * 50)
    
    test_dir = Path(__file__).parent
    
    # List of test files to run
    test_files = [
        "test_json_to_code_conversion.py",
        "test_code_to_json_conversion.py",
        "test_actual_conversion_system.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            print(f"\n🔄 Running {test_file}...")
            print("-" * 40)
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_path), "-v"],
                    capture_output=True,
                    text=True,
                    cwd=test_dir.parent.parent  # Run from project root
                )
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - PASSED")
                    results[test_file] = "PASSED"
                else:
                    print(f"❌ {test_file} - FAILED")
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    results[test_file] = "FAILED"
                    
            except Exception as e:
                print(f"💥 {test_file} - ERROR: {e}")
                results[test_file] = "ERROR"
        else:
            print(f"⚠️ {test_file} - NOT FOUND")
            results[test_file] = "NOT FOUND"
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for status in results.values() if status == "PASSED")
    failed = sum(1 for status in results.values() if status == "FAILED")
    errors = sum(1 for status in results.values() if status == "ERROR")
    not_found = sum(1 for status in results.values() if status == "NOT FOUND")
    
    for test_file, status in results.items():
        status_icon = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "ERROR": "💥",
            "NOT FOUND": "⚠️"
        }.get(status, "❓")
        
        print(f"{status_icon} {test_file}: {status}")
    
    print(f"\n📈 Results: {passed} passed, {failed} failed, {errors} errors, {not_found} not found")
    
    if failed == 0 and errors == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
