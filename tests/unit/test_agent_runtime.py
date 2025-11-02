"""
===============================================================================
MODULE: test_agent_runtime.py
===============================================================================

PURPOSE:
    Unit tests for agent runtime.

USAGE:
    pytest tests/unit/test_agent_runtime.py

WHAT THIS MODULE DOES:
    1. Tests runtime initialization
    2. Tests request handling
    3. Tests error handling
===============================================================================
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from runtime.agent_runtime import handle_invocation, health_check
from runtime.request_validator import validate_request


class MockContext:
    """Mock RequestContext."""
    def __init__(self):
        self.session_id = "test-session"
        self.user_id = "test-user"
        self.request_id = "test-request"


@pytest.fixture
def mock_context():
    """Create mock context."""
    return MockContext()


@pytest.fixture
def mock_agent():
    """Mock agent execution."""
    with patch('runtime.agent_runtime.execute_custom_task') as mock_execute:
        mock_execute.return_value = "Test response"
        yield mock_execute


def test_health_check():
    """Test health check."""
    result = health_check()
    
    assert result['status'] == 'healthy'
    assert 'timestamp' in result
    assert 'version' in result


def test_handle_invocation_success(mock_context, mock_agent):
    """Test successful invocation."""
    payload = {"prompt": "Test prompt"}
    
    response = handle_invocation(payload, mock_context)
    
    assert 'message' in response
    assert response['session_id'] == mock_context.session_id
    assert response['user_id'] == mock_context.user_id


def test_handle_invocation_with_task(mock_context):
    """Test invocation with predefined task."""
    with patch('runtime.agent_runtime.execute_predefined_task') as mock_task:
        mock_task.return_value = "Task response"
        
        payload = {"task_key": "ec2_status"}
        response = handle_invocation(payload, mock_context)
        
        assert 'message' in response
        mock_task.assert_called_once_with("ec2_status")


def test_handle_invocation_invalid_payload(mock_context):
    """Test invocation with invalid payload."""
    payload = {}
    
    response = handle_invocation(payload, mock_context)
    
    assert 'error' in response


def test_validate_request():
    """Test request validation."""
    # Valid request
    valid_payload = {"prompt": "Test"}
    is_valid, error = validate_request(valid_payload)
    assert is_valid
    assert error is None
    
    # Invalid request
    invalid_payload = {}
    is_valid, error = validate_request(invalid_payload)
    assert not is_valid
    assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

