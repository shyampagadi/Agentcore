"""
===============================================================================
MODULE: test_auth.py
===============================================================================

PURPOSE:
    Tests for authentication functionality.

WHEN TO USE THIS MODULE:
    - Testing: Run authentication tests
    - CI/CD: Automated testing pipeline

USAGE EXAMPLES:
    pytest auth/test_auth.py
    pytest auth/test_auth.py::test_cognito_client_initialization

WHAT THIS MODULE DOES:
    1. Tests Cognito client initialization
    2. Tests authentication flow
    3. Tests token validation
    4. Tests error handling

RELATED FILES:
    - auth/cognito_client.py - Module being tested
    - identity/jwt_validator.py - Token validation

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from auth.cognito_client import CognitoAuthClient
from auth.cognito_verification import verify_cognito_configuration


@pytest.fixture
def mock_boto3_client():
    """Mock boto3 client for Cognito."""
    with patch('boto3.client') as mock_client:
        mock_cognito = MagicMock()
        mock_client.return_value = mock_cognito
        yield mock_cognito


@pytest.fixture
def auth_client(mock_boto3_client):
    """Create CognitoAuthClient with mocked client."""
    with patch.dict(os.environ, {
        'COGNITO_USER_POOL_ID': 'us-east-2_test123',
        'COGNITO_CLIENT_ID': 'test_client_id'
    }):
        client = CognitoAuthClient()
        client.cognito_client = mock_boto3_client
        return client


def test_cognito_client_initialization(auth_client):
    """Test CognitoAuthClient initialization."""
    assert auth_client is not None
    assert auth_client.user_pool_id == 'us-east-2_test123'
    assert auth_client.client_id == 'test_client_id'


def test_authenticate_user_success(auth_client, mock_boto3_client):
    """Test successful user authentication."""
    mock_boto3_client.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'test_access_token',
            'IdToken': 'test_id_token',
            'RefreshToken': 'test_refresh_token'
        }
    }
    
    result = auth_client.authenticate_user('test@example.com', 'password123')
    
    assert result is True
    assert auth_client._access_token == 'test_access_token'
    assert auth_client._id_token == 'test_id_token'
    mock_boto3_client.initiate_auth.assert_called_once()


def test_authenticate_user_failure(auth_client, mock_boto3_client):
    """Test failed user authentication."""
    from botocore.exceptions import ClientError
    
    error_response = {
        'Error': {
            'Code': 'NotAuthorizedException',
            'Message': 'Incorrect username or password'
        }
    }
    
    mock_boto3_client.initiate_auth.side_effect = ClientError(error_response, 'initiate_auth')
    
    result = auth_client.authenticate_user('test@example.com', 'wrong_password')
    
    assert result is False


def test_get_access_token(auth_client):
    """Test getting access token."""
    auth_client._access_token = 'test_token'
    assert auth_client.get_access_token() == 'test_token'


def test_get_user_info(auth_client):
    """Test getting user info from ID token."""
    auth_client._id_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJzdWIiOiJ1c2VyLTEyMyJ9.test'
    
    with patch('auth.cognito_client.jwt') as mock_jwt:
        mock_jwt.decode.return_value = {
            'email': 'test@example.com',
            'sub': 'user-123',
            'cognito:username': 'test@example.com'
        }
        
        user_info = auth_client.get_user_info()
        
        assert user_info is not None
        assert user_info['email'] == 'test@example.com'
        assert user_info['sub'] == 'user-123'


def test_verify_cognito_configuration():
    """Test Cognito configuration verification."""
    with patch.dict(os.environ, {
        'COGNITO_USER_POOL_ID': 'us-east-2_test123',
        'COGNITO_CLIENT_ID': 'test_client_id'
    }):
        with patch('auth.cognito_verification.boto3.client') as mock_client:
            mock_cognito = MagicMock()
            mock_client.return_value = mock_cognito
            
            # Mock pool exists
            mock_cognito.describe_user_pool.return_value = {
                'UserPool': {
                    'Id': 'us-east-2_test123',
                    'Name': 'test-pool',
                    'Status': 'Active',
                    'MfaConfiguration': 'OFF',
                    'AutoVerifiedAttributes': ['email'],
                    'UsernameAttributes': ['email']
                }
            }
            
            # Mock client exists
            mock_cognito.describe_user_pool_client.return_value = {
                'UserPoolClient': {
                    'ClientId': 'test_client_id',
                    'ClientName': 'test-client',
                    'AllowedOAuthFlows': ['code'],
                    'CallbackURLs': ['http://localhost:8501']
                }
            }
            
            result = verify_cognito_configuration()
            
            assert result['valid'] is True
            assert result['pool_exists'] is True
            assert result['client_exists'] is True
            assert result['oauth_configured'] is True


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
