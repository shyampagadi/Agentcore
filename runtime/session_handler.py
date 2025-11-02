"""
===============================================================================
MODULE: session_handler.py
===============================================================================

PURPOSE:
    Handles session management for AgentCore Runtime requests.
    Extracts session information from RequestContext and manages session state.

WHEN TO USE THIS MODULE:
    - In agent_runtime.py: Extract session info from context
    - Memory integration: Associate events with sessions
    - Logging: Add session context to logs

USAGE EXAMPLES:
    from runtime.session_handler import extract_session_info
    
    session_info = extract_session_info(context)
    session_id = session_info['session_id']
    user_id = session_info['user_id']

WHAT THIS MODULE DOES:
    1. Extracts session ID from RequestContext
    2. Extracts user ID from RequestContext
    3. Validates session information
    4. Provides session metadata

RELATED FILES:
    - runtime/agent_runtime.py - Uses this module
    - memory/session_memory_handler.py - Uses session info for memory

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Dict, Any, Optional
from bedrock_agentcore.context import RequestContext

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def extract_session_info(context: RequestContext) -> Dict[str, Optional[str]]:
    """
    Extract session information from RequestContext.
    
    ARGUMENTS:
        context (RequestContext): AgentCore Runtime context
    
    RETURNS:
        Dict[str, Optional[str]]: Session information
    """
    session_id = getattr(context, 'session_id', None)
    user_id = getattr(context, 'user_id', None)
    request_id = getattr(context, 'request_id', None)
    
    return {
        'session_id': session_id,
        'user_id': user_id,
        'request_id': request_id
    }

