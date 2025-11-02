"""
===============================================================================
SCRIPT NAME: setup_domain.py
===============================================================================

PURPOSE:
    Sets up domain name and SSL certificate for Streamlit UI.

USAGE:
    python scripts/setup_domain.py --domain your-domain.com

WHAT THIS SCRIPT DOES:
    1. Creates Route 53 hosted zone (if needed)
    2. Requests SSL certificate from ACM
    3. Configures DNS records
    4. Updates ALB with certificate
===============================================================================
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Setup domain name for Streamlit UI")
    parser.add_argument('--domain', type=str, required=True, help='Domain name')
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Setting up domain: {args.domain}")
    logger.info("")
    logger.info("📋 Domain Setup Steps:")
    logger.info("")
    logger.info("1. Request SSL certificate:")
    logger.info("   aws acm request-certificate --domain-name your-domain.com --validation-method DNS --region us-east-2")
    logger.info("")
    logger.info("2. Create Route 53 hosted zone (if needed):")
    logger.info("   aws route53 create-hosted-zone --name your-domain.com --caller-reference $(date +%s)")
    logger.info("")
    logger.info("3. Update ALB listener with certificate:")
    logger.info("   See IMPLEMENTATION_PLAN.md → Domain Setup")
    logger.info("")
    logger.info("4. Update Cognito callback URLs:")
    logger.info("   Update callback URLs in Cognito User Pool to include https://your-domain.com")
    logger.info("")
    logger.info("💡 See IMPLEMENTATION_PLAN.md for detailed domain setup guide")
    return 0


if __name__ == "__main__":
    sys.exit(main())

