#!/usr/bin/env python3
"""
Test GitHub Webhook Endpoint

Tests the GitHub webhook endpoint with various event types.

Usage:
    python tests/test_github_webhook.py
"""

import sys
import asyncio
import logging
import hmac
import hashlib
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from common.config.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_signature(payload: dict, secret: str) -> str:
    """
    Create GitHub webhook signature.
    
    Args:
        payload: Webhook payload
        secret: Webhook secret
        
    Returns:
        Signature header value
    """
    payload_bytes = json.dumps(payload).encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"


async def test_webhook_endpoint():
    """Test that webhook endpoint is accessible."""
    logger.info("=" * 80)
    logger.info("TEST 1: Webhook Endpoint Accessibility")
    logger.info("=" * 80)
    
    try:
        url = "http://localhost:5000/api/v1/github/webhook/test"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Webhook endpoint is accessible")
                logger.info(f"  Status: {data.get('status')}")
                logger.info(f"  Webhook URL: {data.get('webhook_url')}")
                logger.info(f"  Secret configured: {data.get('webhook_secret_configured')}")
                logger.info(f"  App ID: {data.get('app_id')}")
                return True
            else:
                logger.error(f"✗ Webhook endpoint returned {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Failed to access webhook endpoint: {e}")
        return False


async def test_ping_event():
    """Test ping event handling."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 2: Ping Event")
    logger.info("=" * 80)
    
    try:
        url = "http://localhost:5000/api/v1/github/webhook"
        
        payload = {
            "zen": "Design for failure.",
            "hook_id": 123456789,
            "hook": {
                "type": "App",
                "id": 123456789,
                "active": True
            }
        }
        
        signature = create_signature(payload, config.GITHUB_WEBHOOK_SECRET)
        
        headers = {
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": signature,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Ping event processed successfully")
                logger.info(f"  Response: {data}")
                return True
            else:
                logger.error(f"✗ Ping event failed with status {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Ping event test failed: {e}")
        return False


async def test_installation_event():
    """Test installation event handling."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 3: Installation Event")
    logger.info("=" * 80)
    
    try:
        url = "http://localhost:5000/api/v1/github/webhook"
        
        payload = {
            "action": "created",
            "installation": {
                "id": 90513399,
                "account": {
                    "login": "test-ks-001",
                    "type": "User"
                },
                "repository_selection": "selected",
                "permissions": {
                    "contents": "write",
                    "metadata": "read"
                }
            },
            "repositories": [
                {
                    "id": 123456,
                    "name": "mcp-cyoda-quart-app",
                    "full_name": "test-ks-001/mcp-cyoda-quart-app",
                    "private": True
                }
            ]
        }
        
        signature = create_signature(payload, config.GITHUB_WEBHOOK_SECRET)
        
        headers = {
            "X-GitHub-Event": "installation",
            "X-Hub-Signature-256": signature,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ Installation event processed successfully")
                logger.info(f"  Response: {data}")
                return True
            else:
                logger.error(f"✗ Installation event failed with status {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Installation event test failed: {e}")
        return False


async def test_invalid_signature():
    """Test that invalid signatures are rejected."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST 4: Invalid Signature Rejection")
    logger.info("=" * 80)
    
    try:
        url = "http://localhost:5000/api/v1/github/webhook"
        
        payload = {
            "action": "ping"
        }
        
        # Use wrong signature
        headers = {
            "X-GitHub-Event": "ping",
            "X-Hub-Signature-256": "sha256=invalid_signature",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 401:
                logger.info(f"✓ Invalid signature correctly rejected")
                return True
            else:
                logger.error(f"✗ Invalid signature not rejected (status: {response.status_code})")
                return False
                
    except Exception as e:
        logger.error(f"✗ Invalid signature test failed: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("=" * 80)
    logger.info("GitHub Webhook Endpoint Tests")
    logger.info("=" * 80)
    logger.info("")
    logger.info("NOTE: Make sure the application is running on http://localhost:5000")
    logger.info("")
    
    # Run tests
    results = []
    
    results.append(await test_webhook_endpoint())
    results.append(await test_ping_event())
    results.append(await test_installation_event())
    results.append(await test_invalid_signature())
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All webhook tests passed!")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

