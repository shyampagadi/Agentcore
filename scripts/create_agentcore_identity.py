"""
===============================================================================
SCRIPT NAME: create_agentcore_identity.py
===============================================================================

PURPOSE:
    Creates AgentCore Workload Identity resource.

USAGE:
    python scripts/create_agentcore_identity.py [--name NAME] [--description DESC]

OPTIONS:
    --name NAME: Identity name (default: cloud-engineer-agent-workload-identity)
    --description DESC: Identity description (optional)

WHAT THIS SCRIPT DOES:
    1. Creates Workload Identity using AgentCore Control Plane API
    2. Updates .env file with Identity ARN and name
    3. Validates AWS credentials
    4. Handles errors gracefully

OUTPUTS:
    - Updates .env file with WORKLOAD_IDENTITY_NAME and WORKLOAD_IDENTITY_ARN
    - Prints Identity ARN and name

TROUBLESHOOTING:
    - Ensure AWS credentials are configured
    - Verify bedrock-agentcore-control permissions
    - Check region is correct (us-east-2)

RELATED FILES:
    - identity/workload_identity_manager.py - Identity creation logic
    - scripts/setup_agentcore_resources.py - Combined setup script

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
from utils.aws_helpers import validate_aws_credentials
from identity.workload_identity_manager import create_workload_identity

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create AgentCore Workload Identity resource'
    )
    parser.add_argument(
        '--name',
        default='cloud-engineer-agent-workload-identity',
        help='Workload Identity name (default: cloud-engineer-agent-workload-identity)'
    )
    parser.add_argument(
        '--description',
        default=None,
        help='Workload Identity description (optional)'
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Creating AgentCore Workload Identity...")
    logger.info(f"   Name: {args.name}")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        logger.info("   💡 Run: aws configure")
        return 1
    
    load_dotenv()
    
    try:
        # Create workload identity
        identity_result = create_workload_identity(
            name=args.name,
            description=args.description or f"Workload identity for {args.name}"
        )
        
        # Update .env file
        set_key('.env', 'WORKLOAD_IDENTITY_NAME', identity_result['identity_name'])
        
        if identity_result.get('identity_arn'):
            # Extract ARN if not already in result
            identity_arn = identity_result['identity_arn']
            set_key('.env', 'WORKLOAD_IDENTITY_ARN', identity_arn)
        
        logger.info("✅ Workload Identity created successfully!")
        logger.info(f"   Identity Name: {identity_result['identity_name']}")
        logger.info(f"   Identity ARN: {identity_result['identity_arn']}")
        logger.info("   ✅ Updated .env file with Identity details")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to create Workload Identity: {e}")
        
        # Check for common errors
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            logger.info("   💡 Identity already exists. Use a different name or check existing identities.")
        elif 'permission' in error_msg or 'access' in error_msg:
            logger.info("   💡 Check IAM permissions for bedrock-agentcore-control:CreateWorkloadIdentity")
        elif 'region' in error_msg:
            logger.info(f"   💡 Verify region is correct (current: {os.getenv('AWS_REGION', 'us-east-2')})")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

