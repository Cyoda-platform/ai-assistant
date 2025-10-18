"""
GitHub webhook endpoint for GitHub App integration.

Handles webhook events from GitHub App installations including:
- Installation events (created, deleted)
- Repository events (added, removed)
- Push events
- Pull request events
"""

import logging
import hmac
import hashlib
from typing import Dict, Any, Optional

from quart import Blueprint, request, jsonify
from common.config.config import config

logger = logging.getLogger(__name__)

github_bp = Blueprint('github', __name__)


def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verify that the webhook request came from GitHub.
    
    Args:
        payload_body: Raw request body
        signature_header: X-Hub-Signature-256 header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not config.GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured - skipping signature verification")
        return True
    
    if not signature_header:
        logger.error("Missing X-Hub-Signature-256 header")
        return False
    
    # GitHub sends signature as "sha256=<signature>"
    if not signature_header.startswith('sha256='):
        logger.error(f"Invalid signature format: {signature_header}")
        return False
    
    expected_signature = signature_header.split('=')[1]
    
    # Calculate HMAC
    secret = config.GITHUB_WEBHOOK_SECRET.encode('utf-8')
    calculated_signature = hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
    
    # Compare signatures
    if not hmac.compare_digest(calculated_signature, expected_signature):
        logger.error("Webhook signature verification failed")
        return False
    
    return True


async def handle_installation_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle GitHub App installation events.
    
    Args:
        event_type: Event type (installation, installation_repositories)
        payload: Event payload
        
    Returns:
        Response dictionary
    """
    action = payload.get('action')
    installation = payload.get('installation', {})
    installation_id = installation.get('id')
    account = installation.get('account', {})
    account_login = account.get('login')
    
    logger.info(f"Installation event: {action} for account {account_login} (installation_id={installation_id})")
    
    if action == 'created':
        logger.info(f"GitHub App installed by {account_login}")
        logger.info(f"Installation ID: {installation_id}")
        logger.info(f"Repositories: {installation.get('repository_selection')}")
        
        # TODO: Store installation information in database
        # This would allow automatic lookup of installation_id by repository
        
    elif action == 'deleted':
        logger.info(f"GitHub App uninstalled by {account_login}")
        
        # TODO: Remove installation information from database
        
    elif action == 'suspend':
        logger.info(f"GitHub App suspended by {account_login}")
        
    elif action == 'unsuspend':
        logger.info(f"GitHub App unsuspended by {account_login}")
    
    return {"status": "processed", "action": action}


async def handle_repository_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle repository events (added/removed from installation).
    
    Args:
        event_type: Event type
        payload: Event payload
        
    Returns:
        Response dictionary
    """
    action = payload.get('action')
    installation = payload.get('installation', {})
    installation_id = installation.get('id')
    
    if action == 'added':
        repositories_added = payload.get('repositories_added', [])
        logger.info(f"Repositories added to installation {installation_id}:")
        for repo in repositories_added:
            logger.info(f"  - {repo.get('full_name')}")
            
        # TODO: Store repository-installation mapping in database
        
    elif action == 'removed':
        repositories_removed = payload.get('repositories_removed', [])
        logger.info(f"Repositories removed from installation {installation_id}:")
        for repo in repositories_removed:
            logger.info(f"  - {repo.get('full_name')}")
            
        # TODO: Remove repository-installation mapping from database
    
    return {"status": "processed", "action": action}


async def handle_push_event(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle push events.
    
    Args:
        payload: Event payload
        
    Returns:
        Response dictionary
    """
    repository = payload.get('repository', {})
    repo_name = repository.get('full_name')
    ref = payload.get('ref')
    pusher = payload.get('pusher', {}).get('name')
    
    logger.info(f"Push event: {pusher} pushed to {ref} in {repo_name}")
    
    # TODO: Implement push event handling if needed
    # For example, trigger builds or notifications
    
    return {"status": "processed", "event": "push"}


async def handle_pull_request_event(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle pull request events.
    
    Args:
        payload: Event payload
        
    Returns:
        Response dictionary
    """
    action = payload.get('action')
    pull_request = payload.get('pull_request', {})
    pr_number = pull_request.get('number')
    repository = payload.get('repository', {})
    repo_name = repository.get('full_name')
    
    logger.info(f"Pull request event: {action} for PR #{pr_number} in {repo_name}")
    
    # TODO: Implement PR event handling if needed
    # For example, run checks or add comments
    
    return {"status": "processed", "event": "pull_request", "action": action}


@github_bp.route('/webhook', methods=['POST'])
async def webhook():
    """
    GitHub webhook endpoint.
    
    Receives and processes webhook events from GitHub App.
    
    Returns:
        JSON response with processing status
    """
    try:
        # Get raw body for signature verification
        payload_body = await request.get_data()
        
        # Verify webhook signature
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_webhook_signature(payload_body, signature):
            logger.error("Webhook signature verification failed")
            return jsonify({"error": "Invalid signature"}), 401
        
        # Get event type
        event_type = request.headers.get('X-GitHub-Event')
        if not event_type:
            logger.error("Missing X-GitHub-Event header")
            return jsonify({"error": "Missing event type"}), 400
        
        # Parse JSON payload
        payload = await request.get_json()
        
        logger.info(f"Received GitHub webhook: {event_type}")
        
        # Route to appropriate handler
        if event_type == 'installation':
            result = await handle_installation_event(event_type, payload)
        elif event_type == 'installation_repositories':
            result = await handle_repository_event(event_type, payload)
        elif event_type == 'push':
            result = await handle_push_event(payload)
        elif event_type == 'pull_request':
            result = await handle_pull_request_event(payload)
        elif event_type == 'ping':
            logger.info("Received ping event from GitHub")
            result = {"status": "pong"}
        else:
            logger.info(f"Unhandled event type: {event_type}")
            result = {"status": "ignored", "event": event_type}
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@github_bp.route('/webhook/test', methods=['GET'])
async def webhook_test():
    """
    Test endpoint to verify webhook configuration.
    
    Returns:
        JSON response with configuration status
    """
    return jsonify({
        "status": "ok",
        "webhook_url": config.GITHUB_WEBHOOK_URL,
        "webhook_secret_configured": bool(config.GITHUB_WEBHOOK_SECRET),
        "app_id": config.GITHUB_APP_ID,
        "message": "GitHub webhook endpoint is ready"
    }), 200

