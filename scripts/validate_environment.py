"""
===============================================================================
SCRIPT NAME: validate_environment.py
===============================================================================

PURPOSE:
    Validates that the development environment is properly configured before
    starting implementation. This script checks all prerequisites including
    AWS credentials, Python dependencies, configuration files, and service access.

WHEN TO USE THIS SCRIPT:
    - First-time setup: After installing dependencies and configuring .env
    - Before deployment: Verify everything is ready
    - Troubleshooting: Diagnose configuration issues
    - CI/CD pipelines: Validate environment before deployment

PREREQUISITES:
    - Python 3.10+ installed
    - AWS CLI configured (or environment variables set)
    - .env file created with basic values
    - Dependencies installed (pip install -r requirements.txt)

USAGE EXAMPLES:
    # Basic validation (checks everything)
    python scripts/validate_environment.py

    # Quick validation (skip dependency checks)
    python scripts/validate_environment.py --skip-dependencies

    # Validate specific checks only
    python scripts/validate_environment.py --check aws --check python

    # Verbose output (more details)
    python scripts/validate_environment.py --verbose

WHAT THIS SCRIPT DOES:
    1. Validates Python version (3.10+)
    2. Checks AWS credentials are configured
    3. Verifies AWS region is accessible
    4. Validates Bedrock model access
    5. Checks Cognito User Pool accessibility
    6. Verifies Python dependencies are installed
    7. Validates .env file exists and has required values
    8. Checks IAM permissions for required services

OUTPUTS:
    - Console: Step-by-step validation results
    - Exit code: 0 if all checks pass, 1 if any check fails
    - Summary: List of passed/failed checks

TROUBLESHOOTING:
    - "Python version too old": Install Python 3.10+ from python.org
    - "AWS credentials not found": Run `aws configure` or set environment variables
    - "Module not found": Run `pip install -r requirements.txt`
    - "Access denied": Check IAM permissions (see IMPLEMENTATION_PLAN.md)

RELATED FILES:
    - .env - Configuration file being validated
    - requirements.txt - Python dependencies being checked
    - IMPLEMENTATION_PLAN.md - Detailed setup instructions

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
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
# boto3: AWS SDK for Python
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import (
    validate_aws_credentials,
    get_aws_region,
    get_aws_account_id,
    check_service_access
)

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Required Python version (minimum)
REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 10

# Required environment variables (must be set in .env)
REQUIRED_ENV_VARS = [
    'AWS_REGION',
    'AWS_ACCOUNT_ID',
    'COGNITO_USER_POOL_ID'
]

# Optional environment variables (will be populated by scripts)
OPTIONAL_ENV_VARS = [
    'COGNITO_CLIENT_ID',
    'AGENT_RUNTIME_ARN',
    'MEMORY_RESOURCE_ARN',
    'BEDROCK_GUARDRAIL_ID'
]

# Required Python packages (must be importable)
REQUIRED_PACKAGES = [
    'boto3',
    'bedrock_agentcore',
    'streamlit',
    'dotenv'
]

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_python_version() -> Tuple[bool, str]:
    """
    Check Python version meets requirements.
    
    Validates that Python 3.10 or higher is installed. This is required
    for bedrock-agentcore and other dependencies.
    
    RETURNS:
        Tuple[bool, str]: (is_valid, message)
            is_valid: True if Python version is acceptable
            message: Human-readable status message
    
    EXAMPLE:
        >>> is_valid, msg = check_python_version()
        >>> print(f"{msg}: {is_valid}")
    """
    version = sys.version_info
    major = version.major
    minor = version.minor
    
    if major == REQUIRED_PYTHON_MAJOR and minor >= REQUIRED_PYTHON_MINOR:
        return True, f"✅ Python {major}.{minor}.{version.micro} (meets requirement: {REQUIRED_PYTHON_MAJOR}.{REQUIRED_PYTHON_MINOR}+)"
    
    return False, f"❌ Python {major}.{minor}.{version.micro} (requires {REQUIRED_PYTHON_MAJOR}.{REQUIRED_PYTHON_MINOR}+)"


def check_python_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if required Python packages are installed.
    
    Attempts to import each required package. Returns list of missing packages.
    
    RETURNS:
        Tuple[bool, List[str]]: (all_installed, missing_packages)
            all_installed: True if all packages are available
            missing_packages: List of package names that couldn't be imported
    
    EXAMPLE:
        >>> all_installed, missing = check_python_dependencies()
        >>> if not all_installed:
        ...     print(f"Missing packages: {', '.join(missing)}")
    """
    missing = []
    
    for package in REQUIRED_PACKAGES:
        try:
            # Try to import the package
            # Note: Some packages have different import names
            import_map = {
                'bedrock_agentcore': 'bedrock_agentcore',
                'dotenv': 'dotenv',
                'boto3': 'boto3',
                'streamlit': 'streamlit'
            }
            
            import_name = import_map.get(package, package)
            __import__(import_name)
            logger.debug(f"   ✅ Package '{package}' is installed")
        
        except ImportError:
            missing.append(package)
            logger.debug(f"   ❌ Package '{package}' is NOT installed")
    
    return len(missing) == 0, missing


