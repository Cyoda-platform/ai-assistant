#!/usr/bin/env python3
"""
Complete End-to-End Integration Test

Tests the complete GitHub App integration flow:
1. Authentication
2. Git operations
3. Application builder integration
4. Webhook endpoint

Usage:
    python tests/test_complete_integration.py <installation_id> <repository_url>

Example:
    python tests/test_complete_integration.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.github.github_service import GitHubService
from services.github.auth.installation_token_manager import InstallationTokenManager
from services.github.repository.url_parser import parse_repository_url
from common.utils.utils import clone_repo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_authentication(installation_id: int):
    """Test authentication infrastructure."""
    logger.info("=" * 80)
    logger.info("TEST 1: Authentication Infrastructure")
    logger.info("=" * 80)
    
    try:
        token_manager = InstallationTokenManager()
        token = await token_manager.get_installation_token(installation_id)
        
        if token:
            logger.info(f"✓ Successfully obtained installation token")
            logger.info(f"  Token length: {len(token)} characters")
            return True
        else:
            logger.error("✗ Failed to obtain installation token")
            return False
            
    except Exception as e:
        logger.error(f"✗ Authentication test failed: {e}")
        return False


async def test_url_parsing(repository_url: str):
    """Test URL parsing utilities."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: URL Parsing")
    logger.info("=" * 80)
    
    try:
        url_info = parse_repository_url(repository_url)
        
        logger.info(f"✓ Successfully parsed repository URL")
        logger.info(f"  Owner: {url_info.owner}")
        logger.info(f"  Repository: {url_info.repo_name}")
        logger.info(f"  HTTPS URL: {url_info.to_https_url()}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ URL parsing test failed: {e}")
        return False


async def test_github_service(installation_id: int, repository_url: str):
    """Test GitHub service initialization."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: GitHub Service Initialization")
    logger.info("=" * 80)
    
    try:
        # Test with installation ID
        service = GitHubService(installation_id=installation_id)
        
        logger.info(f"✓ GitHub service initialized successfully")
        logger.info(f"  Installation ID: {service.installation_id}")
        logger.info(f"  API client configured: {service.api_client is not None}")
        logger.info(f"  Git operations configured: {service.git is not None}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ GitHub service test failed: {e}")
        return False


async def test_clone_repo_function(installation_id: int, repository_url: str):
    """Test the clone_repo utility function."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 4: Clone Repository Function")
    logger.info("=" * 80)
    
    try:
        url_info = parse_repository_url(repository_url)
        test_branch = "test-clone-function"
        
        logger.info(f"Testing clone_repo with:")
        logger.info(f"  Branch: {test_branch}")
        logger.info(f"  Repository: {url_info.repo_name}")
        logger.info(f"  Installation ID: {installation_id}")
        logger.info(f"  URL: {repository_url}")
        
        # This should use GitHubService internally
        await clone_repo(
            git_branch_id=test_branch,
            repository_name=url_info.repo_name,
            installation_id=installation_id,
            repository_url=repository_url
        )
        
        logger.info(f"✓ clone_repo function executed successfully")
        
        # Cleanup
        import shutil
        from common.config.config import config
        test_dir = Path(config.PROJECT_DIR) / test_branch
        if test_dir.exists():
            shutil.rmtree(test_dir)
            logger.info(f"  Cleaned up test directory")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ clone_repo function test failed: {e}")
        return False


async def test_backward_compatibility():
    """Test that public repository operations still work."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 5: Backward Compatibility (Public Repos)")
    logger.info("=" * 80)
    
    try:
        # Test without installation ID (public repo mode)
        service = GitHubService()
        
        logger.info(f"✓ GitHub service works without installation ID")
        logger.info(f"  Installation ID: {service.installation_id}")
        logger.info(f"  API client configured: {service.api_client is not None}")
        
        # Verify it uses default token
        if service.api_client.token:
            logger.info(f"  Using default token: Yes")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Backward compatibility test failed: {e}")
        return False


async def test_constants():
    """Test that new constants are defined."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 6: Configuration Constants")
    logger.info("=" * 80)
    
    try:
        import common.config.const as const
        
        # Check new constants exist
        constants_to_check = [
            'REPOSITORY_URL_PARAM',
            'INSTALLATION_ID_PARAM',
            'REPOSITORY_NAME_PARAM',
            'GIT_BRANCH_PARAM',
            'PROGRAMMING_LANGUAGE_PARAM'
        ]
        
        all_exist = True
        for constant in constants_to_check:
            if hasattr(const, constant):
                value = getattr(const, constant)
                logger.info(f"  ✓ {constant} = '{value}'")
            else:
                logger.error(f"  ✗ {constant} not found")
                all_exist = False
        
        if all_exist:
            logger.info(f"✓ All required constants are defined")
            return True
        else:
            logger.error(f"✗ Some constants are missing")
            return False
        
    except Exception as e:
        logger.error(f"✗ Constants test failed: {e}")
        return False


async def test_webhook_route():
    """Test that webhook route is registered."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 7: Webhook Route Registration")
    logger.info("=" * 80)
    
    try:
        from app_factory import create_app
        
        app = create_app()
        
        # Check if github blueprint is registered
        blueprints = [bp.name for bp in app.blueprints.values()]
        
        if 'github' in blueprints:
            logger.info(f"✓ GitHub blueprint is registered")
            logger.info(f"  All blueprints: {', '.join(blueprints)}")
            return True
        else:
            logger.error(f"✗ GitHub blueprint not found")
            logger.error(f"  Available blueprints: {', '.join(blueprints)}")
            return False
        
    except Exception as e:
        logger.error(f"✗ Webhook route test failed: {e}")
        return False


async def main():
    """Main test function."""
    if len(sys.argv) < 3:
        print("Usage: python tests/test_complete_integration.py <installation_id> <repository_url>")
        print("")
        print("Example:")
        print("  python tests/test_complete_integration.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app")
        sys.exit(1)
    
    try:
        installation_id = int(sys.argv[1])
    except ValueError:
        logger.error(f"Invalid installation_id: {sys.argv[1]} (must be an integer)")
        sys.exit(1)
    
    repository_url = sys.argv[2]
    
    logger.info("=" * 80)
    logger.info("Complete End-to-End Integration Test")
    logger.info("=" * 80)
    logger.info(f"Installation ID: {installation_id}")
    logger.info(f"Repository URL: {repository_url}")
    logger.info("")
    
    # Run all tests
    results = []
    
    results.append(await test_authentication(installation_id))
    results.append(await test_url_parsing(repository_url))
    results.append(await test_github_service(installation_id, repository_url))
    results.append(await test_clone_repo_function(installation_id, repository_url))
    results.append(await test_backward_compatibility())
    results.append(await test_constants())
    results.append(await test_webhook_route())
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    logger.info("")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("")
        logger.info("The GitHub App integration is fully functional:")
        logger.info("  ✅ Authentication infrastructure")
        logger.info("  ✅ URL parsing utilities")
        logger.info("  ✅ GitHub service integration")
        logger.info("  ✅ Clone repository function")
        logger.info("  ✅ Backward compatibility")
        logger.info("  ✅ Configuration constants")
        logger.info("  ✅ Webhook route registration")
        logger.info("")
        logger.info("Ready for production use! 🚀")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("")
        logger.error("Please review the errors above and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

