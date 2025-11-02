"""
===============================================================================
MODULE: test_deployment.py
===============================================================================

PURPOSE:
    Tests deployment configuration and validates setup.

USAGE:
    python scripts/test_deployment.py

WHAT THIS SCRIPT DOES:
    1. Validates all resources exist
    2. Tests connectivity
    3. Validates configuration
    4. Runs smoke tests
===============================================================================
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, check_service_access
from auth.cognito_verification import verify_cognito_configuration
from guardrails.guardrail_setup import get_guardrail_config
from dotenv import load_dotenv

logger = setup_logger(__name__)


def test_all_resources() -> bool:
    """Test all resources."""
    logger.info("🔍 Testing deployment resources...")
    
    all_passed = True
    
    # Test AWS credentials
    logger.info("\n1. Testing AWS credentials...")
    if validate_aws_credentials():
        logger.info("   ✅ AWS credentials valid")
    else:
        logger.error("   ❌ AWS credentials invalid")
        all_passed = False
    
    # Test Cognito
    logger.info("\n2. Testing Cognito configuration...")
    cognito_result = verify_cognito_configuration()
    if cognito_result['valid']:
        logger.info("   ✅ Cognito configuration valid")
    else:
        logger.error(f"   ❌ Cognito errors: {cognito_result['errors']}")
        all_passed = False
    
    # Test Guardrails
    logger.info("\n3. Testing Guardrails configuration...")
    guardrail_config = get_guardrail_config()
    if guardrail_config['enabled']:
        logger.info(f"   ✅ Guardrail configured: {guardrail_config['guardrail_id']}")
    else:
        logger.warning("   ⚠️  Guardrail not configured")
    
    # Test service access
    logger.info("\n4. Testing AWS service access...")
    services = ['bedrock', 'cognito-idp', 'bedrock-agentcore']
    for service in services:
        if check_service_access(service):
            logger.info(f"   ✅ {service} accessible")
        else:
            logger.error(f"   ❌ {service} not accessible")
            all_passed = False
    
    return all_passed


def main() -> int:
    """Main entry point."""
    logger.info("="*70)
    logger.info("Deployment Testing")
    logger.info("="*70)
    
    load_dotenv()
    
    if test_all_resources():
        logger.info("\n✅ All deployment tests passed!")
        return 0
    else:
        logger.error("\n❌ Some deployment tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

