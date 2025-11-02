"""
===============================================================================
MODULE: test_runtime_local.py
===============================================================================

PURPOSE:
    Local testing script for AgentCore Runtime.

WHEN TO USE THIS MODULE:
    - Development: Test runtime locally before deployment
    - Debugging: Test agent functionality

USAGE EXAMPLES:
    python runtime/test_runtime_local.py

WHAT THIS MODULE DOES:
    1. Tests agent runtime locally
    2. Simulates AgentCore Runtime requests
    3. Validates agent responses
    4. Tests error handling

RELATED FILES:
    - runtime/agent_runtime.py - Runtime being tested

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.agent_runtime import handle_invocation, health_check
from runtime.request_validator import validate_request
from bedrock_agentcore.context import RequestContext
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class MockRequestContext:
    """Mock RequestContext for local testing."""
    def __init__(self, session_id: str = "test-session-123", user_id: str = "test-user-456"):
        self.session_id = session_id
        self.user_id = user_id
        self.request_id = "test-request-789"


def test_health_check():
    """Test health check endpoint."""
    logger.info("Testing health check...")
    result = health_check()
    
    assert result['status'] == 'healthy'
    assert 'timestamp' in result
    logger.info("✅ Health check passed")


def test_agent_invocation():
    """Test agent invocation."""
    logger.info("Testing agent invocation...")
    
    # Create mock context
    context = MockRequestContext()
    
    # Test payload
    payload = {
        "prompt": "List all EC2 instances"
    }
    
    # Validate request
    is_valid, error = validate_request(payload)
    assert is_valid, f"Request validation failed: {error}"
    
    # Invoke agent
    response = handle_invocation(payload, context)
    
    assert 'message' in response or 'error' in response
    assert response.get('session_id') == context.session_id
    assert response.get('user_id') == context.user_id
    
    logger.info("✅ Agent invocation passed")
    logger.info(f"   Response length: {len(response.get('message', ''))} characters")


def test_agent_invocation_with_task():
    """Test agent invocation with predefined task."""
    logger.info("Testing agent invocation with predefined task...")
    
    context = MockRequestContext()
    payload = {
        "task_key": "ec2_status"
    }
    
    response = handle_invocation(payload, context)
    
    assert 'message' in response or 'error' in response
    logger.info("✅ Predefined task invocation passed")


def test_error_handling():
    """Test error handling."""
    logger.info("Testing error handling...")
    
    context = MockRequestContext()
    
    # Test invalid payload
    invalid_payload = {}
    is_valid, error = validate_request(invalid_payload)
    assert not is_valid
    
    # Test empty prompt
    empty_payload = {"prompt": ""}
    response = handle_invocation(empty_payload, context)
    assert 'error' in response or 'message' in response
    
    logger.info("✅ Error handling passed")


def main():
    """Run all tests."""
    logger.info("="*70)
    logger.info("Local Runtime Testing")
    logger.info("="*70)
    logger.info("")
    
    try:
        test_health_check()
        logger.info("")
        
        test_agent_invocation()
        logger.info("")
        
        test_agent_invocation_with_task()
        logger.info("")
        
        test_error_handling()
        logger.info("")
        
        logger.info("="*70)
        logger.info("✅ All tests passed!")
        logger.info("="*70)
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

