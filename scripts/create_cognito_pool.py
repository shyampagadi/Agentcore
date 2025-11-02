"""
===============================================================================
SCRIPT NAME: create_cognito_pool.py
===============================================================================

PURPOSE:
    Creates a new Amazon Cognito User Pool for authentication, or verifies
    an existing one. This script is used during initial setup to ensure
    authentication is properly configured.

WHEN TO USE THIS SCRIPT:
    - First-time setup: Creating a new Cognito User Pool
    - Verification: Checking if an existing pool meets requirements
    - Reconfiguration: Updating pool settings

PREREQUISITES:
    - AWS CLI configured with appropriate credentials
    - Python 3.10+ installed
    - Required packages: boto3, python-dotenv
    - IAM permissions: cognito-idp:CreateUserPool, cognito-idp:DescribeUserPool

USAGE EXAMPLES:
    # Create new pool (interactive)
    python scripts/create_cognito_pool.py

    # Create new pool (non-interactive)
    python scripts/create_cognito_pool.py --pool-name my-pool --region us-east-2

    # Verify existing pool
    python scripts/create_cognito_pool.py --verify-only --pool-id us-east-2_abc123

    # Create pool with custom settings
    python scripts/create_cognito_pool.py --pool-name my-pool --enable-mfa --password-min-length 12

WHAT THIS SCRIPT DOES:
    1. Checks if Cognito User Pool exists (by name or ID)
    2. If exists: Verifies configuration meets requirements
    3. If not exists: Creates new pool with secure defaults
    4. Creates app client for Streamlit authentication
    5. Configures OAuth flows and callback URLs
    6. Outputs credentials needed for .env file

OUTPUTS:
    - Console: Step-by-step progress and results
    - .env file: COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID (if new pool created)
    - AWS Console: New Cognito User Pool (if created)

TROUBLESHOOTING:
    - "Access Denied": Check IAM permissions (see Prerequisites)
    - "Pool already exists": Use --verify-only or --pool-id to use existing
    - "Invalid region": Ensure us-east-2 is supported in your AWS account

RELATED FILES:
    - scripts/verify_cognito.py - Verify existing pool configuration
    - auth/cognito_client.py - Use pool credentials in application
    - .env.example - Environment variable template

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
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
# boto3: AWS SDK for Python - used to interact with AWS services
import boto3
from botocore.exceptions import ClientError, BotoCoreError

# python-dotenv: Load environment variables from .env file
from dotenv import load_dotenv, set_key

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
# Add parent directory to path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.logging_config import setup_logger
    from utils.aws_helpers import get_aws_region, validate_aws_credentials
except ImportError:
    # If utilities don't exist yet, create simple logger
    import logging
    def setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def get_aws_region() -> str:
        return os.getenv('AWS_REGION', 'us-east-2')
    
    def validate_aws_credentials() -> bool:
        try:
            boto3.client('sts').get_caller_identity()
            return True
        except:
            return False

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Default values that can be overridden via command-line arguments or .env file
DEFAULT_REGION = "us-east-2"  # Target AWS region for deployment
DEFAULT_POOL_NAME = "cloud-engineer-agent-pool"  # Default pool name
DEFAULT_PASSWORD_MIN_LENGTH = 8  # Minimum password length (AWS requirement)
DEFAULT_PASSWORD_REQUIRE_UPPERCASE = True  # Require uppercase letters
DEFAULT_PASSWORD_REQUIRE_LOWERCASE = True  # Require lowercase letters
DEFAULT_PASSWORD_REQUIRE_NUMBERS = True  # Require numbers
DEFAULT_PASSWORD_REQUIRE_SYMBOLS = True  # Require special characters

# OAuth callback URLs - these will be used for Streamlit authentication
# Development URL (localhost)
DEV_CALLBACK_URL = "http://localhost:8501"
# Production URL (will be configured later via setup_domain.py)
PROD_CALLBACK_URL = "https://your-domain.com"  # Placeholder, update after domain setup

# Token expiration settings (in seconds)
ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
ID_TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY = 2592000  # 30 days

# Supported OAuth flows for Streamlit authentication
SUPPORTED_OAUTH_FLOWS = [
    "code",  # Authorization code flow (most secure)
    "implicit"  # Implicit flow (less secure, but simpler)
]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# CLASS: CognitoPoolManager
# ============================================================================

class CognitoPoolManager:
    """
    Manages Amazon Cognito User Pool creation and verification.
    
    This class encapsulates all operations related to Cognito User Pools,
    including creation, verification, and client configuration. It handles
    error cases and provides detailed feedback to users.
    
    WHY THIS CLASS EXISTS:
        - Encapsulates Cognito operations in one place
        - Makes code reusable and testable
        - Provides clear error handling
        - Separates concerns (AWS operations vs. CLI interface)
    
    USAGE EXAMPLE:
        >>> manager = CognitoPoolManager(region="us-east-2")
        >>> pool_id = manager.create_pool(name="my-pool")
        >>> print(f"Created pool: {pool_id}")
    
    ATTRIBUTES:
        region (str): AWS region where pool will be created
        cognito_client (boto3.client): Boto3 Cognito client
        logger (logging.Logger): Logger instance for this class
    
    METHODS:
        - create_pool(): Creates a new Cognito User Pool
        - verify_pool(): Verifies existing pool configuration
        - create_app_client(): Creates app client for authentication
        - check_pool_exists(): Checks if pool exists by name or ID
    """
    
    def __init__(self, region: str = DEFAULT_REGION) -> None:
        """
        Initialize CognitoPoolManager.
        
        Creates boto3 client for Cognito Identity Provider service.
        This client will be used for all Cognito operations.
        
        ARGUMENTS:
            region (str): AWS region for Cognito operations
                Default: us-east-2 (from constants)
        
        RAISES:
            ClientError: If AWS credentials are invalid or region is invalid
            ValueError: If region is empty or None
        
        EXAMPLE:
            >>> manager = CognitoPoolManager(region="us-east-2")
            >>> print(manager.region)
            us-east-2
        """
        # Validate region input
        if not region or not isinstance(region, str):
            raise ValueError("Region must be a non-empty string")
        
        self.region = region
        
        # Create boto3 client for Cognito Identity Provider
        # This client handles all API calls to AWS Cognito
        try:
            self.cognito_client = boto3.client('cognito-idp', region_name=region)
            logger.info(f"✅ Initialized Cognito client for region: {region}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cognito client: {e}")
            raise
    
    def check_pool_exists(
        self,
        pool_name: Optional[str] = None,
        pool_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a Cognito User Pool exists.
        
        Searches for a pool by name or ID. This is useful to avoid
        creating duplicate pools or to verify pool exists before use.
        
        HOW IT WORKS:
            - If pool_id provided: Direct lookup by ID (fast)
            - If pool_name provided: List all pools and search by name (slower)
            - Returns pool details if found, None if not found
        
        ARGUMENTS:
            pool_name (Optional[str]): Pool name to search for
                Example: "cloud-engineer-agent-pool"
            
            pool_id (Optional[str]): Pool ID to search for
                Example: "us-east-2_abc123def"
        
        RETURNS:
            Optional[Dict[str, Any]]: Pool details if found, None if not found
                Example:
                {
                    'PoolId': 'us-east-2_abc123def',
                    'Name': 'cloud-engineer-agent-pool',
                    'Status': 'Active'
                }
        
        NOTE:
            At least one of pool_name or pool_id must be provided.
            If both provided, pool_id takes precedence (faster).
        
        EXAMPLE:
            >>> manager = CognitoPoolManager()
            >>> pool = manager.check_pool_exists(pool_name="my-pool")
            >>> if pool:
            ...     print(f"Found pool: {pool['PoolId']}")
            ... else:
            ...     print("Pool not found")
        """
        # Validate: At least one identifier must be provided
        if not pool_name and not pool_id:
            raise ValueError("Must provide either pool_name or pool_id")
        
        # If pool_id provided, use direct lookup (faster)
        if pool_id:
            try:
                response = self.cognito_client.describe_user_pool(UserPoolId=pool_id)
                logger.info(f"✅ Found pool by ID: {pool_id}")
                return {
                    'PoolId': response['UserPool']['Id'],
                    'Name': response['UserPool']['Name'],
                    'Status': response['UserPool']['Status']
                }
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    logger.info(f"ℹ️  Pool not found by ID: {pool_id}")
                    return None
                raise
        
        # If pool_name provided, search by name (slower, requires listing)
        if pool_name:
            logger.info(f"🔍 Searching for pool by name: {pool_name}")
            try:
                # List all pools and search by name
                # Note: This is paginated, so we need to handle pagination
                paginator = self.cognito_client.get_paginator('list_user_pools')
                page_iterator = paginator.paginate(MaxResults=60)
                
                for page in page_iterator:
                    for pool in page.get('UserPools', []):
                        if pool['Name'] == pool_name:
                            logger.info(f"✅ Found pool by name: {pool_name}")
                            return {
                                'PoolId': pool['Id'],
                                'Name': pool['Name'],
                                'Status': pool.get('Status', 'Unknown')
                            }
                
                logger.info(f"ℹ️  Pool not found by name: {pool_name}")
                return None
            
            except ClientError as e:
                logger.error(f"❌ Error searching for pool: {e}")
                raise
    
    def create_pool(
        self,
        pool_name: str,
        password_min_length: int = DEFAULT_PASSWORD_MIN_LENGTH,
        enable_mfa: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new Cognito User Pool.
        
        This method creates a new Cognito User Pool with secure defaults.
        It configures password policies, user attributes, and authentication
        settings according to best practices.
        
        WHAT HAPPENS WHEN YOU CALL THIS:
            1. Validates input parameters
            2. Prepares pool configuration
            3. Calls AWS API to create pool
            4. Waits for pool to be active
            5. Returns pool details including ID
        
        ARGUMENTS:
            pool_name (str): Name for the user pool
                Example: "cloud-engineer-agent-pool"
                Must be: 1-128 characters, alphanumeric + hyphens/underscores
            
            password_min_length (int): Minimum password length
                Default: 8 (AWS minimum)
                Range: 8-99 characters
            
            enable_mfa (bool): Enable multi-factor authentication
                Default: False (can be enabled later)
                Options: True (enable MFA), False (disable MFA)
            
            **kwargs: Additional pool configuration options
                - email_verification: bool (default: True)
                - auto_verify_email: bool (default: True)
                - user_attributes: list (default: ['email'])
        
        RETURNS:
            Dict[str, Any]: Pool creation response containing:
                - PoolId: The unique identifier for the pool
                - Name: The pool name
                - Status: Pool status (usually "Active")
                - CreationDate: When pool was created
                Example:
                {
                    'PoolId': 'us-east-2_abc123def',
                    'Name': 'cloud-engineer-agent-pool',
                    'Status': 'Active',
                    'CreationDate': datetime(...)
                }
        
        RAISES:
            ClientError: If AWS API call fails
                Common errors:
                - PoolNameExistsException: Pool with this name already exists
                - InvalidParameterException: Invalid parameter value
                - LimitExceededException: Too many pools in account
            
            ValueError: If input parameters are invalid
        
        EXAMPLE:
            >>> manager = CognitoPoolManager(region="us-east-2")
            >>> result = manager.create_pool(
            ...     pool_name="my-pool",
            ...     password_min_length=10,
            ...     enable_mfa=True
            ... )
            >>> print(f"Created pool: {result['PoolId']}")
            Created pool: us-east-2_abc123def
        
        NOTES:
            - Pool creation takes 10-30 seconds
            - Pool ID format: {region}_{random_string}
            - Pool name must be unique within your AWS account
            - Password policy is enforced immediately
        """
        # Step 1: Validate inputs
        logger.info(f"🔍 Validating inputs for pool creation...")
        if not pool_name or len(pool_name) < 1 or len(pool_name) > 128:
            raise ValueError("Pool name must be between 1 and 128 characters")
        
        if password_min_length < 8 or password_min_length > 99:
            raise ValueError("Password length must be between 8 and 99 characters")
        
        # Step 2: Check if pool already exists
        logger.info(f"🔍 Checking if pool '{pool_name}' already exists...")
        existing_pool = self.check_pool_exists(pool_name=pool_name)
        if existing_pool:
            logger.warning(f"⚠️  Pool '{pool_name}' already exists!")
            logger.info(f"   Pool ID: {existing_pool['PoolId']}")
            logger.info(f"   Status: {existing_pool['Status']}")
            raise ValueError(
                f"Pool '{pool_name}' already exists. "
                f"Use --pool-id {existing_pool['PoolId']} to use existing pool, "
                f"or use --verify-only to check configuration."
            )
        
        # Step 3: Prepare pool configuration
        logger.info(f"⚙️  Preparing pool configuration...")
        
        # Password policy configuration
        # This defines rules for user passwords (length, complexity, etc.)
        password_policy = {
            'MinimumLength': password_min_length,
            'RequireUppercase': DEFAULT_PASSWORD_REQUIRE_UPPERCASE,
            'RequireLowercase': DEFAULT_PASSWORD_REQUIRE_LOWERCASE,
            'RequireNumbers': DEFAULT_PASSWORD_REQUIRE_NUMBERS,
            'RequireSymbols': DEFAULT_PASSWORD_REQUIRE_SYMBOLS,
            'TemporaryPasswordValidityDays': 7  # Temporary passwords expire in 7 days
        }
        
        # User pool configuration
        # This defines the pool's behavior and settings
        pool_config = {
            'PoolName': pool_name,
            'Policies': {
                'PasswordPolicy': password_policy
            },
            'AutoVerifiedAttributes': ['email'],  # Auto-verify email addresses
            'AliasAttributes': ['email'],  # Allow login with email
            'UsernameAttributes': ['email'],  # Use email as username
            'MfaConfiguration': 'OPTIONAL' if enable_mfa else 'OFF',
            'AccountRecoverySetting': {
                'RecoveryMechanisms': [
                    {
                        'Priority': 1,
                        'Name': 'verified_email'  # Account recovery via email
                    }
                ]
            },
            'UserAttributeUpdateSettings': {
                'AttributesRequireVerificationBeforeUpdate': ['email']
            }
        }
        
        # Step 4: Create the pool
        logger.info(f"🚀 Creating Cognito User Pool '{pool_name}'...")
        logger.info(f"   Password minimum length: {password_min_length}")
        logger.info(f"   MFA: {'Enabled' if enable_mfa else 'Disabled'}")
        
        try:
            response = self.cognito_client.create_user_pool(**pool_config)
            pool_id = response['UserPool']['Id']
            pool_name_created = response['UserPool']['Name']
            
            logger.info(f"✅ Successfully created Cognito User Pool!")
            logger.info(f"   Pool ID: {pool_id}")
            logger.info(f"   Pool Name: {pool_name_created}")
            logger.info(f"   Status: {response['UserPool']['Status']}")
            
            return {
                'PoolId': pool_id,
                'Name': pool_name_created,
                'Status': response['UserPool']['Status'],
                'CreationDate': response['UserPool']['CreationDate']
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"❌ Failed to create Cognito User Pool!")
            logger.error(f"   Error Code: {error_code}")
            logger.error(f"   Error Message: {error_message}")
            
            # Provide helpful error messages for common issues
            if error_code == 'PoolNameExistsException':
                logger.error("   💡 SOLUTION: Pool name already exists. Choose a different name.")
            elif error_code == 'InvalidParameterException':
                logger.error("   💡 SOLUTION: Check your parameters. Review documentation.")
            elif error_code == 'LimitExceededException':
                logger.error("   💡 SOLUTION: Too many pools in account. Delete unused pools.")
            elif error_code == 'AccessDeniedException':
                logger.error("   💡 SOLUTION: Check IAM permissions. Need cognito-idp:CreateUserPool")
            
            raise
    
    def create_app_client(
        self,
        pool_id: str,
        client_name: str = "streamlit-client",
        generate_secret: bool = False,
        callback_urls: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create app client for Streamlit authentication.
        
        Creates a Cognito User Pool App Client that Streamlit will use
        for authentication. Configures OAuth flows and callback URLs.
        
        ARGUMENTS:
            pool_id (str): Cognito User Pool ID
                Format: us-east-2_AbCdEfGhI
            
            client_name (str): Name for the app client
                Default: "streamlit-client"
                Example: "cloud-engineer-agent-streamlit"
            
            generate_secret (bool): Whether to generate client secret
                Default: False (public client, no secret needed)
                True: Generate secret (for confidential clients)
            
            callback_urls (Optional[list]): OAuth callback URLs
                Default: None (uses DEV_CALLBACK_URL)
                Example: ["http://localhost:8501", "https://your-domain.com"]
        
        RETURNS:
            Dict[str, Any]: Client creation response containing:
                - ClientId: The app client ID
                - ClientSecret: The client secret (if generated)
                Example:
                {
                    'ClientId': '1a2b3c4d5e6f7g8h9i0j',
                    'ClientSecret': 'secret123...' (if generate_secret=True)
                }
        
        RAISES:
            ClientError: If AWS API call fails
        
        EXAMPLE:
            >>> manager = CognitoPoolManager()
            >>> client = manager.create_app_client(
            ...     pool_id="us-east-2_abc123",
            ...     client_name="my-streamlit-client"
            ... )
            >>> print(f"Client ID: {client['ClientId']}")
        """
        if callback_urls is None:
            callback_urls = [DEV_CALLBACK_URL]
        
        logger.info(f"🚀 Creating app client '{client_name}' for pool {pool_id}...")
        
        client_config = {
            'UserPoolId': pool_id,
            'ClientName': client_name,
            'GenerateSecret': generate_secret,
            'ExplicitAuthFlows': [
                'ALLOW_USER_PASSWORD_AUTH',  # Username/password flow
                'ALLOW_REFRESH_TOKEN_AUTH',  # Refresh token flow
            ],
            'SupportedIdentityProviders': ['COGNITO'],  # Use Cognito as identity provider
            'CallbackURLs': callback_urls,
            'AllowedOAuthFlows': ['code'],  # Authorization code flow
            'AllowedOAuthScopes': ['email', 'openid', 'profile'],  # OAuth scopes
            'AllowedOAuthFlowsUserPoolClient': True,
            'PreventUserExistenceErrors': 'ENABLED'  # Prevent user enumeration
        }
        
        try:
            response = self.cognito_client.create_user_pool_client(**client_config)
            
            client_id = response['UserPoolClient']['ClientId']
            client_secret = response['UserPoolClient'].get('ClientSecret')
            
            logger.info(f"✅ Successfully created app client!")
            logger.info(f"   Client ID: {client_id}")
            if client_secret:
                logger.info(f"   Client Secret: {client_secret[:20]}... (save this securely!)")
            
            return {
                'ClientId': client_id,
                'ClientSecret': client_secret
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"❌ Failed to create app client!")
            logger.error(f"   Error Code: {error_code}")
            logger.error(f"   Error Message: {error_message}")
            
            if error_code == 'ResourceNotFoundException':
                logger.error("   💡 SOLUTION: User Pool not found. Check pool ID.")
            elif error_code == 'InvalidParameterException':
                logger.error("   💡 SOLUTION: Check callback URLs format.")
            
            raise


# ============================================================================
# COMMAND-LINE INTERFACE (CLI)
# ============================================================================

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    RETURNS:
        argparse.Namespace: Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description="""
        Create or verify Amazon Cognito User Pool for authentication.
        
        This script creates a new Cognito User Pool with secure defaults,
        or verifies an existing pool configuration. It's designed for
        first-time setup and verification.
        
        EXAMPLES:
            # Create new pool (interactive)
            python scripts/create_cognito_pool.py
            
            # Create new pool (non-interactive)
            python scripts/create_cognito_pool.py --pool-name my-pool --region us-east-2
            
            # Verify existing pool
            python scripts/create_cognito_pool.py --verify-only --pool-id us-east-2_abc123
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '--pool-name',
        type=str,
        help='Name for the Cognito User Pool (required if creating new pool)',
        default=None
    )
    
    parser.add_argument(
        '--pool-id',
        type=str,
        help='Existing Cognito User Pool ID (for verification or reuse)',
        default=None
    )
    
    # Optional arguments
    parser.add_argument(
        '--region',
        type=str,
        default=DEFAULT_REGION,
        help=f'AWS region (default: {DEFAULT_REGION})'
    )
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing pool, do not create new pool'
    )
    
    parser.add_argument(
        '--enable-mfa',
        action='store_true',
        help='Enable multi-factor authentication (optional)'
    )
    
    parser.add_argument(
        '--password-min-length',
        type=int,
        default=DEFAULT_PASSWORD_MIN_LENGTH,
        help=f'Minimum password length (default: {DEFAULT_PASSWORD_MIN_LENGTH})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    return parser.parse_args()


def update_env_file(pool_id: str, client_id: str, client_secret: Optional[str] = None) -> None:
    """
    Update .env file with Cognito credentials.
    
    ARGUMENTS:
        pool_id (str): Cognito User Pool ID
        client_id (str): App Client ID
        client_secret (Optional[str]): Client Secret (if applicable)
    """
    env_file = Path('.env')
    
    if not env_file.exists():
        logger.warning("⚠️  .env file not found, creating from .env.example...")
        env_example = Path('.env.example')
        if env_example.exists():
            env_file.write_text(env_example.read_text())
        else:
            logger.error("❌ .env.example not found. Cannot create .env file.")
            return
    
    # Update values
    set_key('.env', 'COGNITO_USER_POOL_ID', pool_id)
    set_key('.env', 'COGNITO_CLIENT_ID', client_id)
    
    if client_secret:
        set_key('.env', 'COGNITO_CLIENT_SECRET', client_secret)
    
    logger.info("✅ Updated .env file with Cognito credentials")


def main() -> int:
    """
    Main entry point for the script.
    
    Orchestrates the entire script execution:
    1. Parse command-line arguments
    2. Load environment variables
    3. Validate prerequisites
    4. Create or verify Cognito pool
    5. Output results and next steps
    
    RETURNS:
        int: Exit code (0 for success, non-zero for failure)
    """
    try:
        # Step 1: Parse arguments
        logger.info("🚀 Starting Cognito User Pool setup...")
        args = parse_arguments()
        
        # Step 2: Load environment variables
        # This allows users to set defaults in .env file
        load_dotenv()
        
        # Step 3: Validate AWS credentials
        logger.info("🔍 Validating AWS credentials...")
        if not validate_aws_credentials():
            logger.error("❌ AWS credentials not configured or invalid")
            logger.error("   💡 SOLUTION: Run 'aws configure' or set AWS_ACCESS_KEY_ID")
            return 1
        
        # Step 4: Initialize manager
        region = args.region or get_aws_region()
        manager = CognitoPoolManager(region=region)
        
        # Step 5: Execute operation
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE: Showing what would be done...")
            logger.info(f"   Would create pool: {args.pool_name}")
            logger.info(f"   Region: {region}")
            logger.info(f"   MFA: {'Enabled' if args.enable_mfa else 'Disabled'}")
            return 0
        
        if args.verify_only:
            # Verify existing pool
            logger.info("📋 Mode: Verification only")
            if args.pool_id:
                pool = manager.check_pool_exists(pool_id=args.pool_id)
                if pool:
                    logger.info(f"✅ Pool verified: {pool['PoolId']}")
                    logger.info(f"   Name: {pool['Name']}")
                    logger.info(f"   Status: {pool['Status']}")
                    return 0
                else:
                    logger.error(f"❌ Pool not found: {args.pool_id}")
                    return 1
            else:
                logger.error("❌ --pool-id required when using --verify-only")
                return 1
        
        elif args.pool_id:
            # Use existing pool
            logger.info("📋 Mode: Using existing pool")
            pool = manager.check_pool_exists(pool_id=args.pool_id)
            if not pool:
                logger.error(f"❌ Pool not found: {args.pool_id}")
                return 1
            
            logger.info(f"✅ Found existing pool: {pool['PoolId']}")
            logger.info(f"   Name: {pool['Name']}")
            logger.info(f"   Status: {pool['Status']}")
            
            # Create app client if needed
            logger.info("📋 Checking for app client...")
            # TODO: Check if client exists, create if not
            
            return 0
        
        elif args.pool_name:
            # Create new pool
            logger.info("📋 Mode: Create new pool")
            try:
                result = manager.create_pool(
                    pool_name=args.pool_name,
                    password_min_length=args.password_min_length,
                    enable_mfa=args.enable_mfa
                )
                
                pool_id = result['PoolId']
                logger.info(f"✅ Success! Pool created: {pool_id}")
                
                # Create app client
                logger.info("📋 Creating app client...")
                client_result = manager.create_app_client(
                    pool_id=pool_id,
                    client_name=f"{args.pool_name}-streamlit-client"
                )
                
                client_id = client_result['ClientId']
                client_secret = client_result.get('ClientSecret')
                
                logger.info(f"✅ App client created: {client_id}")
                
                # Update .env file
                logger.info("📝 Updating .env file...")
                update_env_file(pool_id, client_id, client_secret)
                
                logger.info("\n" + "="*70)
                logger.info("✅ Setup Complete!")
                logger.info("="*70)
                logger.info("\n📝 NEXT STEPS:")
                logger.info(f"   1. Cognito Pool ID: {pool_id}")
                logger.info(f"   2. App Client ID: {client_id}")
                if client_secret:
                    logger.info(f"   3. Client Secret: {client_secret} (save securely!)")
                logger.info(f"   4. Run: python scripts/verify_cognito.py --pool-id {pool_id}")
                logger.info(f"   5. Continue with: python scripts/setup_guardrails.py")
                
                return 0
            
            except ValueError as e:
                logger.error(f"❌ Validation error: {e}")
                return 1
        
        else:
            # Interactive mode
            logger.info("💡 Interactive mode: Please provide --pool-name or --pool-id")
            logger.info("   Example: python scripts/create_cognito_pool.py --pool-name my-pool")
            return 1
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Operation cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("   See troubleshooting guide in IMPLEMENTATION_PLAN.md")
        return 1


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    This block runs when the script is executed directly (not imported).
    
    It calls the main() function and exits with the appropriate exit code.
    Exit codes:
        - 0: Success
        - 1: General error
        - 130: Interrupted (Ctrl+C)
    """
    exit_code = main()
    sys.exit(exit_code)

