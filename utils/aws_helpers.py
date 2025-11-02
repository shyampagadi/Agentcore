"""
===============================================================================
MODULE: aws_helpers.py
===============================================================================

PURPOSE:
    Provides helper functions for AWS operations and credential validation.
    This module centralizes common AWS operations used across the application.

WHEN TO USE THIS MODULE:
    - Validating AWS credentials before operations
    - Getting AWS region from environment or configuration
    - Creating AWS clients with consistent configuration
    - Checking AWS account ID
    - Validating AWS service access

USAGE EXAMPLES:
    # Validate AWS credentials
    from utils.aws_helpers import validate_aws_credentials
    
    if not validate_aws_credentials():
        print("AWS credentials not configured")
        sys.exit(1)

    # Get AWS region
    from utils.aws_helpers import get_aws_region
    region = get_aws_region()  # Returns us-east-2 or from env

    # Get AWS account ID
    from utils.aws_helpers import get_aws_account_id
    account_id = get_aws_account_id()

WHAT THIS MODULE DOES:
    1. Validates AWS credentials and configuration
    2. Retrieves AWS region from environment or defaults
    3. Gets AWS account ID
    4. Creates AWS clients with consistent configuration
    5. Checks AWS service access

OUTPUTS:
    - Console: Validation results and errors
    - Return values: Configuration values and validation status

TROUBLESHOOTING:
    - "Credentials not found": Run `aws configure` or set AWS_ACCESS_KEY_ID
    - "Invalid region": Check AWS_REGION environment variable
    - "Access denied": Check IAM permissions

RELATED FILES:
    - .env - AWS_REGION, AWS_ACCOUNT_ID configuration
    - scripts/validate_environment.py - Uses this module

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
from typing import Optional, Dict, Any
from functools import lru_cache

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
from botocore.config import Config

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
try:
    from utils.logging_config import setup_logger
except ImportError:
    # Fallback if logging_config not available
    import logging
    def setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Default AWS region (can be overridden by environment variable)
DEFAULT_REGION = "us-east-2"

# Boto3 client configuration - retry settings, timeouts, etc.
BOTO3_CONFIG = Config(
    retries={
        'max_attempts': 3,  # Retry failed requests up to 3 times
        'mode': 'adaptive'  # Adaptive retry mode (adjusts based on error type)
    },
    connect_timeout=10,  # Connection timeout in seconds
    read_timeout=30  # Read timeout in seconds
)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# AWS CREDENTIAL VALIDATION
# ============================================================================

def validate_aws_credentials() -> bool:
    """
    Validate that AWS credentials are configured and working.
    
    This function checks if AWS credentials are available and valid by
    attempting to call AWS STS (Security Token Service) to get caller identity.
    This is a lightweight way to verify credentials without making expensive
    API calls.
    
    WHAT HAPPENS WHEN YOU CALL THIS:
        1. Attempts to create boto3 session with current credentials
        2. Calls STS get_caller_identity to verify credentials
        3. Returns True if successful, False if credentials invalid
    
    RETURNS:
        bool: True if credentials are valid, False otherwise
            True: Credentials configured and working
            False: Credentials missing or invalid
    
    RAISES:
        NoCredentialsError: If no credentials found (caught and returns False)
        ClientError: If credentials invalid (caught and returns False)
    
    EXAMPLE:
        >>> from utils.aws_helpers import validate_aws_credentials
        >>> if validate_aws_credentials():
        ...     print("✅ AWS credentials valid")
        ... else:
        ...     print("❌ AWS credentials invalid")
        ...     sys.exit(1)
        ✅ AWS credentials valid
    
    NOTES:
        - Checks both environment variables and AWS credentials file
        - Uses default profile if AWS_PROFILE not set
        - This is a lightweight check (doesn't verify permissions)
    """
    try:
        # Create STS client to validate credentials
        # STS (Security Token Service) is a simple service perfect for validation
        sts_client = boto3.client('sts', config=BOTO3_CONFIG)
        
        # Try to get caller identity (this validates credentials)
        response = sts_client.get_caller_identity()
        
        # Extract account ID and user/role ARN from response
        account_id = response.get('Account')
        arn = response.get('Arn')
        user_id = response.get('UserId')
        
        logger.info(f"✅ AWS credentials validated")
        logger.info(f"   Account ID: {account_id}")
        logger.info(f"   ARN: {arn}")
        logger.info(f"   User ID: {user_id}")
        
        return True
    
    except NoCredentialsError:
        logger.error("❌ AWS credentials not found")
        logger.error("   💡 SOLUTION: Run 'aws configure' or set AWS_ACCESS_KEY_ID environment variable")
        return False
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        logger.error(f"❌ AWS credentials validation failed")
        logger.error(f"   Error Code: {error_code}")
        logger.error(f"   Error Message: {error_message}")
        
        if error_code == 'InvalidClientTokenId':
            logger.error("   💡 SOLUTION: Check AWS_ACCESS_KEY_ID is correct")
        elif error_code == 'SignatureDoesNotMatch':
            logger.error("   💡 SOLUTION: Check AWS_SECRET_ACCESS_KEY is correct")
        elif error_code == 'TokenRefreshRequired':
            logger.error("   💡 SOLUTION: Refresh your AWS credentials")
        
        return False
    
    except Exception as e:
        logger.error(f"❌ Unexpected error validating credentials: {e}")
        return False


def get_aws_region() -> str:
    """
    Get AWS region from environment variable or default.
    
    Retrieves AWS region in this order:
    1. AWS_REGION environment variable
    2. AWS_DEFAULT_REGION environment variable
    3. boto3 session default region
    4. DEFAULT_REGION constant
    
    RETURNS:
        str: AWS region name (e.g., "us-east-2")
    
    EXAMPLE:
        >>> from utils.aws_helpers import get_aws_region
        >>> region = get_aws_region()
        >>> print(region)
        us-east-2
    """
    # Try environment variables first
    region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
    
    if region:
        logger.debug(f"Using AWS region from environment: {region}")
        return region
    
    # Try boto3 session default region
    try:
        session = boto3.Session()
        region = session.region_name
        if region:
            logger.debug(f"Using AWS region from boto3 session: {region}")
            return region
    except Exception:
        pass
    
    # Fall back to default
    logger.debug(f"Using default AWS region: {DEFAULT_REGION}")
    return DEFAULT_REGION


@lru_cache(maxsize=1)  # Cache result (region doesn't change during execution)
def get_aws_account_id() -> Optional[str]:
    """
    Get AWS account ID.
    
    Calls AWS STS to get the current AWS account ID. Result is cached
    for performance (account ID doesn't change during execution).
    
    RETURNS:
        Optional[str]: AWS account ID (12 digits) or None if failed
            Example: "123456789012"
            None: If credentials invalid or API call failed
    
    RAISES:
        NoCredentialsError: If AWS credentials not configured
        ClientError: If API call fails
    
    EXAMPLE:
        >>> from utils.aws_helpers import get_aws_account_id
        >>> account_id = get_aws_account_id()
        >>> print(f"Account ID: {account_id}")
        Account ID: 123456789012
    
    NOTES:
        - Result is cached (subsequent calls return cached value)
        - Requires valid AWS credentials
        - Uses STS get_caller_identity API
    """
    try:
        sts_client = boto3.client('sts', config=BOTO3_CONFIG)
        response = sts_client.get_caller_identity()
        account_id = response.get('Account')
        
        if account_id:
            logger.info(f"✅ Retrieved AWS account ID: {account_id}")
            return account_id
        else:
            logger.warning("⚠️  Account ID not found in STS response")
            return None
    
    except Exception as e:
        logger.error(f"❌ Failed to get AWS account ID: {e}")
        return None


def get_boto3_session(region: Optional[str] = None, profile: Optional[str] = None) -> boto3.Session:
    """
    Create boto3 session with specified region and profile.
    
    Creates a boto3 session with consistent configuration. Useful for
    creating AWS clients with specific settings.
    
    ARGUMENTS:
        region (Optional[str]): AWS region for session
            Default: None (uses get_aws_region())
            Example: "us-east-2"
        
        profile (Optional[str]): AWS profile name
            Default: None (uses default profile)
            Example: "dev" or "prod"
            Get from: AWS_PROFILE environment variable or parameter
    
    RETURNS:
        boto3.Session: Configured boto3 session
    
    RAISES:
        ProfileNotFound: If specified profile doesn't exist
    
    EXAMPLE:
        >>> from utils.aws_helpers import get_boto3_session
        >>> session = get_boto3_session(region="us-east-2", profile="dev")
        >>> s3_client = session.client('s3')
    """
    # Get region
    if region is None:
        region = get_aws_region()
    
    # Get profile from parameter or environment
    if profile is None:
        profile = os.getenv('AWS_PROFILE')
    
    # Create session
    if profile:
        try:
            session = boto3.Session(region_name=region, profile_name=profile)
            logger.debug(f"Created boto3 session with profile '{profile}' and region '{region}'")
        except ProfileNotFound:
            logger.error(f"❌ AWS profile '{profile}' not found")
            logger.error("   💡 SOLUTION: Check AWS_PROFILE or create profile with 'aws configure --profile <name>'")
            raise
    else:
        session = boto3.Session(region_name=region)
        logger.debug(f"Created boto3 session with region '{region}' (default profile)")
    
    return session


def create_aws_client(service_name: str, region: Optional[str] = None, **kwargs) -> Any:
    """
    Create AWS client with consistent configuration.
    
    Creates a boto3 client for an AWS service with retry configuration
    and error handling. This ensures all clients use the same settings.
    
    ARGUMENTS:
        service_name (str): AWS service name
            Examples: 's3', 'cognito-idp', 'bedrock-agentcore', 'sts'
        
        region (Optional[str]): AWS region
            Default: None (uses get_aws_region())
            Example: "us-east-2"
        
        **kwargs: Additional arguments passed to boto3.client()
            Example: endpoint_url, use_ssl, etc.
    
    RETURNS:
        Any: Boto3 client for specified service
    
    RAISES:
        NoCredentialsError: If AWS credentials not configured
        ClientError: If client creation fails
    
    EXAMPLE:
        >>> from utils.aws_helpers import create_aws_client
        >>> cognito_client = create_aws_client('cognito-idp', region='us-east-2')
        >>> response = cognito_client.list_user_pools(MaxResults=10)
    """
    if region is None:
        region = get_aws_region()
    
    try:
        client = boto3.client(service_name, region_name=region, config=BOTO3_CONFIG, **kwargs)
        logger.debug(f"Created AWS client for service: {service_name} (region: {region})")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to create AWS client for {service_name}: {e}")
        raise


def check_service_access(service_name: str, region: Optional[str] = None) -> bool:
    """
    Check if AWS service is accessible with current credentials.
    
    Attempts to make a lightweight API call to verify service access.
    This is useful for validating IAM permissions before major operations.
    
    ARGUMENTS:
        service_name (str): AWS service name to check
            Examples: 'bedrock', 'cognito-idp', 's3'
        
        region (Optional[str]): AWS region
            Default: None (uses get_aws_region())
    
    RETURNS:
        bool: True if service is accessible, False otherwise
    
    EXAMPLE:
        >>> from utils.aws_helpers import check_service_access
        >>> if check_service_access('bedrock'):
        ...     print("✅ Bedrock access verified")
        ✅ Bedrock access verified
    
    NOTES:
        - Makes lightweight API calls (list operations)
        - Returns False on any error (doesn't distinguish error types)
    """
    if region is None:
        region = get_aws_region()
    
    # Map service names to their test API calls
    # Each service has a different way to test access
    test_operations = {
        'bedrock': ('bedrock', 'list_foundation_models'),
        'cognito-idp': ('cognito-idp', 'list_user_pools'),
        's3': ('s3', 'list_buckets'),
        'sts': ('sts', 'get_caller_identity'),
        'bedrock-agentcore': ('bedrock-agentcore-control', 'list_runtimes'),
    }
    
    if service_name not in test_operations:
        logger.warning(f"⚠️  Unknown service '{service_name}', cannot test access")
        return False
    
    client_service, operation = test_operations[service_name]
    
    try:
        client = create_aws_client(client_service, region=region)
        method = getattr(client, operation)
        
        # Call with minimal parameters
        method(MaxResults=1)
        
        logger.info(f"✅ Service '{service_name}' is accessible")
        return True
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'AccessDeniedException':
            logger.error(f"❌ Access denied to service '{service_name}'")
            logger.error("   💡 SOLUTION: Check IAM permissions for this service")
        else:
            logger.error(f"❌ Cannot access service '{service_name}': {error_code}")
        
        return False
    
    except Exception as e:
        logger.error(f"❌ Error checking service '{service_name}': {e}")
        return False


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test AWS helper functions.
    
    Run this file directly to test AWS configuration:
        python utils/aws_helpers.py
    """
    print("="*70)
    print("Testing AWS Helper Functions")
    print("="*70)
    
    # Test credential validation
    print("\n1. Testing AWS Credentials Validation:")
    if validate_aws_credentials():
        print("   ✅ AWS credentials are valid")
    else:
        print("   ❌ AWS credentials are invalid")
        sys.exit(1)
    
    # Test region retrieval
    print("\n2. Testing AWS Region Retrieval:")
    region = get_aws_region()
    print(f"   Region: {region}")
    
    # Test account ID retrieval
    print("\n3. Testing AWS Account ID Retrieval:")
    account_id = get_aws_account_id()
    if account_id:
        print(f"   Account ID: {account_id}")
    else:
        print("   ❌ Failed to get account ID")
    
    # Test service access
    print("\n4. Testing Service Access:")
    services_to_test = ['sts', 'cognito-idp', 'bedrock']
    for service in services_to_test:
        if check_service_access(service):
            print(f"   ✅ {service}: Accessible")
        else:
            print(f"   ❌ {service}: Not accessible")
    
    print("\n" + "="*70)
    print("AWS Helper Functions Test Complete!")
    print("="*70)

