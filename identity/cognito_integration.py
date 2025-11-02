"""
===============================================================================
MODULE: cognito_integration.py
===============================================================================

PURPOSE:
    Integrates Cognito with AgentCore Identity module.

WHEN TO USE THIS MODULE:
    - Identity setup: Configure Cognito integration
    - User mapping: Map Cognito users to sessions

USAGE EXAMPLES:
    from identity.cognito_integration import setup_cognito_integration
    
    identity_config = setup_cognito_integration()

WHAT THIS MODULE DOES:
    1. Configures Cognito OAuth provider
    2. Maps Cognito users to AgentCore sessions
    3. Manages identity configuration

RELATED FILES:
    - identity/jwt_validator.py - Token validation
    - auth/cognito_client.py - Cognito client

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
from typing import Dict, Any

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_cognito_config() -> Dict[str, Any]:
    """
    Get Cognito configuration.
    
    RETURNS:
        Dict[str, Any]: Cognito configuration
    """
    return {
        'user_pool_id': os.getenv('COGNITO_USER_POOL_ID'),
        'client_id': os.getenv('COGNITO_CLIENT_ID'),
        'region': os.getenv('COGNITO_REGION', os.getenv('AWS_REGION', 'us-east-2'))
    }
