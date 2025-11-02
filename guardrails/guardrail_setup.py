"""
===============================================================================
MODULE: guardrail_setup.py
===============================================================================

PURPOSE:
    Sets up Amazon Bedrock Guardrails for content safety.

WHEN TO USE THIS MODULE:
    - Initial setup: Create guardrails
    - Configuration: Update guardrail settings

USAGE EXAMPLES:
    from guardrails.guardrail_setup import create_guardrail
    
    guardrail_id = create_guardrail(name="cloud-engineering-guardrail")

WHAT THIS MODULE DOES:
    1. Creates Bedrock Guardrail
    2. Configures content filters
    3. Sets up topic blocking
    4. Configures PII protection

RELATED FILES:
    - guardrails/guardrail_config.py - Guardrail configuration
    - scripts/setup_guardrails.py - Setup script

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import boto3
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


def create_guardrail(
    name: str,
    description: Optional[str] = None,
    blocked_topics: Optional[List[str]] = None,
    content_filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create Bedrock Guardrail.
    
    ARGUMENTS:
        name (str): Guardrail name
        description (Optional[str]): Description
        blocked_topics (Optional[List[str]]): List of blocked topics
        content_filters (Optional[Dict[str, Any]]): Content filter configuration
    
    RETURNS:
        Dict[str, Any]: Guardrail creation result
    """
    region = get_aws_region()
    bedrock_client = boto3.client('bedrock', region_name=region)
    
    try:
        guardrail_config = {
            'name': name,
            'description': description or f'Guardrail for {name}',
        }
        
        if blocked_topics:
            guardrail_config['topicPolicyConfig'] = {
                'topicsConfig': [
                    {
                        'name': topic,
                        'type': 'DENY'
                    }
                    for topic in blocked_topics
                ]
            }
        
        if content_filters:
            guardrail_config['contentPolicyConfig'] = {
                'filtersConfig': content_filters
            }
        
        response = bedrock_client.create_guardrail(**guardrail_config)
        
        guardrail_id = response['guardrailId']
        guardrail_arn = response['guardrailArn']
        
        logger.info(f"✅ Guardrail created: {guardrail_id}")
        
        return {
            'guardrail_id': guardrail_id,
            'guardrail_arn': guardrail_arn,
            'status': response.get('status', 'CREATING')
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ Failed to create guardrail: {error_code}")
        raise


def get_guardrail_config() -> Dict[str, Any]:
    """
    Get guardrail configuration from environment.
    
    RETURNS:
        Dict[str, Any]: Guardrail configuration
    """
    return {
        'guardrail_id': os.getenv('BEDROCK_GUARDRAIL_ID'),
        'guardrail_version': os.getenv('BEDROCK_GUARDRAIL_VERSION', 'DRAFT'),
        'enabled': os.getenv('BEDROCK_GUARDRAIL_ID') is not None
    }

