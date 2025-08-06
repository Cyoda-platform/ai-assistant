#!/usr/bin/env python3
"""
Convenience script to run both conversions and tests

Usage:
  python run_conversions.py                    # Run both conversions
  python run_conversions.py --test             # Run conversions + tests
  python run_conversions.py --json-to-code     # Only JSON to code
  python run_conversions.py --code-to-json     # Only code to JSON
"""

import sys
import subprocess
import argparse


def run_command(command, description):
    """Run a command and report results"""
    print(f"\n🔄 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run workflow configuration conversions")
    parser.add_argument("--test", action="store_true", help="Run tests after conversions")
    parser.add_argument("--json-to-code", action="store_true", help="Only run JSON to code conversion")
    parser.add_argument("--code-to-json", action="store_true", help="Only run code to JSON conversion")
    
    args = parser.parse_args()
    
    print("🚀 WORKFLOW CONFIGURATION CONVERSIONS")
    print("=" * 50)
    
    success = True
    
    # Run JSON to code conversion
    if not args.code_to_json:
        success &= run_command([sys.executable, "convert_configs_to_code.py"], 
                              "JSON to Python Code Conversion")
    
    # Run code to JSON conversion
    if not args.json_to_code:
        success &= run_command([sys.executable, "convert_code_to_configs.py"], 
                              "Python Code to JSON Conversion")
    
    # Run tests if requested
    if args.test and success:
        # Run tests but don't fail on warnings (exit code 1 with warnings is OK)
        try:
            result = subprocess.run([sys.executable, "test_roundtrip_conversion.py"],
                                  capture_output=True, text=True)
            print("\n🔄 Round-trip Conversion Tests...")
            print("-" * 50)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # Check if tests actually passed (look for success message in output)
            if "All tests passed!" in result.stdout:
                print("✅ Round-trip Conversion Tests completed successfully!")
            else:
                print("❌ Round-trip Conversion Tests failed!")
                success = False
        except Exception as e:
            print(f"❌ Round-trip Conversion Tests failed with error: {e}")
            success = False
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 All operations completed successfully!")
        if args.test:
            print("✅ Round-trip conversion verified!")
    else:
        print("💥 Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
