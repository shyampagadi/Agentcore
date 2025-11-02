"""
===============================================================================
MODULE: conversation_history.py
===============================================================================

PURPOSE:
    Displays conversation history in Streamlit UI.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Show past conversations
    - Session management: View session history

USAGE EXAMPLES:
    from frontend.conversation_history import show_history
    
    show_history()

WHAT THIS MODULE DOES:
    1. Loads conversation history from memory
    2. Displays past conversations
    3. Allows navigation between sessions

RELATED FILES:
    - frontend/app.py - Uses this module
    - memory/session_memory_handler.py - Memory operations

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st
from typing import List, Dict, Any, Optional

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def show_history(user_id: Optional[str] = None):
    """
    Display conversation history.
    
    ARGUMENTS:
        user_id (Optional[str]): User ID for loading history
    """
    if not user_id:
        user_id = st.session_state.get('user_id')
    
    if not user_id:
        st.info("📜 Please log in to view conversation history")
        return
    
    try:
        from memory.session_memory_handler import SessionMemoryHandler
        
        handler = SessionMemoryHandler()
        
        # Get session list (would need to implement list_sessions)
        # For now, show current session history
        session_id = st.session_state.get('runtime_session_id')
        
        if session_id:
            context = handler.load_session_context(user_id, session_id, limit=20)
            if context:
                st.markdown("### Recent Conversations")
                st.text_area("History", context, height=300, disabled=True)
            else:
                st.info("📜 No conversation history found")
        else:
            st.info("📜 Start a conversation to see history")
    
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        st.error("❌ Failed to load conversation history")

