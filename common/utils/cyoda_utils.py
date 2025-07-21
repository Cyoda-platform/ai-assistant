#!/usr/bin/env python3
"""
Cyoda utility functions for MCP integration
"""

import jwt
import logging
from typing import Optional
from common.config.config import config

logger = logging.getLogger(__name__)


def extract_caas_org_id_from_token(token: str) -> Optional[str]:
    """
    Extract caas_org_id from JWT token
    
    Args:
        token: JWT token string (without 'Bearer ' prefix)
        
    Returns:
        caas_org_id if found in token, None otherwise
    """
    try:
        # Decode JWT token without verification (we just need to read the payload)
        # Token should already be validated by the auth system
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Extract caas_org_id from token payload
        caas_org_id = decoded.get('caas_org_id')
        
        if caas_org_id:
            logger.debug(f"Extracted caas_org_id: {caas_org_id}")
            return caas_org_id
        else:
            logger.warning("No caas_org_id found in token payload")
            return None
            
    except jwt.DecodeError as e:
        logger.error(f"Failed to decode JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting caas_org_id from token: {e}")
        return None


def build_cyoda_environment_url(token: str) -> Optional[str]:
    """
    Build Cyoda environment URL from user token
    
    Args:
        token: JWT token string (without 'Bearer ' prefix)
        
    Returns:
        Full Cyoda environment URL or None if cannot be constructed
    """
    try:
        # Extract organization ID from token
        caas_org_id = extract_caas_org_id_from_token(token)
        
        if not caas_org_id:
            logger.error("Cannot build Cyoda URL: no caas_org_id in token")
            return None
        
        # Get CLIENT_HOST from config
        client_host = getattr(config, 'CLIENT_HOST', 'kube.cyoda.org')
        
        # Build URL: client-{caas_org_id}.{CLIENT_HOST}
        cyoda_url = f"https://client-{caas_org_id}.{client_host}"
        
        logger.debug(f"Built Cyoda URL: {cyoda_url}")
        return cyoda_url
        
    except Exception as e:
        logger.error(f"Error building Cyoda environment URL: {e}")
        return None


def validate_cyoda_environment_access(token: str, caas_org_id: str) -> bool:
    """
    Validate that the token has access to the specified Cyoda environment
    
    Args:
        token: JWT token string
        caas_org_id: Organization ID to validate access for
        
    Returns:
        True if token has access to the environment, False otherwise
    """
    try:
        # Extract org ID from token
        token_org_id = extract_caas_org_id_from_token(token)
        
        if not token_org_id:
            logger.warning("Cannot validate access: no caas_org_id in token")
            return False
        
        # Check if token org ID matches requested org ID
        if token_org_id != caas_org_id:
            logger.warning(f"Access denied: token org_id {token_org_id} != requested {caas_org_id}")
            return False
        
        logger.debug(f"Access validated for org_id: {caas_org_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error validating Cyoda environment access: {e}")
        return False


def get_user_cyoda_info(token: str) -> dict:
    """
    Get comprehensive Cyoda information from user token
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with Cyoda information
    """
    try:
        caas_org_id = extract_caas_org_id_from_token(token)
        cyoda_url = build_cyoda_environment_url(token)
        
        return {
            'caas_org_id': caas_org_id,
            'cyoda_url': cyoda_url,
            'client_host': getattr(config, 'CLIENT_HOST', 'kube.cyoda.org'),
            'has_access': caas_org_id is not None and cyoda_url is not None
        }
        
    except Exception as e:
        logger.error(f"Error getting user Cyoda info: {e}")
        return {
            'caas_org_id': None,
            'cyoda_url': None,
            'client_host': None,
            'has_access': False,
            'error': str(e)
        }
