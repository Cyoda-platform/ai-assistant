#!/usr/bin/env python3
"""
Test GitHub Branch Creation with Installation Token

Tests creating a branch in a private repository using GitHub App authentication.

Usage:
    python tests/test_github_branch_creation.py <installation_id> <repository_url> <branch_name>

Example:
    python tests/test_github_branch_creation.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app test-branch
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.github.auth.installation_token_manager import InstallationTokenManager
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_repository_url(url: str) -> tuple[str, str]:
    """Parse repository owner and name from GitHub URL."""
    url = url.rstrip('.git')
    
    if url.startswith('https://github.com/'):
        parts = url.replace('https://github.com/', '').split('/')
    elif url.startswith('git@github.com:'):
        parts = url.replace('git@github.com:', '').split('/')
    else:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    if len(parts) < 2:
        raise ValueError(f"Could not parse owner and repo from URL: {url}")
    
    return parts[0], parts[1]


async def get_default_branch(owner: str, repo: str, token: str) -> str:
    """Get the default branch of a repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    timeout_config = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout_config, trust_env=False) as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            default_branch = data.get("default_branch", "main")
            logger.info(f"Default branch: {default_branch}")
            return default_branch
        else:
            raise Exception(f"Failed to get repository info: {response.status_code} {response.text}")


async def get_branch_sha(owner: str, repo: str, branch: str, token: str) -> str:
    """Get the SHA of the latest commit on a branch."""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    timeout_config = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout_config, trust_env=False) as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            sha = data["object"]["sha"]
            logger.info(f"Branch {branch} SHA: {sha}")
            return sha
        else:
            raise Exception(f"Failed to get branch SHA: {response.status_code} {response.text}")


async def create_branch(owner: str, repo: str, branch_name: str, sha: str, token: str) -> bool:
    """Create a new branch from a specific SHA."""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
    }
    
    data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": sha
    }
    
    timeout_config = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout_config, trust_env=False) as client:
        response = await client.post(url, json=data, headers=headers)
        
        if response.status_code == 201:
            logger.info(f"✓ Branch '{branch_name}' created successfully!")
            return True
        elif response.status_code == 422:
            logger.warning(f"Branch '{branch_name}' already exists")
            return False
        else:
            raise Exception(f"Failed to create branch: {response.status_code} {response.text}")


async def main():
    """Main test function."""
    if len(sys.argv) < 4:
        print("Usage: python tests/test_github_branch_creation.py <installation_id> <repository_url> <branch_name>")
        print("")
        print("Example:")
        print("  python tests/test_github_branch_creation.py 90513399 https://github.com/test-ks-001/mcp-cyoda-quart-app test-branch")
        sys.exit(1)
    
    try:
        installation_id = int(sys.argv[1])
    except ValueError:
        logger.error(f"Invalid installation_id: {sys.argv[1]} (must be an integer)")
        sys.exit(1)
    
    repository_url = sys.argv[2]
    branch_name = sys.argv[3]
    
    logger.info("=" * 80)
    logger.info("GitHub Branch Creation Test")
    logger.info("=" * 80)
    logger.info(f"Installation ID: {installation_id}")
    logger.info(f"Repository: {repository_url}")
    logger.info(f"Branch Name: {branch_name}")
    logger.info("")
    
    try:
        # Parse repository URL
        owner, repo = parse_repository_url(repository_url)
        logger.info(f"Repository: {owner}/{repo}")
        
        # Get installation token
        logger.info("Getting installation access token...")
        token_manager = InstallationTokenManager()
        token = await token_manager.get_installation_token(installation_id)
        logger.info("✓ Installation token obtained")
        
        # Get default branch
        logger.info("Getting default branch...")
        default_branch = await get_default_branch(owner, repo, token)
        
        # Get SHA of default branch
        logger.info(f"Getting SHA of {default_branch} branch...")
        sha = await get_branch_sha(owner, repo, default_branch, token)
        
        # Create new branch
        logger.info(f"Creating branch '{branch_name}' from {default_branch}...")
        success = await create_branch(owner, repo, branch_name, sha, token)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("Test Summary")
        logger.info("=" * 80)
        
        if success:
            logger.info(f"✓ Successfully created branch '{branch_name}'!")
            logger.info(f"  View at: https://github.com/{owner}/{repo}/tree/{branch_name}")
            sys.exit(0)
        else:
            logger.info(f"Branch '{branch_name}' already exists (not an error)")
            logger.info(f"  View at: https://github.com/{owner}/{repo}/tree/{branch_name}")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

