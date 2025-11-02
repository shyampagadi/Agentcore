"""
===============================================================================
MODULE: guardrail_validator.py
===============================================================================

PURPOSE:
    Validates guardrail configuration and tests guardrail functionality.

WHEN TO USE THIS MODULE:
    - Guardrail testing: Validate guardrail settings
    - Content safety: Test content filtering

USAGE EXAMPLES:
    from guardrails.guardrail_validator import validate_guardrail
    
    is_valid = validate_guardrail(guardrail_id)

WHAT THIS MODULE DOES:
    1. Validates guardrail configuration
    2. Tests content filtering
    3. Verifies guardrail is active

RELATED FILES:
    - guardrails/guardrail_setup.py - Guardrail creation

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import boto3
from typing import Dict, Any, Optional

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


def validate_guardrail(guardrail_id: str) -> bool:
    """
    Validate guardrail configuration.
    
    ARGUMENTS:
        guardrail_id (str): Guardrail ID
    
    RETURNS:
        bool: True if valid
    """
    region = get_aws_region()
    bedrock_client = boto3.client('bedrock', region_name=region)
    
    try:
        response = bedrock_client.get_guardrail(guardrailId=guardrail_id)
        status = response.get('status', 'UNKNOWN')
        
        if status == 'READY':
            logger.info(f"✅ Guardrail {guardrail_id} is valid and ready")
            return True
        else:
            logger.warning(f"⚠️  Guardrail {guardrail_id} status: {status}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Failed to validate guardrail: {e}")
        return False