def check_env_file() -> Tuple[bool, List[str]]:
    """
    Check if .env file exists and has required variables.
    
    Validates that .env file exists and contains all required environment
    variables. Also checks that optional variables are documented.
    
    RETURNS:
        Tuple[bool, List[str]]: (is_valid, missing_vars)
            is_valid: True if .env exists and has all required vars
            missing_vars: List of missing required environment variables
    
    EXAMPLE:
        >>> is_valid, missing = check_env_file()
        >>> if not is_valid:
        ...     print(f"Missing variables: {', '.join(missing)}")
    """
    env_path = Path('.env')
    
    if not env_path.exists():
        return False, ["File '.env' not found"]
    
    # Load environment variables
    load_dotenv()
    
    missing = []
    for var in REQUIRED_ENV_VARS:
        value = os.getenv(var)
        if not value or value.startswith('<'):
            missing.append(var)
            logger.debug(f"   ❌ {var}: Not set or placeholder")
        else:
            logger.debug(f"   ✅ {var}: Set")
    
    return len(missing) == 0, missing


def check_aws_services(region: str) -> Dict[str, bool]:
    """
    Check access to required AWS services.
    
    Tests access to AWS services needed for the application:
    - Cognito (for authentication)
    - Bedrock (for model access)
    - AgentCore (for runtime, memory, identity)
    
    ARGUMENTS:
        region (str): AWS region to test
    
    RETURNS:
        Dict[str, bool]: Dictionary mapping service names to access status
            Example: {'cognito-idp': True, 'bedrock': True, 'bedrock-agentcore': False}
    
    EXAMPLE:
        >>> services = check_aws_services('us-east-2')
        >>> for service, accessible in services.items():
        ...     print(f"{service}: {'✅' if accessible else '❌'}")
    """
    services_to_check = {
        'cognito-idp': 'Cognito (Authentication)',
        'bedrock': 'Bedrock (Model Access)',
        'bedrock-agentcore': 'AgentCore (Runtime, Memory, Identity)'
    }
    
    results = {}
    
    for service, display_name in services_to_check.items():
        logger.info(f"🔍 Checking {display_name} access...")
        accessible = check_service_access(service, region=region)
        results[service] = accessible
        
        if accessible:
            logger.info(f"   ✅ {display_name} is accessible")
        else:
            logger.error(f"   ❌ {display_name} is NOT accessible")
    
    return results


