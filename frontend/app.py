"""
===============================================================================
MODULE: app.py (Enhanced Streamlit Application)
===============================================================================

PURPOSE:
    Main Streamlit UI application with authentication and AgentCore Runtime integration.
    This is the enhanced version of the existing app.py with multi-user support.

WHEN TO USE THIS MODULE:
    - Run Streamlit app: streamlit run frontend/app.py
    - User interface: Primary entry point for users

USAGE EXAMPLES:
    # Run the app
    streamlit run frontend/app.py

    # Or use port
    streamlit run frontend/app.py --server.port 8501

WHAT THIS MODULE DOES:
    1. Provides authentication UI (Cognito login)
    2. Manages user sessions
    3. Displays chat interface
    4. Calls AgentCore Runtime via agent_client
    5. Shows predefined tasks
    6. Displays AWS configuration status
    7. Handles diagrams and images

RELATED FILES:
    - frontend/agent_client.py - Agent invocation
    - frontend/auth_ui.py - Authentication components
    - frontend/session_manager.py - Session management
    - auth/cognito_client.py - Cognito authentication

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 2.0.0 (Enhanced with AgentCore)
===============================================================================
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import enhanced modules
try:
    from frontend.agent_client import AgentCoreClient
    from frontend.session_manager import generate_session_id, get_current_session
    from frontend.auth_ui import show_login_page, check_authentication
    from auth.cognito_client import CognitoAuthClient
    from agents.cloud_engineer_agent import PREDEFINED_TASKS, get_detailed_mcp_status
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Configure page
st.set_page_config(
    page_title="AWS Cloud Engineer Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'agent_client' not in st.session_state:
    st.session_state['agent_client'] = AgentCoreClient()

# Main application
def main():
    """Main application entry point."""
    
    # Check authentication
    if not check_authentication():
        show_login_page()
        return
    
    # User is authenticated - show main app
    show_main_app()


def show_main_app():
    """Display main application interface."""
    
    # Sidebar
    with st.sidebar:
        st.title("🚀 Cloud Engineer Agent")
        
        # User info
        if st.session_state.get('user_id'):
            st.info(f"👤 User: {st.session_state['user_id'][:20]}...")
        
        # Session info
        session_id = get_current_session()
        if not session_id:
            session_id = generate_session_id(
                user_id=st.session_state.get('user_id'),
                description="main-session"
            )
        
        st.info(f"💬 Session: {session_id[:30]}...")
        
        # New session button
        if st.button("🔄 New Session"):
            if 'runtime_session_id' in st.session_state:
                del st.session_state['runtime_session_id']
            st.session_state['messages'] = []
            st.rerun()
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state['authenticated'] = False
            st.session_state['user_id'] = None
            st.session_state['access_token'] = None
            st.session_state['messages'] = []
            st.rerun()
        
        st.divider()
        
        # AWS Status
        st.subheader("🔧 AWS Status")
        mcp_status = get_detailed_mcp_status()
        for service, status in mcp_status.items():
            icon = "✅" if status else "❌"
            st.write(f"{icon} {service}")
    
    # Main content area
    st.title("🤖 AWS Cloud Engineer Agent")
    st.caption("Ask me anything about AWS infrastructure, and I'll help you!")
    
    # Display chat messages
    for message in st.session_state['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            
            # Display images if present
            if 'images' in message:
                for img_path in message['images']:
                    if os.path.exists(img_path):
                        st.image(img_path)
    
    # Predefined tasks dropdown
    with st.expander("📋 Predefined Tasks"):
        task_key = st.selectbox(
            "Select a predefined task:",
            options=[''] + list(PREDEFINED_TASKS.keys()),
            format_func=lambda x: PREDEFINED_TASKS.get(x, 'Select a task...')
        )
        
        if task_key:
            if st.button(f"Execute: {PREDEFINED_TASKS[task_key]}"):
                execute_task(task_key=task_key)
    
    # Chat input
    user_input = st.chat_input("Enter your AWS question or task...")
    
    if user_input:
        execute_task(prompt=user_input)


def execute_task(prompt: str = None, task_key: str = None):
    """
    Execute agent task.
    
    ARGUMENTS:
        prompt (str): Custom user prompt
        task_key (str): Predefined task key
    """
    # Add user message to chat
    if prompt:
        st.session_state['messages'].append({
            'role': 'user',
            'content': prompt
        })
    elif task_key:
        task_description = PREDEFINED_TASKS.get(task_key, '')
        st.session_state['messages'].append({
            'role': 'user',
            'content': f"Task: {task_description}"
        })
    
    # Show assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Get session ID
            session_id = get_current_session()
            if not session_id:
                session_id = generate_session_id(
                    user_id=st.session_state.get('user_id')
                )
            
            # Get access token
            access_token = st.session_state.get('access_token')
            
            # Invoke agent
            client = st.session_state['agent_client']
            
            if prompt:
                response = client.invoke_agent(
                    prompt=prompt,
                    session_id=session_id,
                    access_token=access_token
                )
            elif task_key:
                response = client.invoke_agent(
                    prompt=PREDEFINED_TASKS.get(task_key, ''),
                    session_id=session_id,
                    access_token=access_token,
                    task_key=task_key
                )
            else:
                response = {'error': 'No prompt or task provided'}
            
            # Display response
            if 'error' in response:
                st.error(f"❌ Error: {response.get('message', response.get('error'))}")
            else:
                message = response.get('message', str(response))
                st.markdown(message)
                
                # Add to chat history
                st.session_state['messages'].append({
                    'role': 'assistant',
                    'content': message
                })
                
                # Check for images (diagrams)
                # TODO: Handle image responses from agent


if __name__ == "__main__":
    main()
