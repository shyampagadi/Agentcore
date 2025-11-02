"""
===============================================================================
MODULE: guardrail_integration.py
===============================================================================

PURPOSE:
    Integrates Bedrock Guardrails with agent runtime.

WHEN TO USE THIS MODULE:
    - In runtime: Apply guardrails to agent requests
    - Content safety: Filter unsafe content

USAGE EXAMPLES:
    from runtime.guardrail_integration import apply_guardrail
    
    safe_response = apply_guardrail(prompt, response)

WHAT THIS MODULE DOES:
    1. Applies guardrails to user input
    2. Applies guardrails to agent output
    3. Handles guardrail violations
    4. Logs violations for monitoring

RELATED FILES:
    - runtime/agent_runtime.py - Uses this module
    - guardrails/guardrail_setup.py - Guardrail configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region
from guardrails.guardrail_config import get_default_config

logger = setup_logger(__name__)


def apply_guardrail(
    text: str,
    guardrail_id: Optional[str] = None,
    guardrail_version: Optional[str] = None,
    check_input: bool = True
) -> Dict[str, Any]:
    """
    Apply guardrail to text content.
    
    ARGUMENTS:
        text (str): Text to check
        guardrail_id (Optional[str]): Guardrail ID (from env if not provided)
        guardrail_version (Optional[str]): Guardrail version (from env if not provided)
        check_input (bool): True to check input, False to check output
    
    RETURNS:
        Dict[str, Any]: Guardrail result
            {
                'allowed': bool,
                'violations': List[Dict],
                'filtered_text': str
            }
    """
    if not guardrail_id:
        guardrail_id = os.getenv('BEDROCK_GUARDRAIL_ID')
    
    if not guardrail_id:
        logger.debug("No guardrail configured, allowing content")
        return {'allowed': True, 'violations': [], 'filtered_text': text}
    
    if not guardrail_version:
        guardrail_version = os.getenv('BEDROCK_GUARDRAIL_VERSION', 'DRAFT')
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name=get_aws_region())
        
        # Use guardrail check API
        response = bedrock_client.check_guardrail_content(
            GuardrailIdentifier=guardrail_id,
            GuardrailVersion=guardrail_version,
            Content={
                'text': text
            }
        )
        
        violations = response.get('violations', [])
        allowed = len(violations) == 0
        
        result = {
            'allowed': allowed,
            'violations': violations,
            'filtered_text': text  # Guardrail doesn't modify text, just flags violations
        }
        
        if not allowed:
            logger.warning(f"⚠️  Guardrail violation detected: {len(violations)} violations")
            for violation in violations:
                logger.warning(f"   - {violation.get('type', 'Unknown')}: {violation.get('policy', {}).get('name', 'Unknown')}")
        
        return result
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ Guardrail check failed: {error_code}")
        # On error, allow content but log warning
        return {'allowed': True, 'violations': [], 'filtered_text': text, 'error': error_code}
    
    except Exception as e:
        logger.error(f"❌ Unexpected error checking guardrail: {e}")
        return {'allowed': True, 'violations': [], 'filtered_text': text, 'error': str(e)}


def check_input_guardrail(prompt: str) -> Dict[str, Any]:
    """Check user input with guardrail."""
    return apply_guardrail(prompt, check_input=True)


def check_output_guardrail(response: str) -> Dict[str, Any]:
    """Check agent output with guardrail."""
    return apply_guardrail(response, check_input=False)

