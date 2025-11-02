"""
===============================================================================
SCRIPT NAME: setup_guardrails.py
===============================================================================

PURPOSE:
    Sets up Amazon Bedrock Guardrails for content safety.

USAGE:
    python scripts/setup_guardrails.py

WHAT THIS SCRIPT DOES:
    1. Creates Bedrock Guardrail
    2. Configures content filters
    3. Sets up topic blocking
    4. Updates .env file with guardrail ID
===============================================================================
"""

import os
import sys
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
    logger.info("🚀 Setting up Bedrock Guardrails...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    
    # Get configuration
    config = get_default_config()
    
    try:
        # Create guardrail
        result = create_guardrail(
            name=config['name'],
            description=config['description'],
            blocked_topics=config.get('blocked_topics'),
            content_filters=config.get('content_filters')
        )
        
        # Update .env file
        set_key('.env', 'BEDROCK_GUARDRAIL_ID', result['guardrail_id'])
        set_key('.env', 'BEDROCK_GUARDRAIL_VERSION', 'DRAFT')
        
        logger.info("✅ Guardrail setup complete!")
        logger.info(f"   Guardrail ID: {result['guardrail_id']}")
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to setup guardrails: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

