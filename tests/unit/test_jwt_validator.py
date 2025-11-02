"""
===============================================================================
MODULE: test_jwt_validator.py
===============================================================================

PURPOSE:
    Unit tests for JWT validator.

USAGE:
    pytest tests/unit/test_jwt_validator.py

WHAT THIS MODULE DOES:
    1. Tests JWT token validation
    2. Tests token decoding
    3. Tests error handling
===============================================================================
"""

import pytest
from unittest.mock import Mock, patch
import os

from identity.jwt_validator import validate_token, get_jwks


@pytest.fixture
def mock_jwks():
    """Mock JWKS response."""
    return {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key-id",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB"
            }
        ]
    }


def test_validate_token(mock_jwks):
    """Test JWT token validation."""
    with patch('identity.jwt_validator.get_jwks', return_value=mock_jwks):
        with patch('identity.jwt_validator.jwt') as mock_jwt:
            mock_jwt.decode.return_value = {
                'email': 'test@example.com',
                'sub': 'user-123'
            }
            
            token = "test.token.here"
            result = validate_token(token)
            
            assert result is not None
            assert result['email'] == 'test@example.com'


def test_validate_token_expired():
    """Test expired token validation."""
    with patch('identity.jwt_validator.jwt') as mock_jwt:
        import jwt
        mock_jwt.ExpiredSignatureError = jwt.ExpiredSignatureError
        mock_jwt.decode.side_effect = jwt.ExpiredSignatureError("Token expired")
        
        result = validate_token("expired.token")
        
        assert result is None


def test_get_jwks():
    """Test JWKS retrieval."""
    with patch('identity.jwt_validator.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"keys": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {
            'COGNITO_USER_POOL_ID': 'us-east-2_test123',
            'AWS_REGION': 'us-east-2'
        }):
            jwks = get_jwks()
            assert isinstance(jwks, dict)


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

