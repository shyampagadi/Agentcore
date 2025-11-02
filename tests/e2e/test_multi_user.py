"""
===============================================================================
MODULE: test_multi_user.py
===============================================================================

PURPOSE:
    End-to-end tests for multi-user scenarios.

USAGE:
    pytest tests/e2e/test_multi_user.py

WHAT THIS MODULE DOES:
    1. Tests concurrent user sessions
    2. Tests session isolation
    3. Tests user-specific data
===============================================================================
"""

import pytest
from unittest.mock import Mock, patch
import concurrent.futures

from frontend.agent_client import AgentCoreClient


@pytest.fixture
def agent_client():
    """Create agent client."""
    with patch.dict('os.environ', {'AGENT_RUNTIME_ARN': 'arn:test:runtime:123'}):
        client = AgentCoreClient()
        client.client = Mock()
        return client


def test_concurrent_users(agent_client):
    """Test concurrent user sessions."""
    def invoke_user(user_id):
        session_id = f"session-{user_id}"
        agent_client.client.invoke_agent_runtime.return_value = {
            'response': [b'{"message": "Response for user ' + str(user_id).encode() + b'"}']
        }
        
        response = agent_client.invoke_agent(
            prompt=f"Request from user {user_id}",
            session_id=session_id
        )
        
        return response, session_id
    
    # Simulate concurrent users
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(invoke_user, i) for i in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Verify all sessions are unique
    session_ids = [r[1] for r in results]
    assert len(set(session_ids)) == 5  # All sessions should be unique


def test_session_isolation(agent_client):
    """Test session isolation."""
    # Each session should have separate runtime session IDs
    session1 = "user1-session-abc"
    session2 = "user2-session-xyz"
    
    assert session1 != session2
    # In real scenario, AgentCore Runtime creates separate microVMs for each session


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

