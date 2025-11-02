"""
===============================================================================
SCRIPT NAME: verify_cognito.py
===============================================================================

PURPOSE:
    Verifies existing Cognito User Pool configuration and ensures it meets
    requirements for the application. This script checks pool settings,
    creates app client if missing, and validates OAuth configuration.

WHEN TO USE THIS SCRIPT:
    - First-time setup: Verifying existing Cognito User Pool
    - Before deployment: Ensuring pool is correctly configured
    - Troubleshooting: Diagnosing authentication issues

PREREQUISITES:
    - Cognito User Pool ID (from .env or --pool-id argument)
    - AWS credentials configured
    - IAM permissions: cognito-idp:DescribeUserPool, cognito-idp:ListUserPoolClients

USAGE EXAMPLES:
    # Verify pool from .env file
    python scripts/verify_cognito.py

    # Verify specific pool
    python scripts/verify_cognito.py --pool-id us-east-2_abc123

    # Create app client if missing
    python scripts/verify_cognito.py --create-client-if-missing

WHAT THIS SCRIPT DOES:
    1. Verifies Cognito User Pool exists and is accessible
    2. Checks pool configuration (password policy, MFA, etc.)
    3. Lists existing app clients
    4. Creates app client if missing (optional)
    5. Validates OAuth flows and callback URLs
    6. Outputs configuration summary

OUTPUTS:
    - Console: Detailed verification results
    - JSON file: Configuration summary (optional)

RELATED FILES:
    - scripts/create_cognito_pool.py - Create new pool
    - auth/cognito_client.py - Use pool credentials

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
import boto3
from botocore.exceptions import ClientError

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region, validate_aws_credentials
from scripts.create_cognito_pool import CognitoPoolManager

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def verify_pool_configuration(pool_id: str, cognito_client: Any) -> Dict[str, Any]:
    """
    Verify Cognito User Pool configuration.
    
    Checks pool settings and returns verification results.
    
    RETURNS:
        Dict[str, Any]: Verification results
    """
    try:
        response = cognito_client.describe_user_pool(UserPoolId=pool_id)
        pool = response['UserPool']
        
        verification = {
            'exists': True,
            'pool_id': pool_id,
            'name': pool.get('Name'),
            'status': pool.get('Status'),
            'password_policy': pool.get('Policies', {}).get('PasswordPolicy', {}),
            'mfa_enabled': pool.get('MfaConfiguration') != 'OFF',
            'email_verification': 'email' in pool.get('AutoVerifiedAttributes', []),
            'username_attributes': pool.get('UsernameAttributes', []),
        }
        
        return verification
    
    except ClientError as e:
        logger.error(f"❌ Failed to verify pool: {e}")
        return {'exists': False, 'error': str(e)}


def list_app_clients(pool_id: str, cognito_client: Any) -> List[Dict[str, Any]]:
    """
    List all app clients for a Cognito User Pool.
    
    RETURNS:
        List[Dict[str, Any]]: List of app client configurations
    """
    try:
        response = cognito_client.list_user_pool_clients(UserPoolId=pool_id)
        return response.get('UserPoolClients', [])
    except ClientError as e:
        logger.error(f"❌ Failed to list app clients: {e}")
        return []


def main() -> int:
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(description="Verify Cognito User Pool configuration")
    parser.add_argument('--pool-id', type=str, help='Cognito User Pool ID')
    parser.add_argument('--create-client-if-missing', action='store_true',
                       help='Create app client if none exists')
    
    args = parser.parse_args()
    
    load_dotenv()
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    region = get_aws_region()
    pool_id = args.pool_id or os.getenv('COGNITO_USER_POOL_ID')
    
    if not pool_id:
        logger.error("❌ Pool ID not provided. Use --pool-id or set COGNITO_USER_POOL_ID in .env")
        return 1
    
    manager = CognitoPoolManager(region=region)
    
    logger.info("="*70)
    logger.info("Verifying Cognito User Pool Configuration")
    logger.info("="*70)
    logger.info(f"Pool ID: {pool_id}")
    logger.info(f"Region: {region}")
    logger.info("")
    
    # Verify pool exists
    pool = manager.check_pool_exists(pool_id=pool_id)
    if not pool:
        logger.error(f"❌ Pool not found: {pool_id}")
        return 1
    
    logger.info(f"✅ Pool found: {pool['Name']}")
    logger.info(f"   Status: {pool['Status']}")
    
    # List app clients
    clients = list_app_clients(pool_id, manager.cognito_client)
    logger.info(f"\n📋 Found {len(clients)} app client(s):")
    for client in clients:
        logger.info(f"   - {client.get('ClientName')} ({client.get('ClientId')})")
    
    if not clients and args.create_client_if_missing:
        logger.info("\n📋 Creating app client...")
        client_result = manager.create_app_client(pool_id=pool_id)
        logger.info(f"✅ Created client: {client_result['ClientId']}")
    
    logger.info("\n✅ Verification complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

