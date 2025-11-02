"""
===============================================================================
MODULE: chat_interface.py
===============================================================================

PURPOSE:
    Provides chat interface components for Streamlit UI.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Display chat interface
    - Chat UI: Message display components

USAGE EXAMPLES:
    from frontend.chat_interface import display_chat_message
    
    display_chat_message("Hello", role="user")

WHAT THIS MODULE DOES:
    1. Displays chat messages
    2. Handles user input
    3. Shows typing indicators
    4. Formats messages

RELATED FILES:
    - frontend/app.py - Uses this module

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def display_chat_message(content: str, role: str = "assistant", timestamp: Optional[datetime] = None):
    """
    Display a chat message in Streamlit.
    
    ARGUMENTS:
        content (str): Message content
        role (str): Message role ('user' or 'assistant')
        timestamp (Optional[datetime]): Message timestamp
    """
    with st.chat_message(role):
        st.markdown(content)
        if timestamp:
            st.caption(timestamp.strftime("%Y-%m-%d %H:%M:%S"))


def display_typing_indicator():
    """Display typing indicator."""
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            st.empty()


def format_message_for_display(message: Dict[str, Any]) -> str:
    """
    Format message for display.
    
    ARGUMENTS:
        message (Dict[str, Any]): Message dictionary
    
    RETURNS:
        str: Formatted message string
    """
    if isinstance(message, dict):
        return message.get('content', message.get('message', str(message)))
    return str(message)
