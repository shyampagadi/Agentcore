"""
===============================================================================
SCRIPT NAME: create_agentcore_memory.py
===============================================================================

PURPOSE:
    Creates AgentCore Memory resource.

USAGE:
    python scripts/create_agentcore_memory.py [--name NAME] [--enable-ltm] [--disable-ltm]

OPTIONS:
    --name NAME: Memory resource name (default: cloud-engineer-agent-memory)
    --enable-ltm: Enable Long-Term Memory (default: True)
    --disable-ltm: Disable Long-Term Memory

WHAT THIS SCRIPT DOES:
    1. Creates Memory resource using AgentCore SDK
    2. Configures STM (Short-Term Memory) and optionally LTM (Long-Term Memory)
    3. Updates .env file with Memory ARN and ID
    4. Validates AWS credentials

OUTPUTS:
    - Updates .env file with MEMORY_RESOURCE_ARN and MEMORY_RESOURCE_ID
    - Prints Memory ARN, ID, and status

TROUBLESHOOTING:
    - Ensure bedrock-agentcore-starter-toolkit is installed
    - Verify AWS credentials have bedrock-agentcore permissions
    - Check region is correct (us-east-2)

RELATED FILES:
    - memory/memory_resource_manager.py - Memory creation logic
    - scripts/setup_agentcore_resources.py - Combined setup script

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

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create AgentCore Memory resource'
    )
    parser.add_argument(
        '--name',
        default='cloud-engineer-agent-memory',
        help='Memory resource name (default: cloud-engineer-agent-memory)'
    )
    parser.add_argument(
        '--enable-ltm',
        action='store_true',
        default=True,
        help='Enable Long-Term Memory (default: True)'
    )
    parser.add_argument(
        '--disable-ltm',
        action='store_true',
        help='Disable Long-Term Memory (overrides --enable-ltm)'
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Creating AgentCore Memory resource...")
    logger.info(f"   Name: {args.name}")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        logger.info("   💡 Run: aws configure")
        return 1
    
    load_dotenv()
    
    try:
        from memory.memory_resource_manager import create_memory_resource
        
        enable_ltm = args.enable_ltm and not args.disable_ltm
        logger.info(f"   Long-Term Memory: {'Enabled' if enable_ltm else 'Disabled'}")
        
        memory_result = create_memory_resource(
            name=args.name,
            description=f"Memory resource for Cloud Engineer Agent",
            enable_ltm=enable_ltm
        )
        
        # Update .env file
        if memory_result.get('memory_arn'):
            set_key('.env', 'MEMORY_RESOURCE_ARN', memory_result['memory_arn'])
        if memory_result.get('memory_id'):
            set_key('.env', 'MEMORY_RESOURCE_ID', memory_result['memory_id'])
        
        logger.info("✅ Memory resource created successfully!")
        logger.info(f"   Memory ID: {memory_result['memory_id']}")
        logger.info(f"   Memory ARN: {memory_result['memory_arn']}")
        logger.info(f"   Status: {memory_result['status']}")
        logger.info(f"   Strategies: {', '.join(memory_result.get('strategies', []))}")
        logger.info("   ✅ Updated .env file with Memory details")
        
        return 0
    
    except ImportError as e:
        logger.error(f"❌ Failed to import Memory manager: {e}")
        logger.info("   💡 Install bedrock-agentcore-starter-toolkit:")
        logger.info("      pip install bedrock-agentcore-starter-toolkit")
        return 1
    except Exception as e:
        logger.error(f"❌ Failed to create Memory resource: {e}")
        
        # Check for common errors
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            logger.info("   💡 Memory already exists. Use a different name or check existing memories.")
        elif 'permission' in error_msg or 'access' in error_msg:
            logger.info("   💡 Check IAM permissions for bedrock-agentcore:CreateMemoryResource")
        elif 'region' in error_msg:
            logger.info(f"   💡 Verify region is correct (current: {os.getenv('AWS_REGION', 'us-east-2')})")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