def check_cognito_pool(pool_id: str, region: str) -> Tuple[bool, str]:
    """
    Check if Cognito User Pool exists and is accessible.
    
    Validates that the Cognito User Pool specified in .env file exists
    and can be accessed with current credentials.
    
    ARGUMENTS:
        pool_id (str): Cognito User Pool ID
            Format: us-east-2_AbCdEfGhI
        
        region (str): AWS region where pool is located
    
    RETURNS:
        Tuple[bool, str]: (is_valid, message)
            is_valid: True if pool exists and is accessible
            message: Human-readable status message
    
    EXAMPLE:
        >>> is_valid, msg = check_cognito_pool('us-east-2_abc123', 'us-east-2')
        >>> print(msg)
    """
    if not pool_id or pool_id.startswith('<'):
        return False, "❌ Cognito User Pool ID not set in .env file"
    
    try:
        cognito_client = boto3.client('cognito-idp', region_name=region)
        
        # Try to describe the user pool
        response = cognito_client.describe_user_pool(UserPoolId=pool_id)
        
        pool_name = response['UserPool'].get('Name', 'Unknown')
        pool_status = response['UserPool'].get('Status', 'Unknown')
        
        return True, f"✅ Cognito User Pool '{pool_name}' ({pool_id}) is accessible (Status: {pool_status})"
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'ResourceNotFoundException':
            return False, f"❌ Cognito User Pool '{pool_id}' not found. Check pool ID in .env file."
        elif error_code == 'AccessDeniedException':
            return False, f"❌ Access denied to Cognito User Pool. Check IAM permissions."
        else:
            return False, f"❌ Error accessing Cognito User Pool: {error_code} - {error_message}"
    
    except Exception as e:
        return False, f"❌ Unexpected error checking Cognito: {e}"


