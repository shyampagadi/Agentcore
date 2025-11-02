"""
===============================================================================
MODULE: cognito_client.py
===============================================================================

PURPOSE:
    Provides Cognito client wrapper for Streamlit authentication.
    Handles user authentication, token management, and session handling.

WHEN TO USE THIS MODULE:
    - In Streamlit app: For user login/logout
    - Token validation: Checking if user is authenticated
    - User info retrieval: Getting user details from tokens

USAGE EXAMPLES:
    # In Streamlit app
    from auth.cognito_client import CognitoAuthClient
    
    auth_client = CognitoAuthClient()
    if auth_client.login(username, password):
        token = auth_client.get_access_token()
        user_info = auth_client.get_user_info()

WHAT THIS MODULE DOES:
    1. Handles user authentication (login/logout)
    2. Manages JWT tokens (access, ID, refresh)
    3. Validates tokens
    4. Retrieves user information
    5. Handles token refresh

RELATED FILES:
    - identity/jwt_validator.py - Token validation logic
    - frontend/auth_ui.py - UI components using this client

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


class CognitoAuthClient:
    """
    Cognito authentication client for Streamlit.
    
    Handles user authentication, token management, and user info retrieval.
    """
    
    def __init__(self):
        """Initialize Cognito auth client."""
        self.user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = os.getenv('COGNITO_CLIENT_ID')
        self.region = get_aws_region()
        self.cognito_client = boto3.client('cognito-idp', region_name=self.region)
        
        # Token storage (in production, use secure storage)
        self._access_token: Optional[str] = None
        self._id_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate user with username and password.
        
        ARGUMENTS:
            username (str): Username (email)
            password (str): User password
        
        RETURNS:
            bool: True if authentication successful
        """
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            # Extract tokens
            auth_result = response.get('AuthenticationResult', {})
            self._access_token = auth_result.get('AccessToken')
            self._id_token = auth_result.get('IdToken')
            self._refresh_token = auth_result.get('RefreshToken')
            
            logger.info(f"✅ User authenticated: {username}")
            return True
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"❌ Authentication failed: {error_code}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token."""
        return self._access_token
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get user information from ID token.
        
        RETURNS:
            Dict[str, Any]: User information (email, sub, etc.)
        """
        if not self._id_token:
            return None
        
        # Decode JWT token (simplified - use jwt_validator for full validation)
        try:
            import jwt
            decoded = jwt.decode(self._id_token, options={"verify_signature": False})
            return {
                'email': decoded.get('email'),
                'sub': decoded.get('sub'),
                'username': decoded.get('cognito:username')
            }
        except Exception as e:
            logger.error(f"❌ Failed to decode token: {e}")
            return None

