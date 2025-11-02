"""
===============================================================================
SCRIPT NAME: verify_agentcore_resources.py
===============================================================================

PURPOSE:
    Verifies that all required AgentCore resources exist and are configured.

USAGE:
    python scripts/verify_agentcore_resources.py [--check-memory] [--check-identity] [--check-runtime]

OPTIONS:
    --check-memory: Verify Memory resource exists
    --check-identity: Verify Identity resource exists
    --check-runtime: Verify Runtime resource exists
    --all: Check all resources (default)

WHAT THIS SCRIPT DOES:
    1. Checks .env file for resource ARNs/IDs
    2. Verifies resources exist in AWS
    3. Validates resource status (ACTIVE, CREATING, etc.)
    4. Reports any missing or misconfigured resources

OUTPUTS:
    - Status report for each resource
    - List of missing resources
    - Recommendations for fixing issues

TROUBLESHOOTING:
    - Ensure .env file exists and has resource IDs
    - Verify AWS credentials have read permissions
    - Check region matches resource region

RELATED FILES:
    - scripts/list_agentcore_resources.py - List all resources
    - scripts/get_resource_status.py - Get detailed status
    - scripts/setup_agentcore_resources.py - Create missing resources

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region
import boto3
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


def verify_memory_resource(memory_id: str, region: str) -> Dict[str, Any]:
    """Verify Memory resource exists."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_memory_resource(memoryIdentifier=memory_id)
        
        return {
            'exists': True,
            'status': response.get('status', 'UNKNOWN'),
            'arn': response.get('arn'),
            'name': response.get('name')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return {'exists': False, 'error': 'Resource not found'}
        return {'exists': False, 'error': str(e)}


def verify_identity_resource(identity_name: str, region: str) -> Dict[str, Any]:
    """Verify Workload Identity resource exists."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_workload_identity(workloadIdentityName=identity_name)
        
        return {
            'exists': True,
            'status': response.get('status', 'ACTIVE'),
            'arn': response.get('workloadIdentityArn'),
            'name': response.get('name')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return {'exists': False, 'error': 'Resource not found'}
        return {'exists': False, 'error': str(e)}


def verify_runtime_resource(runtime_id: str, region: str) -> Dict[str, Any]:
    """Verify Runtime resource exists."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        response = client.get_runtime(runtimeIdentifier=runtime_id)
        
        return {
            'exists': True,
            'status': response.get('status', 'UNKNOWN'),
            'arn': response.get('runtimeArn'),
            'name': response.get('name')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return {'exists': False, 'error': 'Resource not found'}
        return {'exists': False, 'error': str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify AgentCore resources exist and are configured'
    )
    parser.add_argument(
        '--check-memory',
        action='store_true',
        help='Verify Memory resource'
    )
    parser.add_argument(
        '--check-identity',
        action='store_true',
        help='Verify Identity resource'
    )
    parser.add_argument(
        '--check-runtime',
        action='store_true',
        help='Verify Runtime resource'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='Check all resources (default)'
    )
    
    args = parser.parse_args()
    
    logger.info("🔍 Verifying AgentCore resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    region = get_aws_region()
    logger.info(f"   Region: {region}")
    
    results = {}
    issues = []
    
    # Check Memory
    check_memory = args.check_memory or (args.all and not args.check_identity and not args.check_runtime)
    if check_memory:
        memory_id = os.getenv('MEMORY_RESOURCE_ID') or os.getenv('MEMORY_RESOURCE_ARN')
        if memory_id:
            logger.info("   Checking Memory resource...")
            results['memory'] = verify_memory_resource(memory_id, region)
        else:
            logger.warning("   ⚠️  MEMORY_RESOURCE_ID not found in .env")
            results['memory'] = {'exists': False, 'error': 'Not configured in .env'}
            issues.append("Memory resource not configured in .env")
    
    # Check Identity
    check_identity = args.check_identity or (args.all and not args.check_memory and not args.check_runtime)
    if check_identity:
        identity_name = os.getenv('WORKLOAD_IDENTITY_NAME')
        if identity_name:
            logger.info("   Checking Identity resource...")
            results['identity'] = verify_identity_resource(identity_name, region)
        else:
            logger.warning("   ⚠️  WORKLOAD_IDENTITY_NAME not found in .env")
            results['identity'] = {'exists': False, 'error': 'Not configured in .env'}
            issues.append("Identity resource not configured in .env")
    
    # Check Runtime
    if args.check_runtime:
        runtime_id = os.getenv('AGENT_RUNTIME_ARN') or os.getenv('AGENT_RUNTIME_ID')
        if runtime_id:
            logger.info("   Checking Runtime resource...")
            results['runtime'] = verify_runtime_resource(runtime_id, region)
        else:
            logger.warning("   ⚠️  AGENT_RUNTIME_ARN not found in .env")
            results['runtime'] = {'exists': False, 'error': 'Not configured in .env'}
            issues.append("Runtime resource not configured in .env")
    
    # Display results
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION RESULTS")
    logger.info("="*80)
    
    all_ok = True
    for resource_type, result in results.items():
        logger.info(f"\n{resource_type.upper()}:")
        if result.get('exists'):
            logger.info(f"  ✅ Status: {result.get('status', 'UNKNOWN')}")
            logger.info(f"  ARN: {result.get('arn', 'N/A')}")
            logger.info(f"  Name: {result.get('name', 'N/A')}")
            if result.get('status') not in ['ACTIVE', 'CREATING']:
                logger.warning(f"  ⚠️  Resource status is {result.get('status')}")
                all_ok = False
        else:
            logger.error(f"  ❌ {result.get('error', 'Resource not found')}")
            all_ok = False
    
    logger.info("\n" + "="*80)
    
    if issues:
        logger.info("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            logger.info(f"  - {issue}")
        logger.info("\n💡 RECOMMENDATIONS:")
        if 'Memory' in str(issues):
            logger.info("  - Run: python scripts/create_agentcore_memory.py")
        if 'Identity' in str(issues):
            logger.info("  - Run: python scripts/create_agentcore_identity.py")
        logger.info("  - Or run: python scripts/setup_agentcore_resources.py")
    
    if all_ok and not issues:
        logger.info("✅ All checked resources are configured and accessible!")
        return 0
    else:
        logger.error("❌ Some resources are missing or misconfigured")
        return 1


if __name__ == "__main__":
    sys.exit(main())

