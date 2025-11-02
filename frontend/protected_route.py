"""
===============================================================================
MODULE: protected_route.py
===============================================================================

PURPOSE:
    Provides route protection decorator for Streamlit pages.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Protect routes/pages
    - Authentication: Require login for pages

USAGE EXAMPLES:
    from frontend.protected_route import require_auth
    
    @require_auth
    def my_page():
        st.write("Protected content")

WHAT THIS MODULE DOES:
    1. Checks authentication
    2. Redirects to login if not authenticated
    3. Protects routes

RELATED FILES:
    - frontend/app.py - Uses this module
    - frontend/auth_ui.py - Authentication UI

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st
from functools import wraps
from typing import Callable

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication.
    
    ARGUMENTS:
        func (Callable): Function to protect
    
    RETURNS:
        Callable: Protected function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            st.warning("🔐 Please log in to access this page")
            from frontend.auth_ui import show_login_page
            show_login_page()
            return
        return func(*args, **kwargs)
    return wrapper

