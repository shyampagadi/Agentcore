"""
===============================================================================
MODULE: user_mapper.py
===============================================================================

PURPOSE:
    Maps Cognito users to AgentCore sessions.

WHEN TO USE THIS MODULE:
    - Session management: Map users to sessions
    - User tracking: Track user sessions

USAGE EXAMPLES:
    from identity.user_mapper import map_user_to_session
    
    session_id = map_user_to_session(user_id="user-123")

WHAT THIS MODULE DOES:
    1. Maps user IDs to session IDs
    2. Tracks user sessions
    3. Provides user session lookup

RELATED FILES:
    - frontend/session_manager.py - Uses user mapping
    - runtime/session_handler.py - Session handling

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Dict, Optional

from utils.session_utils import generate_session_id
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def map_user_to_session(user_id: str, description: Optional[str] = None) -> str:
    """
    Map user ID to session ID.
    
    ARGUMENTS:
        user_id (str): User identifier
        description (Optional[str]): Session description
    
    RETURNS:
        str: Generated session ID
    """
    return generate_session_id(user_id, description or "agent-session")
