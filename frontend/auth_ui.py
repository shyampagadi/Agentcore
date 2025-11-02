"""
===============================================================================
MODULE: auth_ui.py
===============================================================================

PURPOSE:
    Provides authentication UI components for Streamlit.
    Handles login/logout flows and authentication state management.

WHEN TO USE THIS MODULE:
    - In Streamlit app: For user authentication
    - Login page: Display login form

USAGE EXAMPLES:
    from frontend.auth_ui import show_login_page, check_authentication
    
    if not check_authentication():
        show_login_page()
        return

WHAT THIS MODULE DOES:
    1. Displays login form
    2. Handles authentication logic
    3. Manages authentication state
    4. Validates tokens

RELATED FILES:
    - frontend/app.py - Uses this module
    - auth/cognito_client.py - Cognito authentication

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import streamlit as st
from typing import Optional

from auth.cognito_client import CognitoAuthClient
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def show_login_page():
    """Display login page."""
    st.title("🔐 Login")
    st.caption("Enter your credentials to access the Cloud Engineer Agent")
    
    with st.form("login_form"):
        username = st.text_input("Username (Email)", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                auth_client = CognitoAuthClient()
                if auth_client.authenticate_user(username, password):
                    # Store authentication state
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = username
                    st.session_state['access_token'] = auth_client.get_access_token()
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")
            else:
                st.error("❌ Please enter both username and password.")


def check_authentication() -> bool:
    """
    Check if user is authenticated.
    
    RETURNS:
        bool: True if authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)

