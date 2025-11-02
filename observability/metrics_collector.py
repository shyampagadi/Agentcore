"""
===============================================================================
MODULE: metrics_collector.py
===============================================================================

PURPOSE:
    Collects custom metrics for monitoring.

WHEN TO USE THIS MODULE:
    - Metrics collection: Collect custom metrics
    - Monitoring: Track application metrics

USAGE EXAMPLES:
    from observability.metrics_collector import record_metric
    
    record_metric("agent_invocations", 1, {"session_id": "session-123"})

WHAT THIS MODULE DOES:
    1. Records custom metrics
    2. Sends metrics to CloudWatch
    3. Tracks application performance

RELATED FILES:
    - observability/otel_config.py - OpenTelemetry configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import boto3
from typing import Dict, Any, Optional

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


def record_metric(
    metric_name: str,
    value: float,
    dimensions: Optional[Dict[str, str]] = None
) -> None:
    """
    Record custom metric.
    
    ARGUMENTS:
        metric_name (str): Metric name
        value (float): Metric value
        dimensions (Optional[Dict[str, str]]): Metric dimensions
    """
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=get_aws_region())
        
        cloudwatch.put_metric_data(
            Namespace='CloudEngineerAgent',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Dimensions': [
                    {'Name': k, 'Value': v}
                    for k, v in (dimensions or {}).items()
                ]
            }]
        )
        
        logger.debug(f"Metric recorded: {metric_name}={value}")
    except Exception as e:
        logger.error(f"Failed to record metric: {e}")

