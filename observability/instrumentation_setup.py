"""
===============================================================================
MODULE: instrumentation_setup.py
===============================================================================

PURPOSE:
    Sets up OpenTelemetry instrumentation.

WHEN TO USE THIS MODULE:
    - Observability setup: Initialize instrumentation
    - Tracing: Enable distributed tracing

USAGE EXAMPLES:
    from observability.instrumentation_setup import initialize_instrumentation
    
    initialize_instrumentation()

WHAT THIS MODULE DOES:
    1. Initializes OpenTelemetry
    2. Configures exporters
    3. Sets up automatic instrumentation

RELATED FILES:
    - observability/otel_config.py - OpenTelemetry configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from observability.otel_config import setup_otel
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def initialize_instrumentation() -> None:
    """Initialize OpenTelemetry instrumentation."""
    setup_otel()
    logger.info("✅ Instrumentation initialized")

