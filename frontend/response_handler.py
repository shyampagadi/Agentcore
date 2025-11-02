"""
===============================================================================
MODULE: response_handler.py
===============================================================================

PURPOSE:
    Handles agent response formatting and display.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Format agent responses
    - Response processing: Handle different response types

USAGE EXAMPLES:
    from frontend.response_handler import format_response
    
    formatted = format_response(response)

WHAT THIS MODULE DOES:
    1. Formats agent responses
    2. Handles markdown
    3. Processes images/diagrams
    4. Error handling

RELATED FILES:
    - frontend/app.py - Uses this module

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Dict, Any

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def format_response(response: Dict[str, Any]) -> str:
    """
    Format agent response for display.
    
    ARGUMENTS:
        response (Dict[str, Any]): Agent response
    
    RETURNS:
        str: Formatted response
    """
    if 'error' in response:
        return f"❌ Error: {response.get('message', response.get('error'))}"
    
    return response.get('message', str(response))

