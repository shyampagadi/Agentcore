"""
===============================================================================
MODULE: alarms_setup.py
===============================================================================

PURPOSE:
    Sets up CloudWatch alarms for monitoring.

WHEN TO USE THIS MODULE:
    - Monitoring setup: Create alarms
    - Alerting: Configure notifications

USAGE EXAMPLES:
    from observability.alarms_setup import create_alarm
    
    create_alarm("high-error-rate", threshold=10)

WHAT THIS MODULE DOES:
    1. Creates CloudWatch alarms
    2. Configures thresholds
    3. Sets up SNS notifications

RELATED FILES:
    - observability/metrics_collector.py - Metrics collection

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


def create_alarm(
    alarm_name: str,
    metric_name: str,
    threshold: float,
    sns_topic_arn: Optional[str] = None
) -> bool:
    """
    Create CloudWatch alarm.
    
    ARGUMENTS:
        alarm_name (str): Alarm name
        metric_name (str): Metric name
        threshold (float): Alarm threshold
        sns_topic_arn (Optional[str]): SNS topic ARN for notifications
    
    RETURNS:
        bool: True if successful
    """
    region = get_aws_region()
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    alarm_config = {
        'AlarmName': alarm_name,
        'MetricName': metric_name,
        'Namespace': 'CloudEngineerAgent',
        'Statistic': 'Sum',
        'Period': 300,
        'EvaluationPeriods': 1,
        'Threshold': threshold,
        'ComparisonOperator': 'GreaterThanThreshold'
    }
    
    if sns_topic_arn:
        alarm_config['AlarmActions'] = [sns_topic_arn]
    
    try:
        cloudwatch.put_metric_alarm(**alarm_config)
        logger.info(f"✅ Created alarm: {alarm_name}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to create alarm: {e}")
        return False