def check_bedrock_model_access(region: str) -> Tuple[bool, str]:
    """
    Check if Bedrock model access is enabled.
    
    Validates that Bedrock foundation models (specifically Claude) are
    accessible. This is required for the agent to function.
    
    ARGUMENTS:
        region (str): AWS region to check
    
    RETURNS:
        Tuple[bool, str]: (is_valid, message)
            is_valid: True if models are accessible
            message: Human-readable status message
    
    EXAMPLE:
        >>> is_valid, msg = check_bedrock_model_access('us-east-2')
        >>> print(msg)
    """
    try:
        bedrock_client = boto3.client('bedrock', region_name=region)
        
        # List foundation models
        response = bedrock_client.list_foundation_models()
        
        # Check for Claude models
        models = response.get('modelSummaries', [])
        claude_models = [m for m in models if 'claude' in m.get('modelId', '').lower()]
        
        if claude_models:
            model_ids = [m['modelId'] for m in claude_models[:3]]  # Show first 3
            return True, f"✅ Bedrock model access enabled ({len(claude_models)} Claude models found, e.g., {', '.join(model_ids)})"
        else:
            return False, "❌ No Claude models found. Enable model access in AWS Console → Bedrock → Model access"
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'AccessDeniedException':
            return False, "❌ Access denied to Bedrock. Check IAM permissions and model access."
        else:
            return False, f"❌ Error checking Bedrock access: {error_code}"
    
    except Exception as e:
        return False, f"❌ Unexpected error checking Bedrock: {e}"


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
        Validate development environment configuration.
        
        This script checks all prerequisites including AWS credentials,
        Python dependencies, configuration files, and service access.
        Run this before starting implementation to ensure everything is ready.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--skip-dependencies',
        action='store_true',
        help='Skip Python dependency checks (faster validation)'
    )
    
    parser.add_argument(
        '--skip-aws',
        action='store_true',
        help='Skip AWS credential and service checks'
    )
    
    parser.add_argument(
        '--check',
        action='append',
        choices=['python', 'dependencies', 'env', 'aws', 'cognito', 'bedrock'],
        help='Run specific checks only (can be used multiple times)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for each check'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the script.
    
    Orchestrates all validation checks and reports results.
    
    RETURNS:
        int: Exit code (0 if all checks pass, 1 if any check fails)
    """
    args = parse_arguments()
    
    logger.info("="*70)
    logger.info("Environment Validation")
    logger.info("="*70)
    logger.info("")
    
    # Determine which checks to run
    checks_to_run = {
        'python': args.check is None or 'python' in args.check,
        'dependencies': args.check is None or 'dependencies' in args.check,
        'env': args.check is None or 'env' in args.check,
        'aws': args.check is None or 'aws' in args.check,
        'cognito': args.check is None or 'cognito' in args.check,
        'bedrock': args.check is None or 'bedrock' in args.check
    }
    
    # Apply skip flags
    if args.skip_dependencies:
        checks_to_run['dependencies'] = False
    if args.skip_aws:
        checks_to_run['aws'] = False
        checks_to_run['cognito'] = False
        checks_to_run['bedrock'] = False
    
    # Track results
    results = {}
    all_passed = True
    
    # ========================================================================
    # CHECK 1: Python Version
    # ========================================================================
    if checks_to_run['python']:
        logger.info("1. Checking Python Version...")
        is_valid, message = check_python_version()
        results['python'] = is_valid
        logger.info(f"   {message}")
        if not is_valid:
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 2: Python Dependencies
    # ========================================================================
    if checks_to_run['dependencies']:
        logger.info("2. Checking Python Dependencies...")
        all_installed, missing = check_python_dependencies()
        results['dependencies'] = all_installed
        
        if all_installed:
            logger.info(f"   ✅ All required packages are installed")
        else:
            logger.error(f"   ❌ Missing packages: {', '.join(missing)}")
            logger.error(f"   💡 SOLUTION: Run 'pip install -r requirements.txt'")
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 3: Environment File
    # ========================================================================
    if checks_to_run['env']:
        logger.info("3. Checking .env File...")
        is_valid, missing = check_env_file()
        results['env'] = is_valid
        
        if is_valid:
            logger.info(f"   ✅ .env file exists and has required variables")
        else:
            logger.error(f"   ❌ Missing variables: {', '.join(missing)}")
            logger.error(f"   💡 SOLUTION: Copy .env.example to .env and fill in values")
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 4: AWS Credentials
    # ========================================================================
    if checks_to_run['aws']:
        logger.info("4. Checking AWS Credentials...")
        is_valid = validate_aws_credentials()
        results['aws'] = is_valid
        
        if not is_valid:
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 5: AWS Region
    # ========================================================================
    if checks_to_run['aws']:
        logger.info("5. Checking AWS Region...")
        region = get_aws_region()
        account_id = get_aws_account_id()
        
        if account_id:
            logger.info(f"   ✅ Region: {region}, Account ID: {account_id}")
            results['region'] = True
        else:
            logger.error(f"   ❌ Failed to get account ID")
            results['region'] = False
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 6: Cognito User Pool
    # ========================================================================
    if checks_to_run['cognito']:
        logger.info("6. Checking Cognito User Pool...")
        load_dotenv()
        pool_id = os.getenv('COGNITO_USER_POOL_ID', '')
        region = get_aws_region()
        
        is_valid, message = check_cognito_pool(pool_id, region)
        results['cognito'] = is_valid
        logger.info(f"   {message}")
        
        if not is_valid:
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 7: Bedrock Model Access
    # ========================================================================
    if checks_to_run['bedrock']:
        logger.info("7. Checking Bedrock Model Access...")
        region = get_aws_region()
        
        is_valid, message = check_bedrock_model_access(region)
        results['bedrock'] = is_valid
        logger.info(f"   {message}")
        
        if not is_valid:
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # CHECK 8: AWS Service Access
    # ========================================================================
    if checks_to_run['aws']:
        logger.info("8. Checking AWS Service Access...")
        region = get_aws_region()
        services = check_aws_services(region)
        results['services'] = all(services.values())
        
        if all(services.values()):
            logger.info("   ✅ All required AWS services are accessible")
        else:
            failed_services = [s for s, accessible in services.items() if not accessible]
            logger.error(f"   ❌ Services not accessible: {', '.join(failed_services)}")
            all_passed = False
        logger.info("")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    logger.info("="*70)
    logger.info("Validation Summary")
    logger.info("="*70)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"   {status}: {check_name}")
    
    logger.info("")
    
    if all_passed:
        logger.info("✅ All checks passed! Environment is ready for implementation.")
        logger.info("   Next steps:")
        logger.info("   1. Review IMPLEMENTATION_PLAN.md")
        logger.info("   2. Start with Phase 1: Foundation Setup")
        logger.info("   3. Run: python scripts/create_cognito_pool.py (if needed)")
        return 0
    else:
        logger.error("❌ Some checks failed. Please fix the issues above before proceeding.")
        logger.error("   See IMPLEMENTATION_PLAN.md → Troubleshooting Guide for help.")
        return 1


# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    This block runs when the script is executed directly.
    """
    exit_code = main()
    sys.exit(exit_code)

