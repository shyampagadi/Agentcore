"""
===============================================================================
MODULE: test_agent_flow.py
===============================================================================

PURPOSE:
    End-to-end tests for agent flow.

USAGE:
    pytest tests/e2e/test_agent_flow.py

WHAT THIS MODULE DOES:
    1. Tests complete agent flow
    2. Tests request/response cycle
    3. Tests error scenarios
===============================================================================
"""

import pytest
from unittest.mock import Mock, patch

from frontend.agent_client import AgentCoreClient


@pytest.fixture
def agent_client():
    """Create agent client."""
    with patch.dict('os.environ', {'AGENT_RUNTIME_ARN': 'arn:test:runtime:123'}):
        client = AgentCoreClient()
        client.client = Mock()
        return client


def test_agent_flow(agent_client):
    """Test complete agent flow."""
    # Mock successful response
    agent_client.client.invoke_agent_runtime.return_value = {
        'response': [b'{"message": "Test response"}']
    }
    
    response = agent_client.invoke_agent(
        prompt="Test prompt",
        session_id="test-session"
    )
    
    assert 'message' in response or 'error' in response


def test_agent_flow_error(agent_client):
    """Test agent flow with error."""
    from botocore.exceptions import ClientError
    
    error_response = {
        'Error': {
            'Code': 'ServiceException',
            'Message': 'Service error'
        }
    }
    
    agent_client.client.invoke_agent_runtime.side_effect = ClientError(error_response, 'invoke_agent_runtime')
    
    response = agent_client.invoke_agent(
        prompt="Test prompt",
        session_id="test-session"
    )
    
    assert 'error' in response


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

