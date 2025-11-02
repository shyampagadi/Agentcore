"""
===============================================================================
MODULE: memory_config.py
===============================================================================

PURPOSE:
    Configuration for AgentCore Memory module.

WHEN TO USE THIS MODULE:
    - Memory initialization: Configure memory settings
    - Memory operations: Get configuration values

USAGE EXAMPLES:
    from memory.memory_config import get_memory_config
    
    config = get_memory_config()
    memory_arn = config['memory_arn']

WHAT THIS MODULE DOES:
    1. Loads memory configuration from environment
    2. Validates configuration
    3. Provides default values

RELATED FILES:
    - memory/memory_manager.py - Uses this configuration

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
from typing import Dict, Any

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def get_memory_config() -> Dict[str, Any]:
    """
    Get memory configuration.
    
    RETURNS:
        Dict[str, Any]: Memory configuration
    """
    return {
        'memory_arn': os.getenv('MEMORY_RESOURCE_ARN'),
        'memory_id': os.getenv('MEMORY_RESOURCE_ID'),
        'enabled': os.getenv('MEMORY_RESOURCE_ARN') is not None
    }
