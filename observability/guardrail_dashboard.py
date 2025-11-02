"""
===============================================================================
MODULE: guardrail_dashboard.py
===============================================================================

PURPOSE:
    Creates dashboard for guardrail monitoring.

WHEN TO USE THIS MODULE:
    - Guardrail monitoring: Track violations
    - Compliance: Monitor content safety

USAGE EXAMPLES:
    from observability.guardrail_dashboard import create_guardrail_dashboard
    
    create_guardrail_dashboard()

WHAT THIS MODULE DOES:
    1. Creates guardrail-specific dashboard
    2. Tracks violations
    3. Monitors compliance metrics

RELATED FILES:
    - guardrails/guardrail_monitor.py - Violation monitoring

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


def create_guardrail_dashboard(dashboard_name: str = "GuardrailMonitoring") -> Dict[str, Any]:
    """
    Create guardrail monitoring dashboard.
    
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
                        ["CloudEngineerAgent", "guardrail_violations"],
                        [".", "guardrail_blocks"],
                        [".", "guardrail_checks"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": region,
                    "title": "Guardrail Metrics"
                }
            }
        ]
    }
    
    try:
        response = cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=str(dashboard_body).replace("'", '"')
        )
        
        logger.info(f"✅ Guardrail dashboard created: {dashboard_name}")
        return response
    
    except Exception as e:
        logger.error(f"❌ Failed to create guardrail dashboard: {e}")
        raise

