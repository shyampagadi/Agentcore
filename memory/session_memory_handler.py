"""
===============================================================================
MODULE: session_memory_handler.py
===============================================================================

PURPOSE:
    Handles session-specific memory operations.

WHEN TO USE THIS MODULE:
    - Session management: Load/save session context
    - Memory integration: Session-specific memory operations

USAGE EXAMPLES:
    from memory.session_memory_handler import SessionMemoryHandler
    
    handler = SessionMemoryHandler()
    context = handler.load_session_context(user_id, session_id)

WHAT THIS MODULE DOES:
    1. Loads session context from memory
    2. Saves session context to memory
    3. Manages session history

RELATED FILES:
    - memory/memory_manager.py - Uses memory manager
    - runtime/memory_integration.py - Uses this handler

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Optional, Dict, Any, List

from memory.memory_manager import MemoryManager
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class SessionMemoryHandler:
    """
    Handles session-specific memory operations.
    """
    
    def __init__(self):
        """Initialize session memory handler."""
        self.memory_manager = MemoryManager()
    
    def load_session_context(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> str:
        """
        Load session context from memory.
        
        ARGUMENTS:
            user_id (str): User identifier
            session_id (str): Session identifier
            limit (int): Number of events to load
        
        RETURNS:
            str: Formatted context string
        """
        events = self.memory_manager.read_events(user_id, session_id, limit=limit)
        
        if not events:
            return ""
        
        # Format events as context
        context_parts = []
        for event in events:
            if 'message' in event and 'response' in event:
                context_parts.append(f"User: {event['message']}")
                context_parts.append(f"Assistant: {event['response']}")
        
        return "\n".join(context_parts)
    
    def save_conversation(
        self,
        user_id: str,
        session_id: str,
        message: str,
        response: str
    ) -> bool:
        """
        Save conversation to memory.
        
        ARGUMENTS:
            user_id (str): User identifier
            session_id (str): Session identifier
            message (str): User message
            response (str): Agent response
        
        RETURNS:
            bool: True if successful
        """
        return self.memory_manager.write_event(user_id, session_id, message, response)
