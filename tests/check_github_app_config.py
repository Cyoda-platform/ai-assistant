#!/usr/bin/env python3
"""
GitHub App Configuration Checker

Verifies that all required environment variables and files are present
before running the authentication tests.

Usage:
    python tests/check_github_app_config.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
    """
    Check if an environment variable is set.
    
    Args:
        name: Environment variable name
        required: Whether the variable is required
        
    Returns:
        Tuple of (is_set, value_or_message)
    """
    value = os.getenv(name)
    
    if value:
        # Mask sensitive values
        if 'SECRET' in name or 'KEY' in name or 'TOKEN' in name:
            masked = value[:10] + '...' if len(value) > 10 else '***'
            return True, masked
        return True, value
    else:
        if required:
            return False, "NOT SET (required)"
        return False, "NOT SET (optional)"


def check_file(path: str) -> tuple[bool, str]:
    """
    Check if a file exists.
    
    Args:
        path: File path to check
        
    Returns:
        Tuple of (exists, message)
    """
    file_path = Path(path)
    
    if file_path.exists():
        size = file_path.stat().st_size
        return True, f"Found ({size} bytes)"
    else:
        return False, "NOT FOUND"


def main():
    """Main configuration check function."""
    print("=" * 80)
    print("GitHub App Configuration Checker")
    print("=" * 80)
    print()
    
    all_ok = True
    
    # Check environment variables
    print("Environment Variables:")
    print("-" * 80)
    
    env_vars = [
        ("GITHUB_APP_ID", True),
        ("GITHUB_APP_OWNER", True),
        ("GITHUB_APP_CLIENT_ID", True),
        ("GITHUB_APP_PRIVATE_KEY_PATH", True),
        ("GITHUB_APP_PUBLIC_LINK", False),
        ("GITHUB_WEBHOOK_URL", False),
        ("GITHUB_WEBHOOK_SECRET", False),
    ]
    
    for var_name, required in env_vars:
        is_set, value = check_env_var(var_name, required)
        status = "✓" if is_set else "✗"
        print(f"  {status} {var_name:35} {value}")
        
        if required and not is_set:
            all_ok = False
    
    print()
    
    # Check private key file
    print("Files:")
    print("-" * 80)
    
    key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH", "private-key.pem")
    exists, message = check_file(key_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {key_path:35} {message}")
    
    if not exists:
        all_ok = False
    
    print()
    
    # Check dependencies
    print("Dependencies:")
    print("-" * 80)
    
    try:
        import jwt
        print(f"  ✓ PyJWT installed (version: {jwt.__version__})")
    except ImportError:
        print(f"  ✗ PyJWT not installed")
        all_ok = False
    
    try:
        import cryptography
        print(f"  ✓ cryptography installed (version: {cryptography.__version__})")
    except ImportError:
        print(f"  ✗ cryptography not installed (required for PyJWT[crypto])")
        all_ok = False
    
    try:
        import httpx
        print(f"  ✓ httpx installed (version: {httpx.__version__})")
    except ImportError:
        print(f"  ✗ httpx not installed")
        all_ok = False
    
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    if all_ok:
        print("✓ All required configuration is present!")
        print()
        print("Next steps:")
        print("  1. Install GitHub App on your test account")
        print("  2. Note the installation ID from the URL")
        print("  3. Run: python tests/github_app_auth_test.py <installation_id>")
        print()
        return 0
    else:
        print("✗ Some required configuration is missing.")
        print()
        print("Please fix the issues above and try again.")
        print()
        print("Setup guide: GITHUB_APP_SETUP.md")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())

