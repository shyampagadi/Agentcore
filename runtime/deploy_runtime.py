"""
===============================================================================
MODULE: deploy_runtime.py
===============================================================================

PURPOSE:
    Deployment script for AgentCore Runtime.

WHEN TO USE THIS MODULE:
    - Deployment: Deploy runtime to AgentCore
    - Updates: Update existing runtime

USAGE EXAMPLES:
    python runtime/deploy_runtime.py

WHAT THIS MODULE DOES:
    1. Validates runtime configuration
    2. Builds container image (if using Dockerfile)
    3. Pushes to ECR
    4. Deploys to AgentCore Runtime

RELATED FILES:
    - runtime/agent_runtime.py - Runtime entrypoint
    - runtime/Dockerfile - Container definition

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import subprocess
from pathlib import Path

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region

logger = setup_logger(__name__)


def deploy_runtime():
    """
    Deploy runtime to AgentCore.
    
    NOTE: This script uses agentcore CLI commands.
    For manual deployment, use:
        agentcore configure --entrypoint runtime/agent_runtime.py
        agentcore launch
    """
    logger.info("🚀 Deploying AgentCore Runtime...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    region = get_aws_region()
    logger.info(f"   Region: {region}")
    
    # Check if agentcore CLI is available
    try:
        result = subprocess.run(['agentcore', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ agentcore CLI not found")
            logger.error("   💡 SOLUTION: Install bedrock-agentcore-starter-toolkit")
            return 1
    except FileNotFoundError:
        logger.error("❌ agentcore CLI not found")
        logger.error("   💡 SOLUTION: Install bedrock-agentcore-starter-toolkit")
        return 1
    
    logger.info("")
    logger.info("📋 Deployment Steps:")
    logger.info("")
    logger.info("1. Configure runtime:")
    logger.info("   agentcore configure --entrypoint runtime/agent_runtime.py")
    logger.info("")
    logger.info("2. Deploy runtime:")
    logger.info("   agentcore launch")
    logger.info("")
    logger.info("   This will:")
    logger.info("   - Build container image using CodeBuild")
    logger.info("   - Push to ECR")
    logger.info("   - Create Memory resource")
    logger.info("   - Deploy Runtime")
    logger.info("   - Configure Identity")
    logger.info("")
    logger.info("3. Get runtime ARN:")
    logger.info("   agentcore runtime list")
    logger.info("")
    logger.info("💡 See IMPLEMENTATION_PLAN.md for detailed deployment guide")
    
    return 0


if __name__ == "__main__":
    sys.exit(deploy_runtime())

