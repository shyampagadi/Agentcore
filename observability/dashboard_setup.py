"""
===============================================================================
MODULE: dashboard_setup.py
===============================================================================

PURPOSE:
    Sets up CloudWatch dashboards for monitoring.

WHEN TO USE THIS MODULE:
    - Monitoring setup: Create dashboards
    - Observability: Configure monitoring

USAGE EXAMPLES:
    from observability.dashboard_setup import create_dashboard
    
    create_dashboard()

WHAT THIS MODULE DOES:
    1. Creates CloudWatch dashboards
    2. Configures metrics widgets
    3. Sets up alarms

RELATED FILES:
    - observability/metrics_collector.py - Metrics collection

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import boto3
from typing import Dict, Any

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


def create_dashboard(dashboard_name: str = "CloudEngineerAgent") -> Dict[str, Any]:
    """
    Create CloudWatch dashboard.
    
    ARGUMENTS:
        dashboard_name (str): Dashboard name
    
    RETURNS:
        Dict[str, Any]: Dashboard creation result
    """
    region = get_aws_region()
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["CloudEngineerAgent", "agent_invocations"],
                        [".", "agent_errors"],
                        [".", "agent_response_time"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": region,
                    "title": "Agent Metrics"
                }
            }
        ]
    }
    
    try:
        response = cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=str(dashboard_body).replace("'", '"')
        )
        
        logger.info(f"✅ Dashboard created: {dashboard_name}")
        return response
    
    except Exception as e:
        logger.error(f"❌ Failed to create dashboard: {e}")
        raise

