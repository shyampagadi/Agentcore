"""
===============================================================================
MODULE: session_manager.py
===============================================================================

PURPOSE:
    Manages session IDs for Streamlit UI.
    Generates unique session IDs and manages session state.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Generate session IDs for conversations
    - Session management: Track active sessions

USAGE EXAMPLES:
    from frontend.session_manager import generate_session_id, get_current_session
    
    session_id = generate_session_id(user_id="user-123")
    current_session = get_current_session()

WHAT THIS MODULE DOES:
    1. Generates unique session IDs
    2. Stores session IDs in Streamlit session state
    3. Retrieves current session
    4. Manages session lifecycle

RELATED FILES:
    - frontend/app.py - Uses this module
    - utils/session_utils.py - Session ID utilities

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st
from typing import Optional

from utils.session_utils import generate_session_id as _generate_session_id
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def generate_session_id(user_id: Optional[str] = None, description: Optional[str] = None) -> str:
    """
    Generate session ID for Streamlit session.
    
    ARGUMENTS:
        user_id (Optional[str]): User ID from Cognito
        description (Optional[str]): Session description
    
    RETURNS:
        str: Generated session ID
    """
    if not user_id:
        user_id = st.session_state.get('user_id', 'anonymous')
    
    if not description:
        description = "streamlit-session"
    
    session_id = _generate_session_id(user_id, description)
    
    # Store in Streamlit session state
    st.session_state['runtime_session_id'] = session_id
    
    return session_id


def get_current_session() -> Optional[str]:
    """
    Get current session ID from Streamlit session state.
    
    RETURNS:
        Optional[str]: Current session ID or None
    """
    return st.session_state.get('runtime_session_id')


def reset_session() -> None:
    """Reset current session."""
    if 'runtime_session_id' in st.session_state:
        del st.session_state['runtime_session_id']
    logger.info("Session reset")

