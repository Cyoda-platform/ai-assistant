#!/usr/bin/env python3
"""
GitHub App Authentication Test Script

Tests GitHub App JWT generation and installation token retrieval.
Run this script to verify your GitHub App credentials are configured correctly.

Usage:
    python tests/github_app_auth_test.py <installation_id> [repository_url]

Example:
    python tests/github_app_auth_test.py 12345678
    python tests/github_app_auth_test.py 12345678 https://github.com/owner/repo
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.github.auth.jwt_generator import GitHubAppJWTGenerator
from services.github.auth.installation_token_manager import InstallationTokenManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_repository_url(url: str) -> tuple[str, str]:
    """
    Parse repository owner and name from GitHub URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Tuple of (owner, repo_name)
    """
    # Remove .git suffix if present
    url = url.rstrip('.git')
    
    # Handle different URL formats
    if url.startswith('https://github.com/'):
        parts = url.replace('https://github.com/', '').split('/')
    elif url.startswith('git@github.com:'):
        parts = url.replace('git@github.com:', '').split('/')
    else:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    if len(parts) < 2:
        raise ValueError(f"Could not parse owner and repo from URL: {url}")
    
    return parts[0], parts[1]


async def test_jwt_generation():
    """Test JWT token generation."""
    logger.info("=" * 80)
    logger.info("TEST 1: JWT Token Generation")
    logger.info("=" * 80)
    
    try:
        jwt_gen = GitHubAppJWTGenerator()
        logger.info(f"✓ JWT Generator initialized")
        logger.info(f"  App ID: {jwt_gen.app_id}")
        logger.info(f"  Private Key Path: {jwt_gen.private_key_path}")
        
        # Generate JWT
        jwt_token = jwt_gen.generate_jwt()
        logger.info(f"✓ JWT token generated successfully")
        logger.info(f"  Token (first 50 chars): {jwt_token[:50]}...")
        logger.info(f"  Token length: {len(jwt_token)} characters")
        
        # Check if expired
        is_expired = jwt_gen.is_token_expired(jwt_token)
        logger.info(f"  Token expired: {is_expired}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ JWT generation failed: {e}")
        return False


async def test_installation_token(installation_id: int):
    """Test installation access token retrieval."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: Installation Access Token")
    logger.info("=" * 80)
    
    try:
        token_manager = InstallationTokenManager()
        logger.info(f"✓ Token Manager initialized")
        
        # Get installation token
        logger.info(f"Requesting installation token for installation ID: {installation_id}")
        token = await token_manager.get_installation_token(installation_id)
        
        logger.info(f"✓ Installation token obtained successfully")
        logger.info(f"  Token (first 50 chars): {token[:50]}...")
        logger.info(f"  Token length: {len(token)} characters")
        
        # Check cached token
        cached_token = token_manager._token_cache.get(installation_id)
        if cached_token:
            logger.info(f"  Cached token info:")
            logger.info(f"    Expires at: {cached_token.expires_at}")
            logger.info(f"    Permissions: {list(cached_token.permissions.keys())}")
            logger.info(f"    Repository selection: {cached_token.repository_selection}")
            logger.info(f"    Is expired: {cached_token.is_expired()}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Installation token request failed: {e}")
        return False


async def test_repository_access(installation_id: int, repository_url: str):
    """Test repository access verification."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: Repository Access Verification")
    logger.info("=" * 80)
    
    try:
        # Parse repository URL
        owner, repo_name = parse_repository_url(repository_url)
        logger.info(f"Repository: {owner}/{repo_name}")
        
        token_manager = InstallationTokenManager()
        
        # Verify access
        has_access = await token_manager.verify_installation_access(
            installation_id,
            owner,
            repo_name
        )
        
        if has_access:
            logger.info(f"✓ Installation {installation_id} has access to {owner}/{repo_name}")
        else:
            logger.warning(f"✗ Installation {installation_id} does NOT have access to {owner}/{repo_name}")
        
        return has_access
        
    except Exception as e:
        logger.error(f"✗ Repository access verification failed: {e}")
        return False


async def main():
    """Main test function."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python tests/github_app_auth_test.py <installation_id> [repository_url]")
        print("")
        print("Example:")
        print("  python tests/github_app_auth_test.py 12345678")
        print("  python tests/github_app_auth_test.py 12345678 https://github.com/owner/repo")
        sys.exit(1)
    
    try:
        installation_id = int(sys.argv[1])
    except ValueError:
        logger.error(f"Invalid installation_id: {sys.argv[1]} (must be an integer)")
        sys.exit(1)
    
    repository_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    logger.info("GitHub App Authentication Test")
    logger.info(f"Installation ID: {installation_id}")
    if repository_url:
        logger.info(f"Repository URL: {repository_url}")
    logger.info("")
    
    # Run tests
    results = []
    
    # Test 1: JWT Generation
    results.append(await test_jwt_generation())
    
    # Test 2: Installation Token
    results.append(await test_installation_token(installation_id))
    
    # Test 3: Repository Access (if URL provided)
    if repository_url:
        results.append(await test_repository_access(installation_id, repository_url))
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All tests passed! GitHub App authentication is working correctly.")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

