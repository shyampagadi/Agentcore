"""
===============================================================================
MODULE: workload_identity_manager.py
===============================================================================

PURPOSE:
    Manages workload identity for AgentCore Runtime.

WHEN TO USE THIS MODULE:
    - Runtime setup: Configure workload identity
    - Identity management: Manage workload identities

USAGE EXAMPLES:
    from identity.workload_identity_manager import create_workload_identity
    
    identity = create_workload_identity(name="agent-runtime-identity")

WHAT THIS MODULE DOES:
    1. Creates workload identities
    2. Configures identity policies
    3. Manages identity lifecycle

RELATED FILES:
    - scripts/setup_agentcore_resources.py - Setup script

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

logger = setup_logger(__name__)


def create_workload_identity(
    name: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create workload identity.
    
    ARGUMENTS:
        name (str): Identity name
        description (Optional[str]): Description
    
    RETURNS:
        Dict[str, Any]: Identity creation result
    """
    region = get_aws_region()
    client = boto3.client('bedrock-agentcore-control', region_name=region)
    
    try:
        response = client.create_workload_identity(
            name=name,
            description=description or f'Workload identity for {name}'
        )
        
        identity_arn = response['workloadIdentityArn']
        logger.info(f"✅ Workload identity created: {identity_arn}")
        
        return {
            'identity_arn': identity_arn,
            'identity_name': name
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ Failed to create workload identity: {error_code}")
        raise
