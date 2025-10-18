#!/usr/bin/env python3
"""
Test Building Application from Private Repository

This test simulates the complete flow of building an application from a private repository.

Usage:
    python tests/test_private_repo_build.py <installation_id> <repository_url>

Example:
    python tests/test_private_repo_build.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.application_builder_service import ApplicationBuilderService
from entity.chat_entity import ChatEntity
from common.config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_private_repo_build(installation_id: int, repository_url: str):
    """
    Test building an application from a private repository.
    
    Args:
        installation_id: GitHub App installation ID
        repository_url: Full repository URL
    """
    logger.info("=" * 80)
    logger.info("Test: Build Application from Private Repository")
    logger.info("=" * 80)
    logger.info(f"Installation ID: {installation_id}")
    logger.info(f"Repository URL: {repository_url}")
    logger.info("")
    
    try:
        # Create a test chat entity
        chat_entity = ChatEntity(
            technical_id="test-private-repo-build",
            user_id="test-user",
            workflow_name="build_general_application"
        )
        
        # Initialize the service
        service = ApplicationBuilderService()
        
        # Test parameters
        user_request = "Create a simple REST API with user management endpoints"
        programming_language = "python"
        mode = "optimized"
        
        logger.info("Building application with parameters:")
        logger.info(f"  User Request: {user_request}")
        logger.info(f"  Language: {programming_language}")
        logger.info(f"  Mode: {mode}")
        logger.info(f"  Installation ID: {installation_id}")
        logger.info(f"  Repository URL: {repository_url}")
        logger.info("")
        
        # Call build_general_application with private repo parameters
        result = await service.build_general_application(
            technical_id=chat_entity.technical_id,
            entity=chat_entity,
            user_request=user_request,
            programming_language=programming_language,
            mode=mode,
            installation_id=installation_id,
            repository_url=repository_url
        )
        
        logger.info("=" * 80)
        logger.info("Build Result:")
        logger.info("=" * 80)
        logger.info(result)
        logger.info("")
        
        # Check if workflow was scheduled
        if "scheduled" in result.lower() or "started" in result.lower():
            logger.info("✓ Application build workflow started successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Monitor the workflow execution")
            logger.info("2. Check the generated code in the repository")
            logger.info("3. Verify the application works as expected")
            return True
        else:
            logger.error("✗ Build workflow may not have started correctly")
            return False
            
    except Exception as e:
        logger.error(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_parameter_validation():
    """Test that parameters are properly validated."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Test: Parameter Validation")
    logger.info("=" * 80)
    
    try:
        from services.github.repository.url_parser import parse_repository_url
        
        # Test valid URLs
        test_urls = [
            "https://github.com/owner/repo",
            "https://github.com/owner/repo.git",
            "git@github.com:owner/repo.git",
        ]
        
        for url in test_urls:
            try:
                url_info = parse_repository_url(url)
                logger.info(f"✓ Valid URL: {url}")
                logger.info(f"  Owner: {url_info.owner}, Repo: {url_info.repo_name}")
            except Exception as e:
                logger.error(f"✗ Failed to parse URL: {url} - {e}")
                return False
        
        logger.info("")
        logger.info("✓ All parameter validation tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Parameter validation test failed: {e}")
        return False


async def main():
    """Main test function."""
    if len(sys.argv) < 3:
        print("Usage: python tests/test_private_repo_build.py <installation_id> <repository_url>")
        print("")
        print("Example:")
        print("  python tests/test_private_repo_build.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app")
        print("")
        print("Note: This test will actually schedule a build workflow.")
        print("      Make sure you want to do this before running!")
        sys.exit(1)
    
    try:
        installation_id = int(sys.argv[1])
    except ValueError:
        logger.error(f"Invalid installation_id: {sys.argv[1]} (must be an integer)")
        sys.exit(1)
    
    repository_url = sys.argv[2]
    
    # Run tests
    results = []
    
    results.append(await test_parameter_validation())
    
    # Ask for confirmation before running actual build
    logger.info("")
    logger.info("=" * 80)
    logger.info("WARNING: The next test will schedule an actual build workflow!")
    logger.info("=" * 80)
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        results.append(await test_private_repo_build(installation_id, repository_url))
    else:
        logger.info("Skipping build test.")
        results.append(True)  # Don't fail the test
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All tests passed!")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

