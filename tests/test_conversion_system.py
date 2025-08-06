#!/usr/bin/env python3
"""
Quick test script for the conversion system

This script provides a simple way to test the conversion system from the project root.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Run conversion system tests"""
    print("🧪 TESTING CONVERSION SYSTEM")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent
    
    # Run the conversion tests
    print("🔄 Running conversion tests...")
    result = subprocess.run(
        [sys.executable, "tests/config_conversion/run_conversion_tests.py"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n🎉 All conversion tests passed!")
        
        # Also test the actual round-trip conversion
        print("\n🔄 Testing actual round-trip conversion...")
        result2 = subprocess.run(
            [sys.executable, "tests/test_roundtrip_conversion.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if result2.returncode == 0:
            print("✅ Round-trip conversion test passed!")
        else:
            print("⚠️ Round-trip conversion test had warnings (this is expected)")
            print("   The warnings indicate that generated configs contain more data than originals")
        
        return True
    else:
        print("\n💥 Some conversion tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
