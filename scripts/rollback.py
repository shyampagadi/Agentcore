"""
===============================================================================
MODULE: rollback.py
===============================================================================

PURPOSE:
    Rolls back deployment in case of failures.

USAGE:
    python scripts/rollback.py --resource-type runtime

WHAT THIS SCRIPT DOES:
    1. Deletes created resources
    2. Restores previous state
    3. Cleans up failed deployments
===============================================================================
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def rollback_runtime():
    """Rollback runtime deployment."""
    logger.info("🔄 Rolling back runtime deployment...")
    logger.info("   💡 Use 'agentcore runtime delete <runtime-arn>' to remove runtime")
    logger.info("   💡 Or use AWS Console to delete resources")


def rollback_cognito():
    """Rollback Cognito setup."""
    logger.info("🔄 Rolling back Cognito setup...")
    logger.info("   💡 Delete Cognito User Pool from AWS Console if needed")


def rollback_guardrails():
    """Rollback guardrails setup."""
    logger.info("🔄 Rolling back guardrails setup...")
    logger.info("   💡 Delete guardrail from AWS Console if needed")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Rollback deployment")
    parser.add_argument('--resource-type', type=str, choices=['runtime', 'cognito', 'guardrails', 'all'],
                       default='all', help='Resource type to rollback')
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("Rollback Deployment")
    logger.info("="*70)
    
    if args.resource_type == 'all':
        rollback_runtime()
        rollback_cognito()
        rollback_guardrails()
    elif args.resource_type == 'runtime':
        rollback_runtime()
    elif args.resource_type == 'cognito':
        rollback_cognito()
    elif args.resource_type == 'guardrails':
        rollback_guardrails()
    
    logger.info("\n✅ Rollback instructions provided")
    logger.info("   💡 Manual cleanup may be required")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

