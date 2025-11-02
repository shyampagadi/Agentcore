"""
===============================================================================
SCRIPT NAME: cleanup_resources.py
===============================================================================

PURPOSE:
    Cleans up/destroys AgentCore resources and related AWS resources.

USAGE:
    python scripts/cleanup_resources.py [--resource-type TYPE] [--dry-run] [--force]

OPTIONS:
    --resource-type TYPE: Resource type to cleanup (memory|identity|runtime|guardrail|all)
    --dry-run: Show what would be deleted without actually deleting
    --force: Skip confirmation prompts

WHAT THIS SCRIPT DOES:
    1. Lists resources to be deleted
    2. Prompts for confirmation (unless --force)
    3. Deletes resources in safe order
    4. Updates .env file to remove deleted resource IDs

OUTPUTS:
    - List of resources to be deleted
    - Confirmation prompt
    - Deletion progress
    - Updated .env file

TROUBLESHOOTING:
    - Use --dry-run first to preview deletions
    - Ensure you have delete permissions
    - Check dependencies before deleting (e.g., don't delete Memory if Runtime uses it)

RELATED FILES:
    - scripts/rollback.py - Rollback deployment
    - scripts/list_agentcore_resources.py - List resources before cleanup

WARNING:
    This script permanently deletes resources. Use with caution!

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv, set_key

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region
import boto3
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


def delete_memory_resource(memory_id: str, region: str) -> bool:
    """Delete Memory resource."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_memory_resource(memoryIdentifier=memory_id)
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to delete Memory: {e}")
        return False


def delete_identity_resource(identity_name: str, region: str) -> bool:
    """Delete Workload Identity resource."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_workload_identity(workloadIdentityName=identity_name)
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to delete Identity: {e}")
        return False


def delete_runtime_resource(runtime_id: str, region: str) -> bool:
    """Delete Runtime resource."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_runtime(runtimeIdentifier=runtime_id)
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to delete Runtime: {e}")
        return False


def delete_guardrail_resource(guardrail_id: str, region: str) -> bool:
    """Delete Guardrail resource."""
    try:
        client = boto3.client('bedrock', region_name=region)
        client.delete_guardrail(guardrailIdentifier=guardrail_id)
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to delete Guardrail: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Clean up AgentCore resources',
        epilog='⚠️  WARNING: This permanently deletes resources. Use with caution!'
    )
    parser.add_argument(
        '--resource-type',
        choices=['memory', 'identity', 'runtime', 'guardrail', 'all'],
        default='all',
        help='Resource type to cleanup (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    parser.add_argument(
        '--region',
        default=None,
        help='AWS region (default: from env or us-east-2)'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No resources will be deleted")
    else:
        logger.warning("⚠️  WARNING: This will permanently delete resources!")
    
    logger.info("🧹 Cleaning up AgentCore resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    region = args.region or get_aws_region()
    
    resources_to_delete = []
    
    # Collect resources to delete
    if args.resource_type in ['memory', 'all']:
        memory_id = os.getenv('MEMORY_RESOURCE_ID') or os.getenv('MEMORY_RESOURCE_ARN')
        if memory_id:
            resources_to_delete.append(('memory', memory_id, 'Memory'))
    
    if args.resource_type in ['identity', 'all']:
        identity_name = os.getenv('WORKLOAD_IDENTITY_NAME')
        if identity_name:
            resources_to_delete.append(('identity', identity_name, 'Identity'))
    
    if args.resource_type in ['runtime', 'all']:
        runtime_id = os.getenv('AGENT_RUNTIME_ARN') or os.getenv('AGENT_RUNTIME_ID')
        if runtime_id:
            resources_to_delete.append(('runtime', runtime_id, 'Runtime'))
    
    if args.resource_type in ['guardrail', 'all']:
        guardrail_id = os.getenv('BEDROCK_GUARDRAIL_ID')
        if guardrail_id:
            resources_to_delete.append(('guardrail', guardrail_id, 'Guardrail'))
    
    if not resources_to_delete:
        logger.info("   No resources found to delete.")
        return 0
    
    # Display resources to delete
    logger.info("\n" + "="*80)
    logger.info("RESOURCES TO DELETE:")
    logger.info("="*80)
    for rtype, rid, rname in resources_to_delete:
        logger.info(f"  {rname}: {rid}")
    logger.info("="*80)
    
    if args.dry_run:
        logger.info("\n✅ DRY RUN complete. No resources deleted.")
        logger.info("   Remove --dry-run flag to actually delete resources.")
        return 0
    
    # Confirm deletion
    if not args.force:
        logger.warning("\n⚠️  Are you sure you want to delete these resources?")
        response = input("Type 'DELETE' to confirm: ")
        if response != 'DELETE':
            logger.info("   Deletion cancelled.")
            return 0
    
    # Delete resources in safe order (Runtime -> Memory -> Identity -> Guardrail)
    order = ['runtime', 'memory', 'identity', 'guardrail']
    ordered_resources = sorted(resources_to_delete, key=lambda x: order.index(x[0]) if x[0] in order else 99)
    
    logger.info("\n🗑️  Deleting resources...")
    deleted = []
    failed = []
    
    for rtype, rid, rname in ordered_resources:
        logger.info(f"\n   Deleting {rname} ({rid})...")
        
        if rtype == 'memory':
            success = delete_memory_resource(rid, region)
        elif rtype == 'identity':
            success = delete_identity_resource(rid, region)
        elif rtype == 'runtime':
            success = delete_runtime_resource(rid, region)
        elif rtype == 'guardrail':
            success = delete_guardrail_resource(rid, region)
        else:
            success = False
        
        if success:
            logger.info(f"   ✅ {rname} deleted successfully")
            deleted.append((rtype, rname))
            
            # Update .env file
            if rtype == 'memory':
                set_key('.env', 'MEMORY_RESOURCE_ARN', '', quote_mode='never')
                set_key('.env', 'MEMORY_RESOURCE_ID', '', quote_mode='never')
            elif rtype == 'identity':
                set_key('.env', 'WORKLOAD_IDENTITY_NAME', '', quote_mode='never')
                set_key('.env', 'WORKLOAD_IDENTITY_ARN', '', quote_mode='never')
            elif rtype == 'runtime':
                set_key('.env', 'AGENT_RUNTIME_ARN', '', quote_mode='never')
                set_key('.env', 'AGENT_RUNTIME_ID', '', quote_mode='never')
            elif rtype == 'guardrail':
                set_key('.env', 'BEDROCK_GUARDRAIL_ID', '', quote_mode='never')
                set_key('.env', 'BEDROCK_GUARDRAIL_VERSION', '', quote_mode='never')
        else:
            logger.error(f"   ❌ Failed to delete {rname}")
            failed.append((rtype, rname))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("CLEANUP SUMMARY")
    logger.info("="*80)
    logger.info(f"   Deleted: {len(deleted)}")
    logger.info(f"   Failed: {len(failed)}")
    
    if deleted:
        logger.info("\n   Successfully deleted:")
        for rtype, rname in deleted:
            logger.info(f"     ✅ {rname}")
    
    if failed:
        logger.info("\n   Failed to delete:")
        for rtype, rname in failed:
            logger.info(f"     ❌ {rname}")
    
    logger.info("="*80)
    
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

