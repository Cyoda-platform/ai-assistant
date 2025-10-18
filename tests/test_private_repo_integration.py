#!/usr/bin/env python3
"""
Test Private Repository Integration

Tests the full GitHub App integration with private repositories:
- Clone private repository
- Create branch
- Make changes
- Push changes

Usage:
    python tests/test_private_repo_integration.py <installation_id> <repository_url> <branch_id>

Example:
    python tests/test_private_repo_integration.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app test-integration-branch
"""

import sys
import asyncio
import logging
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.github.github_service import GitHubService
from common.config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_clone(service: GitHubService, branch_id: str, repository_url: str):
    """Test cloning a private repository."""
    logger.info("=" * 80)
    logger.info("TEST 1: Clone Private Repository")
    logger.info("=" * 80)
    
    try:
        result = await service.clone_repository(
            git_branch_id=branch_id,
            repository_name="test-repo",  # Not used when repository_url is provided
            base_branch="main",
            repository_url=repository_url
        )
        
        if result.success:
            logger.info(f"✓ Clone successful: {result.message}")
            return True
        else:
            logger.error(f"✗ Clone failed: {result.message}")
            if result.error:
                logger.error(f"  Error: {result.error}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Clone failed with exception: {e}")
        return False


async def test_create_file(branch_id: str, repository_url: str):
    """Create a test file in the cloned repository."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: Create Test File")
    logger.info("=" * 80)
    
    try:
        from services.github.repository.url_parser import parse_repository_url
        url_info = parse_repository_url(repository_url)
        repo_dir = Path(config.PROJECT_DIR) / branch_id / url_info.repo_name
        
        test_file = repo_dir / "test_github_app_integration.txt"
        test_content = f"""GitHub App Integration Test
Branch: {branch_id}
Repository: {repository_url}
Test timestamp: {asyncio.get_event_loop().time()}

This file was created by the GitHub App integration test.
If you can see this file, the integration is working correctly!
"""
        
        test_file.write_text(test_content)
        logger.info(f"✓ Created test file: {test_file}")
        logger.info(f"  Content: {len(test_content)} bytes")
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to create test file: {e}")
        return False


async def test_push(service: GitHubService, branch_id: str, repository_url: str):
    """Test pushing changes to private repository."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: Push Changes to Private Repository")
    logger.info("=" * 80)
    
    try:
        result = await service.push_changes(
            git_branch_id=branch_id,
            repository_name="test-repo",  # Not used when repository_url is provided
            file_paths=["test_github_app_integration.txt"],
            commit_message="Test GitHub App integration",
            repository_url=repository_url
        )
        
        if result.success:
            logger.info(f"✓ Push successful: {result.message}")
            return True
        else:
            logger.error(f"✗ Push failed: {result.message}")
            if result.error:
                logger.error(f"  Error: {result.error}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Push failed with exception: {e}")
        return False


async def cleanup(branch_id: str, repository_url: str):
    """Clean up test directory."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Cleanup")
    logger.info("=" * 80)
    
    try:
        from services.github.repository.url_parser import parse_repository_url
        url_info = parse_repository_url(repository_url)
        test_dir = Path(config.PROJECT_DIR) / branch_id
        
        if test_dir.exists():
            shutil.rmtree(test_dir)
            logger.info(f"✓ Cleaned up test directory: {test_dir}")
        else:
            logger.info(f"  No cleanup needed (directory doesn't exist)")
            
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")


async def main():
    """Main test function."""
    if len(sys.argv) < 4:
        print("Usage: python tests/test_private_repo_integration.py <installation_id> <repository_url> <branch_id>")
        print("")
        print("Example:")
        print("  python tests/test_private_repo_integration.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app test-integration")
        sys.exit(1)
    
    try:
        installation_id = int(sys.argv[1])
    except ValueError:
        logger.error(f"Invalid installation_id: {sys.argv[1]} (must be an integer)")
        sys.exit(1)
    
    repository_url = sys.argv[2]
    branch_id = sys.argv[3]
    
    logger.info("=" * 80)
    logger.info("GitHub App Private Repository Integration Test")
    logger.info("=" * 80)
    logger.info(f"Installation ID: {installation_id}")
    logger.info(f"Repository URL: {repository_url}")
    logger.info(f"Branch ID: {branch_id}")
    logger.info("")
    
    # Initialize GitHub service with installation ID
    service = GitHubService(installation_id=installation_id)
    logger.info("✓ GitHub service initialized with installation ID")
    logger.info("")
    
    # Run tests
    results = []
    
    # Test 1: Clone
    results.append(await test_clone(service, branch_id, repository_url))
    
    if results[-1]:
        # Test 2: Create file
        results.append(await test_create_file(branch_id, repository_url))
        
        if results[-1]:
            # Test 3: Push
            results.append(await test_push(service, branch_id, repository_url))
    
    # Cleanup
    await cleanup(branch_id, repository_url)
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All tests passed! Private repository integration is working correctly.")
        logger.info("")
        logger.info(f"Check your repository to see the new branch and file:")
        logger.info(f"  {repository_url}/tree/{branch_id}")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

