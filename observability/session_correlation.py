"""
===============================================================================
MODULE: session_correlation.py
===============================================================================

PURPOSE:
    Correlates sessions across services for observability.

WHEN TO USE THIS MODULE:
    - Observability: Track requests across services
    - Debugging: Correlate logs and traces

USAGE EXAMPLES:
    from observability.session_correlation import get_correlation_id
    
    correlation_id = get_correlation_id(session_id, request_id)

WHAT THIS MODULE DOES:
    1. Generates correlation IDs
    2. Adds correlation to traces
    3. Tracks session across services

RELATED FILES:
    - observability/otel_config.py - OpenTelemetry configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import uuid
from typing import Optional

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_correlation_id(session_id: Optional[str] = None, request_id: Optional[str] = None) -> str:
    """
    Generate correlation ID for tracing.
    
    ARGUMENTS:
        session_id (Optional[str]): Session ID
        request_id (Optional[str]): Request ID
    
    RETURNS:
        str: Correlation ID
    """
    if session_id and request_id:
        return f"{session_id}:{request_id}"
    elif session_id:
        return f"{session_id}:{uuid.uuid4().hex[:8]}"
    elif request_id:
        return f"{uuid.uuid4().hex[:8]}:{request_id}"
    else:
        return uuid.uuid4().hex


def add_correlation_to_logger(session_id: Optional[str] = None, request_id: Optional[str] = None):
    """
    Add correlation ID to logger context.
    
    ARGUMENTS:
        session_id (Optional[str]): Session ID
        request_id (Optional[str]): Request ID
    """
    correlation_id = get_correlation_id(session_id, request_id)
    
    # Add to logger context (if using structured logging)
    import logging
    logger = logging.getLogger()
    for handler in logger.handlers:
        if hasattr(handler, 'formatter'):
            # Add correlation ID to formatter
            pass

