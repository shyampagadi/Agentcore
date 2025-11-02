"""
===============================================================================
MODULE: context_builder.py
===============================================================================

PURPOSE:
    Builds context for agent from memory and previous conversations.

WHEN TO USE THIS MODULE:
    - In runtime: Build context before agent execution
    - Context management: Combine memory and current input

USAGE EXAMPLES:
    from runtime.context_builder import build_context
    
    context = build_context(session_id, user_id, current_prompt)

WHAT THIS MODULE DOES:
    1. Loads conversation history from memory
    2. Performs semantic search if needed
    3. Formats context for agent
    4. Manages context length

RELATED FILES:
    - runtime/memory_integration.py - Memory operations
    - memory/session_memory_handler.py - Session memory

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Optional, List, Dict, Any

from runtime.memory_integration import load_context
from memory.semantic_search import search_memory
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

# Maximum context length (in characters)
MAX_CONTEXT_LENGTH = 10000


def build_context(
    session_id: str,
    user_id: Optional[str],
    current_prompt: str,
    include_history: bool = True,
    include_semantic: bool = False,
    max_history_items: int = 10
) -> str:
    """
    Build context string for agent.
    
    ARGUMENTS:
        session_id (str): Session ID
        user_id (Optional[str]): User ID
        current_prompt (str): Current user prompt
        include_history (bool): Include conversation history
        include_semantic (bool): Include semantic search results
        max_history_items (int): Maximum history items to include
    
    RETURNS:
        str: Formatted context string
    """
    context_parts = []
    
    # Add conversation history
    if include_history:
        history = load_context(session_id, user_id, limit=max_history_items)
        if history:
            context_parts.append("Previous conversation:")
            context_parts.append(history)
            context_parts.append("")
    
    # Add semantic search results
    if include_semantic and user_id:
        semantic_results = search_memory(current_prompt, user_id, limit=5)
        if semantic_results:
            context_parts.append("Relevant past conversations:")
            for result in semantic_results:
                # Format semantic result
                if isinstance(result, dict) and 'content' in result:
                    context_parts.append(f"- {result['content'][:200]}...")
            context_parts.append("")
    
    # Add current prompt
    context_parts.append("Current request:")
    context_parts.append(current_prompt)
    
    # Combine and truncate if needed
    full_context = "\n".join(context_parts)
    
    if len(full_context) > MAX_CONTEXT_LENGTH:
        logger.warning(f"Context truncated from {len(full_context)} to {MAX_CONTEXT_LENGTH} characters")
        # Truncate from the beginning (keep current prompt)
        truncated = full_context[-MAX_CONTEXT_LENGTH:]
        full_context = truncated
    
    return full_context


def format_conversation_history(events: List[Dict[str, Any]]) -> str:
    """
    Format conversation events into context string.
    
    ARGUMENTS:
        events (List[Dict[str, Any]]): List of conversation events
    
    RETURNS:
        str: Formatted history string
    """
    if not events:
        return ""
    
    formatted = []
    for event in events:
        if isinstance(event, dict):
            user_msg = event.get('message', event.get('user_message', ''))
            agent_msg = event.get('response', event.get('agent_response', ''))
            
            if user_msg:
                formatted.append(f"User: {user_msg}")
            if agent_msg:
                formatted.append(f"Assistant: {agent_msg}")
    
    return "\n".join(formatted)

