"""
===============================================================================
MODULE: cloudwatch_setup.py
===============================================================================

PURPOSE:
    Sets up CloudWatch logging and monitoring.

WHEN TO USE THIS MODULE:
    - Observability setup: Configure CloudWatch
    - Logging: Set up log groups

USAGE EXAMPLES:
    from observability.cloudwatch_setup import setup_log_group
    
    setup_log_group("cloud-engineer-agent")

WHAT THIS MODULE DOES:
    1. Creates log groups
    2. Configures log retention
    3. Sets up log streams

RELATED FILES:
    - observability/otel_config.py - OpenTelemetry configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import boto3
from typing import Optional

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


def setup_log_group(log_group_name: str, retention_days: int = 7) -> bool:
    """
    Setup CloudWatch log group.
    
    ARGUMENTS:
        log_group_name (str): Log group name
        retention_days (int): Retention period in days
    
    RETURNS:
        bool: True if successful
    """
    region = get_aws_region()
    logs_client = boto3.client('logs', region_name=region)
    
    try:
        # Create log group if it doesn't exist
        try:
            logs_client.create_log_group(logGroupName=log_group_name)
            logger.info(f"✅ Created log group: {log_group_name}")
        except logs_client.exceptions.ResourceAlreadyExistsException:
            logger.debug(f"Log group already exists: {log_group_name}")
        
        # Set retention policy
        logs_client.put_retention_policy(
            logGroupName=log_group_name,
            retentionInDays=retention_days
        )
        
        logger.info(f"✅ Configured retention: {retention_days} days")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to setup log group: {e}")
        return False

