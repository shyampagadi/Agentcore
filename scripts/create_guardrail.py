"""
===============================================================================
SCRIPT NAME: create_guardrail.py
===============================================================================

PURPOSE:
    Creates Amazon Bedrock Guardrail resource.

USAGE:
    python scripts/create_guardrail.py [--name NAME] [--description DESC]

OPTIONS:
    --name NAME: Guardrail name (default: cloud-engineer-agent-guardrail)
    --description DESC: Guardrail description (optional)

WHAT THIS SCRIPT DOES:
    1. Creates Bedrock Guardrail with default configuration
    2. Configures content filters (profanity, hate speech, violence, etc.)
    3. Sets up topic blocking (cloud engineering focused)
    4. Updates .env file with Guardrail ID and version

OUTPUTS:
    - Updates .env file with BEDROCK_GUARDRAIL_ID and BEDROCK_GUARDRAIL_VERSION
    - Prints Guardrail ID, version, and ARN

TROUBLESHOOTING:
    - Ensure AWS credentials are configured
    - Verify bedrock:CreateGuardrail permissions
    - Check region is correct (us-east-2)

RELATED FILES:
    - guardrails/guardrail_setup.py - Guardrail creation logic
    - guardrails/guardrail_config.py - Guardrail configuration
    - scripts/setup_guardrails.py - Combined setup script

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
from guardrails.guardrail_setup import create_guardrail
from guardrails.guardrail_config import get_default_config

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create Amazon Bedrock Guardrail resource'
    )
    parser.add_argument(
        '--name',
        default='cloud-engineer-agent-guardrail',
        help='Guardrail name (default: cloud-engineer-agent-guardrail)'
    )
    parser.add_argument(
        '--description',
        default=None,
        help='Guardrail description (optional)'
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Creating Bedrock Guardrail...")
    logger.info(f"   Name: {args.name}")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        logger.info("   💡 Run: aws configure")
        return 1
    
    load_dotenv()
    
    try:
        # Get default configuration
        config = get_default_config()
        config['name'] = args.name
        if args.description:
            config['description'] = args.description
        
        # Create guardrail
        result = create_guardrail(config)
        
        # Update .env file
        set_key('.env', 'BEDROCK_GUARDRAIL_ID', result['guardrail_id'])
        set_key('.env', 'BEDROCK_GUARDRAIL_VERSION', result['guardrail_version'])
        
        logger.info("✅ Guardrail created successfully!")
        logger.info(f"   Guardrail ID: {result['guardrail_id']}")
        logger.info(f"   Guardrail Version: {result['guardrail_version']}")
        if result.get('guardrail_arn'):
            logger.info(f"   Guardrail ARN: {result['guardrail_arn']}")
        logger.info("   ✅ Updated .env file with Guardrail details")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to create Guardrail: {e}")
        
        # Check for common errors
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            logger.info("   💡 Guardrail already exists. Use a different name or check existing guardrails.")
        elif 'permission' in error_msg or 'access' in error_msg:
            logger.info("   💡 Check IAM permissions for bedrock:CreateGuardrail")
        elif 'region' in error_msg:
            logger.info(f"   💡 Verify region is correct (current: {os.getenv('AWS_REGION', 'us-east-2')})")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

