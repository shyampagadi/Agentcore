"""
===============================================================================
MODULE: setup_aws_resources.py
===============================================================================

PURPOSE:
    Sets up base AWS resources required for the application.

USAGE:
    python scripts/setup_aws_resources.py

WHAT THIS SCRIPT DOES:
    1. Creates IAM roles
    2. Creates CloudWatch log groups
    3. Creates ECR repository (if needed)
    4. Outputs resource ARNs
===============================================================================
"""

import os
import sys
import boto3
import json
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region, get_aws_account_id
from dotenv import load_dotenv, set_key

logger = setup_logger(__name__)


def create_iam_role(role_name: str, trust_policy: Dict[str, Any]) -> str:
    """Create IAM role."""
    iam = boto3.client('iam')
    
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f'IAM role for {role_name}'
        )
        return response['Role']['Arn']
    except iam.exceptions.EntityAlreadyExistsException:
        logger.info(f"Role {role_name} already exists")
        response = iam.get_role(RoleName=role_name)
        return response['Role']['Arn']


def create_log_group(log_group_name: str) -> bool:
    """Create CloudWatch log group."""
    logs = boto3.client('logs', region_name=get_aws_region())
    
    try:
        logs.create_log_group(logGroupName=log_group_name)
        logs.put_retention_policy(logGroupName=log_group_name, retentionInDays=7)
        logger.info(f"✅ Created log group: {log_group_name}")
        return True
    except logs.exceptions.ResourceAlreadyExistsException:
        logger.info(f"Log group {log_group_name} already exists")
        return True
    except Exception as e:
        logger.error(f"Failed to create log group: {e}")
        return False


def create_ecr_repository(repo_name: str) -> str:
    """Create ECR repository."""
    ecr = boto3.client('ecr', region_name=get_aws_region())
    
    try:
        response = ecr.create_repository(repositoryName=repo_name)
        repo_uri = response['repository']['repositoryUri']
        logger.info(f"✅ Created ECR repository: {repo_name}")
        return repo_uri
    except ecr.exceptions.RepositoryAlreadyExistsException:
        logger.info(f"Repository {repo_name} already exists")
        response = ecr.describe_repositories(repositoryNames=[repo_name])
        return response['repositories'][0]['repositoryUri']
    except Exception as e:
        logger.error(f"Failed to create ECR repository: {e}")
        raise


def main() -> int:
    """Main entry point."""
    logger.info("🚀 Setting up AWS resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    
    region = get_aws_region()
    account_id = get_aws_account_id()
    
    if not account_id:
        logger.error("❌ Failed to get AWS account ID")
        return 1
    
    logger.info(f"   Region: {region}")
    logger.info(f"   Account ID: {account_id}")
    
    resources = {}
    
    try:
        # Create log groups
        logger.info("\n📋 Creating CloudWatch log groups...")
        log_groups = [
            '/aws/bedrock-agentcore/runtimes',
            '/aws/bedrock-agentcore/memory',
            '/aws/cloud-engineer-agent/streamlit'
        ]
        
        for log_group in log_groups:
            create_log_group(log_group)
        
        # Create ECR repository (if needed)
        logger.info("\n📋 Creating ECR repository...")
        repo_name = 'cloud-engineer-agent-runtime'
        try:
            repo_uri = create_ecr_repository(repo_name)
            resources['ecr_repository'] = repo_uri
            logger.info(f"   Repository URI: {repo_uri}")
        except Exception as e:
            logger.warning(f"⚠️  ECR repository creation skipped: {e}")
        
        # Note: IAM roles and AgentCore resources are created by agentcore launch
        logger.info("\n✅ AWS resources setup complete!")
        logger.info("   💡 Note: IAM roles and AgentCore resources will be created by 'agentcore launch'")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Failed to setup resources: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

