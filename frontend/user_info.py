"""
===============================================================================
MODULE: user_info.py
===============================================================================

PURPOSE:
    Displays user information in Streamlit UI.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Show user profile
    - User dashboard: Display user details

USAGE EXAMPLES:
    from frontend.user_info import show_user_info
    
    show_user_info()

WHAT THIS MODULE DOES:
    1. Displays user information
    2. Shows user profile
    3. Provides user settings

RELATED FILES:
    - frontend/app.py - Uses this module

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def show_user_info():
    """Display user information."""
    user_id = st.session_state.get('user_id')
    if user_id:
        st.info(f"👤 User: {user_id}")

