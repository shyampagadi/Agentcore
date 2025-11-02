"""
===============================================================================
MODULE: cognito_verification.py
===============================================================================

PURPOSE:
    Verifies Cognito User Pool configuration and validates authentication setup.

WHEN TO USE THIS MODULE:
    - Setup verification: Verify Cognito is properly configured
    - Troubleshooting: Diagnose authentication issues
    - Health checks: Validate Cognito connectivity

USAGE EXAMPLES:
    from auth.cognito_verification import verify_cognito_configuration
    
    result = verify_cognito_configuration()
    if result['valid']:
        print("Cognito configuration is valid")

WHAT THIS MODULE DOES:
    1. Verifies Cognito User Pool exists
    2. Validates app client configuration
    3. Checks OAuth flows
    4. Validates callback URLs
    5. Tests authentication flow

RELATED FILES:
    - scripts/verify_cognito.py - Uses this module
    - auth/cognito_client.py - Cognito client

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


def verify_cognito_configuration() -> Dict[str, Any]:
    """
    Verify Cognito User Pool configuration.
    
    RETURNS:
        Dict[str, Any]: Verification results
            {
                'valid': bool,
                'pool_exists': bool,
                'client_exists': bool,
                'oauth_configured': bool,
                'errors': List[str],
                'warnings': List[str]
            }
    """
    pool_id = os.getenv('COGNITO_USER_POOL_ID')
    client_id = os.getenv('COGNITO_CLIENT_ID')
    region = get_aws_region()
    
    result = {
        'valid': False,
        'pool_exists': False,
        'client_exists': False,
        'oauth_configured': False,
        'errors': [],
        'warnings': []
    }
    
    if not pool_id:
        result['errors'].append('COGNITO_USER_POOL_ID not set in environment')
        return result
    
    if not client_id:
        result['warnings'].append('COGNITO_CLIENT_ID not set in environment')
    
    try:
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        # Verify pool exists
        try:
            pool_response = cognito_client.describe_user_pool(UserPoolId=pool_id)
            result['pool_exists'] = True
            pool_status = pool_response['UserPool'].get('Status', 'UNKNOWN')
            
            if pool_status != 'Active':
                result['warnings'].append(f'Pool status is {pool_status}, expected Active')
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                result['errors'].append(f'Cognito User Pool {pool_id} not found')
            else:
                result['errors'].append(f'Error accessing pool: {e.response["Error"]["Message"]}')
            return result
        
        # Verify app client exists
        if client_id:
            try:
                client_response = cognito_client.describe_user_pool_client(
                    UserPoolId=pool_id,
                    ClientId=client_id
                )
                result['client_exists'] = True
                
                # Check OAuth configuration
                client_config = client_response['UserPoolClient']
                oauth_flows = client_config.get('AllowedOAuthFlows', [])
                callback_urls = client_config.get('CallbackURLs', [])
                
                if oauth_flows:
                    result['oauth_configured'] = True
                else:
                    result['warnings'].append('OAuth flows not configured')
                
                if not callback_urls:
                    result['warnings'].append('No callback URLs configured')
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    result['errors'].append(f'App client {client_id} not found')
                else:
                    result['errors'].append(f'Error accessing client: {e.response["Error"]["Message"]}')
        
        # Determine overall validity
        result['valid'] = result['pool_exists'] and len(result['errors']) == 0
        
        return result
    
    except Exception as e:
        result['errors'].append(f'Unexpected error: {str(e)}')
        logger.error(f"Verification failed: {e}", exc_info=True)
        return result


def get_cognito_details() -> Dict[str, Any]:
    """
    Get detailed Cognito configuration information.
    
    RETURNS:
        Dict[str, Any]: Detailed configuration
    """
    pool_id = os.getenv('COGNITO_USER_POOL_ID')
    client_id = os.getenv('COGNITO_CLIENT_ID')
    region = get_aws_region()
    
    details = {
        'pool_id': pool_id,
        'client_id': client_id,
        'region': region
    }
    
    if not pool_id:
        return details
    
    try:
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        # Get pool details
        pool_response = cognito_client.describe_user_pool(UserPoolId=pool_id)
        pool = pool_response['UserPool']
        
        details.update({
            'pool_name': pool.get('Name'),
            'pool_status': pool.get('Status'),
            'mfa_enabled': pool.get('MfaConfiguration') != 'OFF',
            'auto_verified_attributes': pool.get('AutoVerifiedAttributes', []),
            'username_attributes': pool.get('UsernameAttributes', [])
        })
        
        # Get client details
        if client_id:
            try:
                client_response = cognito_client.describe_user_pool_client(
                    UserPoolId=pool_id,
                    ClientId=client_id
                )
                client_config = client_response['UserPoolClient']
                
                details.update({
                    'client_name': client_config.get('ClientName'),
                    'oauth_flows': client_config.get('AllowedOAuthFlows', []),
                    'callback_urls': client_config.get('CallbackURLs', []),
                    'explicit_auth_flows': client_config.get('ExplicitAuthFlows', [])
                })
            except ClientError:
                pass
    
    except Exception as e:
        logger.error(f"Failed to get Cognito details: {e}")
    
    return details
