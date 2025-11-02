"""
===============================================================================
SCRIPT NAME: list_agentcore_resources.py
===============================================================================

PURPOSE:
    Lists all AgentCore resources (Memory, Identity, Runtime).

USAGE:
    python scripts/list_agentcore_resources.py [--resource-type TYPE] [--region REGION]

OPTIONS:
    --resource-type TYPE: Filter by resource type (memory|identity|runtime|all)
    --region REGION: AWS region (default: from env or us-east-2)

WHAT THIS SCRIPT DOES:
    1. Lists all Memory resources
    2. Lists all Workload Identity resources
    3. Lists all Runtime resources (if available)
    4. Displays resource details (ARN, ID, status, creation date)

OUTPUTS:
    - Table of all resources with details
    - Summary count by resource type

TROUBLESHOOTING:
    - Ensure AWS credentials are configured
    - Verify bedrock-agentcore-control permissions
    - Check region is correct

RELATED FILES:
    - scripts/verify_agentcore_resources.py - Verify resources exist
    - scripts/get_resource_status.py - Get detailed status

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region
import boto3
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


def list_memory_resources(region: str) -> List[Dict[str, Any]]:
    """List all Memory resources."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.list_memory_resources()
        
        resources = []
        for memory in response.get('memoryResources', []):
            resources.append({
                'type': 'Memory',
                'id': memory.get('memoryId') or memory.get('id'),
                'arn': memory.get('arn'),
                'name': memory.get('name'),
                'status': memory.get('status', 'UNKNOWN'),
                'created': memory.get('createdAt')
            })
        return resources
    except ClientError as e:
        logger.warning(f"⚠️  Could not list Memory resources: {e}")
        return []


def list_identity_resources(region: str) -> List[Dict[str, Any]]:
    """List all Workload Identity resources."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.list_workload_identities()
        
        resources = []
        for identity in response.get('workloadIdentities', []):
            resources.append({
                'type': 'Identity',
                'id': identity.get('workloadIdentityId') or identity.get('id'),
                'arn': identity.get('workloadIdentityArn') or identity.get('arn'),
                'name': identity.get('name'),
                'status': identity.get('status', 'ACTIVE'),
                'created': identity.get('createdAt')
            })
        return resources
    except ClientError as e:
        logger.warning(f"⚠️  Could not list Identity resources: {e}")
        return []


def list_runtime_resources(region: str) -> List[Dict[str, Any]]:
    """List all Runtime resources."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.list_runtimes()
        
        resources = []
        for runtime in response.get('runtimes', []):
            resources.append({
                'type': 'Runtime',
                'id': runtime.get('runtimeId') or runtime.get('id'),
                'arn': runtime.get('runtimeArn') or runtime.get('arn'),
                'name': runtime.get('name'),
                'status': runtime.get('status', 'UNKNOWN'),
                'created': runtime.get('createdAt')
            })
        return resources
    except ClientError as e:
        logger.warning(f"⚠️  Could not list Runtime resources: {e}")
        return []


def format_date(date_str: Any) -> str:
    """Format date string."""
    if not date_str:
        return 'N/A'
    try:
        if isinstance(date_str, (int, float)):
            dt = datetime.fromtimestamp(date_str)
        else:
            dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(date_str)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='List all AgentCore resources'
    )
    parser.add_argument(
        '--resource-type',
        choices=['memory', 'identity', 'runtime', 'all'],
        default='all',
        help='Filter by resource type (default: all)'
    )
    parser.add_argument(
        '--region',
        default=None,
        help='AWS region (default: from env or us-east-2)'
    )
    
    args = parser.parse_args()
    
    logger.info("📋 Listing AgentCore resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    region = args.region or get_aws_region()
    logger.info(f"   Region: {region}")
    
    all_resources = []
    
    # List resources based on filter
    if args.resource_type in ['memory', 'all']:
        logger.info("   Fetching Memory resources...")
        all_resources.extend(list_memory_resources(region))
    
    if args.resource_type in ['identity', 'all']:
        logger.info("   Fetching Identity resources...")
        all_resources.extend(list_identity_resources(region))
    
    if args.resource_type in ['runtime', 'all']:
        logger.info("   Fetching Runtime resources...")
        all_resources.extend(list_runtime_resources(region))
    
    # Display results
    if not all_resources:
        logger.info("   No resources found.")
        return 0
    
    logger.info("\n" + "="*80)
    logger.info("AGENTCORE RESOURCES")
    logger.info("="*80)
    
    # Group by type
    by_type = {}
    for resource in all_resources:
        rtype = resource['type']
        if rtype not in by_type:
            by_type[rtype] = []
        by_type[rtype].append(resource)
    
    # Display each type
    for rtype in ['Memory', 'Identity', 'Runtime']:
        if rtype in by_type:
            logger.info(f"\n{rtype} Resources ({len(by_type[rtype])}):")
            logger.info("-" * 80)
            for resource in by_type[rtype]:
                logger.info(f"  Name: {resource.get('name', 'N/A')}")
                logger.info(f"  ID:   {resource.get('id', 'N/A')}")
                logger.info(f"  ARN:  {resource.get('arn', 'N/A')}")
                logger.info(f"  Status: {resource.get('status', 'N/A')}")
                logger.info(f"  Created: {format_date(resource.get('created'))}")
                logger.info("")
    
    # Summary
    logger.info("="*80)
    logger.info("SUMMARY:")
    for rtype in ['Memory', 'Identity', 'Runtime']:
        count = len(by_type.get(rtype, []))
        logger.info(f"  {rtype}: {count}")
    logger.info("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

