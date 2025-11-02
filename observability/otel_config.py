"""
===============================================================================
MODULE: otel_config.py
===============================================================================

PURPOSE:
    Configures OpenTelemetry for observability.

WHEN TO USE THIS MODULE:
    - Observability setup: Initialize OpenTelemetry
    - Instrumentation: Configure tracing

USAGE EXAMPLES:
    from observability.otel_config import setup_otel
    
    setup_otel()

WHAT THIS MODULE DOES:
    1. Configures OpenTelemetry SDK
    2. Sets up exporters
    3. Configures resource attributes
    4. Initializes instrumentation

RELATED FILES:
    - observability/instrumentation_setup.py - Instrumentation setup

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
from typing import Optional

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def setup_otel() -> None:
    """Setup OpenTelemetry configuration."""
    try:
        from aws_opentelemetry_distro import AWSInstrumentor
        AWSInstrumentor().instrument()
        logger.info("✅ OpenTelemetry configured")
    except ImportError:
        logger.warning("⚠️  OpenTelemetry not available. Install aws-opentelemetry-distro")
    except Exception as e:
        logger.error(f"❌ Failed to setup OpenTelemetry: {e}")

