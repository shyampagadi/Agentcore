"""
===============================================================================
SCRIPT NAME: get_resource_status.py
===============================================================================

PURPOSE:
    Gets detailed status of a specific AgentCore resource.

USAGE:
    python scripts/get_resource_status.py --resource-type TYPE --resource-id ID

OPTIONS:
    --resource-type TYPE: Resource type (memory|identity|runtime|guardrail)
    --resource-id ID: Resource ID or ARN

WHAT THIS SCRIPT DOES:
    1. Retrieves detailed information about a specific resource
    2. Displays status, configuration, and metadata
    3. Shows resource health and availability

OUTPUTS:
    - Detailed resource information
    - Status and health metrics
    - Configuration details

TROUBLESHOOTING:
    - Ensure resource ID is correct
    - Verify AWS credentials have read permissions
    - Check region matches resource region

RELATED FILES:
    - scripts/list_agentcore_resources.py - List all resources
    - scripts/verify_agentcore_resources.py - Verify resources exist

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region
import boto3
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


def get_memory_status(memory_id: str, region: str) -> Dict:
    """Get Memory resource status."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_memory_resource(memoryIdentifier=memory_id)
        return response
    except ClientError as e:
        logger.error(f"❌ Failed to get Memory status: {e}")
        raise


def get_identity_status(identity_name: str, region: str) -> Dict:
    """Get Identity resource status."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_workload_identity(workloadIdentityName=identity_name)
        return response
    except ClientError as e:
        logger.error(f"❌ Failed to get Identity status: {e}")
        raise


def get_runtime_status(runtime_id: str, region: str) -> Dict:
    """Get Runtime resource status."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_runtime(runtimeIdentifier=runtime_id)
        return response
    except ClientError as e:
        logger.error(f"❌ Failed to get Runtime status: {e}")
        raise


def get_guardrail_status(guardrail_id: str, region: str) -> Dict:
    """Get Guardrail status."""
    try:
        client = boto3.client('bedrock', region_name=region)
        response = client.get_guardrail(guardrailIdentifier=guardrail_id)
        return response
    except ClientError as e:
        logger.error(f"❌ Failed to get Guardrail status: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Get detailed status of an AgentCore resource'
    )
    parser.add_argument(
        '--resource-type',
        required=True,
        choices=['memory', 'identity', 'runtime', 'guardrail'],
        help='Resource type'
    )
    parser.add_argument(
        '--resource-id',
        required=True,
        help='Resource ID, ARN, or name'
    )
    parser.add_argument(
        '--region',
        default=None,
        help='AWS region (default: from env or us-east-2)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    args = parser.parse_args()
    
    logger.info(f"🔍 Getting {args.resource_type} resource status...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    region = args.region or get_aws_region()
    
    try:
        if args.resource_type == 'memory':
            status = get_memory_status(args.resource_id, region)
        elif args.resource_type == 'identity':
            status = get_identity_status(args.resource_id, region)
        elif args.resource_type == 'runtime':
            status = get_runtime_status(args.resource_id, region)
        elif args.resource_type == 'guardrail':
            status = get_guardrail_status(args.resource_id, region)
        
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            logger.info("\n" + "="*80)
            logger.info(f"{args.resource_type.upper()} RESOURCE STATUS")
            logger.info("="*80)
            
            # Format and display status
            for key, value in status.items():
                if isinstance(value, dict):
                    logger.info(f"\n{key}:")
                    for sub_key, sub_value in value.items():
                        logger.info(f"  {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    logger.info(f"\n{key}:")
                    for item in value:
                        logger.info(f"  - {item}")
                else:
                    logger.info(f"{key}: {value}")
            
            logger.info("="*80)
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to get resource status: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

