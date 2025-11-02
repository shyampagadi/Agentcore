"""
===============================================================================
MODULE: guardrail_config.py
===============================================================================

PURPOSE:
    Guardrail configuration definitions.

WHEN TO USE THIS MODULE:
    - Guardrail setup: Get default configurations
    - Content filtering: Configure filter settings

USAGE EXAMPLES:
    from guardrails.guardrail_config import get_default_config
    
    config = get_default_config()

WHAT THIS MODULE DOES:
    1. Defines default guardrail configurations
    2. Provides content filter settings
    3. Defines topic blocking rules

RELATED FILES:
    - guardrails/guardrail_setup.py - Uses this configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

from typing import Dict, Any, List


def get_default_config() -> Dict[str, Any]:
    """
    Get default guardrail configuration.
    
    RETURNS:
        Dict[str, Any]: Default configuration
    """
    return {
        'name': 'cloud-engineer-agent-guardrail',
        'description': 'Guardrail for Cloud Engineer Agent - content safety and compliance',
        'blocked_topics': [
            # Add topics to block if needed
        ],
        'content_filters': {
            # Configure content filters
            'hate': {'filterStrength': 'MEDIUM'},
            'insults': {'filterStrength': 'MEDIUM'},
            'misconduct': {'filterStrength': 'MEDIUM'},
            'promptAttack': {'filterStrength': 'MEDIUM'},
            'violence': {'filterStrength': 'HIGH'},
        },
        'pii_protection': {
            'enabled': True,
            'redact_input': True,
            'redact_output': False  # Allow AWS ARNs and account IDs in output
        }
    }

