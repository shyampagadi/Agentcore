"""
===============================================================================
SCRIPT NAME: setup_agentcore_resources.py
===============================================================================

PURPOSE:
    Sets up AgentCore Memory and Identity resources.

USAGE:
    python scripts/setup_agentcore_resources.py [--create-memory] [--memory-name NAME]

OPTIONS:
    --create-memory: Create Memory resource (default: False, Memory created by agentcore launch)
    --memory-name NAME: Custom Memory resource name (default: cloud-engineer-agent-memory)
    --enable-ltm: Enable Long-Term Memory (default: True)

WHAT THIS SCRIPT DOES:
    1. Creates Workload Identity (always)
    2. Optionally creates Memory resource (if --create-memory flag used)
    3. Updates .env file with ARNs
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
from identity.workload_identity_manager import create_workload_identity

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Setup AgentCore Memory and Identity resources'
    )
    parser.add_argument(
        '--create-memory',
        action='store_true',
        help='Create Memory resource (default: False, Memory created by agentcore launch)'
    )
    parser.add_argument(
        '--memory-name',
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
    
    logger.info("🚀 Setting up AgentCore resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    
    try:
        # Create workload identity
        logger.info("📋 Creating Workload Identity...")
        identity_result = create_workload_identity(
            name="cloud-engineer-agent-workload-identity",
            description="Workload identity for Cloud Engineer Agent Runtime"
        )
        
        # Update .env file with identity
        set_key('.env', 'WORKLOAD_IDENTITY_NAME', identity_result['identity_name'])
        logger.info(f"✅ Workload Identity created: {identity_result['identity_arn']}")
        
        # Optionally create Memory resource
        if args.create_memory:
            logger.info("📋 Creating Memory resource...")
            try:
                from memory.memory_resource_manager import create_memory_resource
                
                enable_ltm = args.enable_ltm and not args.disable_ltm
                memory_result = create_memory_resource(
                    name=args.memory_name,
                    description=f"Memory resource for Cloud Engineer Agent",
                    enable_ltm=enable_ltm
                )
                
                # Update .env file with Memory details
                if memory_result.get('memory_arn'):
                    set_key('.env', 'MEMORY_RESOURCE_ARN', memory_result['memory_arn'])
                if memory_result.get('memory_id'):
                    set_key('.env', 'MEMORY_RESOURCE_ID', memory_result['memory_id'])
                
                logger.info(f"✅ Memory resource created!")
                logger.info(f"   Memory ID: {memory_result['memory_id']}")
                logger.info(f"   Memory ARN: {memory_result['memory_arn']}")
                logger.info(f"   Status: {memory_result['status']}")
                logger.info(f"   Strategies: {', '.join(memory_result.get('strategies', []))}")
                
            except ImportError as e:
                logger.error(f"❌ Failed to import Memory manager: {e}")
                logger.info("   💡 Install bedrock-agentcore-starter-toolkit:")
                logger.info("      pip install bedrock-agentcore-starter-toolkit")
                return 1
            except Exception as e:
                logger.error(f"❌ Failed to create Memory resource: {e}")
                logger.info("   💡 Memory will be created automatically by 'agentcore launch'")
                logger.info("   💡 You can skip --create-memory flag and let agentcore launch handle it")
        else:
            logger.info("💡 Memory resource creation skipped (use --create-memory to create)")
            logger.info("   Memory will be created automatically by 'agentcore launch'")
        
        logger.info("✅ AgentCore resources setup complete!")
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to setup resources: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

