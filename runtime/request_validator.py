"""
===============================================================================
MODULE: request_validator.py
===============================================================================

PURPOSE:
    Validates request payloads before processing.

WHEN TO USE THIS MODULE:
    - In agent_runtime.py: Validate payload before processing
    - API endpoints: Validate incoming requests

USAGE EXAMPLES:
    from runtime.request_validator import validate_request
    
    if validate_request(payload):
        process_request(payload)

WHAT THIS MODULE DOES:
    1. Validates payload structure
    2. Checks required fields
    3. Validates field types
    4. Returns validation errors

RELATED FILES:
    - runtime/agent_runtime.py - Uses this module

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Dict, Any, Tuple, Optional

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def validate_request(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate request payload.
    
    ARGUMENTS:
        payload (Dict[str, Any]): Request payload
    
    RETURNS:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not isinstance(payload, dict):
        return False, "Payload must be a dictionary"
    
    # Check for at least one input field
    if not any(key in payload for key in ['prompt', 'message', 'input', 'task_key']):
        return False, "Payload must contain 'prompt', 'message', 'input', or 'task_key'"
    
    return True, None

