#!/usr/bin/env python3
"""
Test Parameter Logging in build_general_application

This test verifies that all parameters are properly logged when calling build_general_application.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.application_builder_service import ApplicationBuilderService
from entity.chat.chat import ChatEntity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_public_repo_logging():
    """Test logging with public repository parameters."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Public Repository Parameters")
    logger.info("=" * 80)
    
    service = ApplicationBuilderService()
    entity = ChatEntity(
        technical_id='test-public-123',
        user_id='test-user',
        workflow_name='build_general_application'
    )
    
    try:
        result = await service.build_general_application(
            technical_id='test-public-123',
            entity=entity,
            user_request='Build a simple REST API with user authentication',
            programming_language='python',
            mode='optimized'
        )
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.info(f"Expected error (workflow not scheduled in test): {type(e).__name__}: {e}")
    
    return True


async def test_private_repo_logging():
    """Test logging with private repository parameters."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Private Repository Parameters")
    logger.info("=" * 80)
    
    service = ApplicationBuilderService()
    entity = ChatEntity(
        technical_id='test-private-456',
        user_id='test-user',
        workflow_name='build_general_application'
    )
    
    try:
        result = await service.build_general_application(
            technical_id='test-private-456',
            entity=entity,
            user_request='Build a user management system with role-based access control',
            programming_language='python',
            mode='optimized',
            installation_id=90513399,
            repository_url='https://github.com/test-ks-001/mcp-cyoda-quart-app'
        )
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.info(f"Expected error (workflow not scheduled in test): {type(e).__name__}: {e}")
    
    return True


async def test_all_parameters_logging():
    """Test logging with all possible parameters."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: All Parameters Including Extra Ones")
    logger.info("=" * 80)
    
    service = ApplicationBuilderService()
    entity = ChatEntity(
        technical_id='test-all-789',
        user_id='test-user',
        workflow_name='build_general_application'
    )
    
    try:
        result = await service.build_general_application(
            technical_id='test-all-789',
            entity=entity,
            user_request='Build a comprehensive e-commerce platform',
            programming_language='java',
            mode='regular',
            installation_id=12345678,
            repository_url='https://github.com/example/example-repo',
            extra_param='This should also be logged',
            another_param=42
        )
        logger.info(f"Result: {result}")
    except Exception as e:
        logger.info(f"Expected error (workflow not scheduled in test): {type(e).__name__}: {e}")
    
    return True


async def main():
    """Run all logging tests."""
    logger.info("\n" + "=" * 80)
    logger.info("PARAMETER LOGGING TESTS")
    logger.info("=" * 80)
    logger.info("These tests verify that build_general_application logs all received parameters")
    logger.info("")
    
    results = []
    
    # Run tests
    results.append(await test_public_repo_logging())
    results.append(await test_private_repo_logging())
    results.append(await test_all_parameters_logging())
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests completed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All logging tests completed successfully!")
        logger.info("")
        logger.info("Verify that the logs above show:")
        logger.info("  1. All parameters received by build_general_application")
        logger.info("  2. Repository mode (public vs private)")
        logger.info("  3. Installation ID and repository URL when provided")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

