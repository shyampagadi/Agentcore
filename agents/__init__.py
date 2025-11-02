"""
===============================================================================
MODULE: agents/__init__.py
===============================================================================

PURPOSE:
    Package marker for the agents module.
    Provides simple exports for agent-related functionality.

WHAT THIS MODULE DOES:
    - Marks this directory as a Python package
    - Provides convenient imports for agent functionality

USAGE EXAMPLES:
    from agents.cloud_engineer_agent import execute_custom_task, PREDEFINED_TASKS

RELATED FILES:
    - agents/cloud_engineer_agent.py - Main cloud engineer agent

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# Export main agent functions for convenience
from agents.cloud_engineer_agent import (
    execute_custom_task,
    execute_predefined_task,
    get_predefined_tasks,
    PREDEFINED_TASKS,
    mcp_initialized,
    get_mcp_status,
    get_detailed_mcp_status
)

__all__ = [
    'execute_custom_task',
    'execute_predefined_task',
    'get_predefined_tasks',
    'PREDEFINED_TASKS',
    'mcp_initialized',
    'get_mcp_status',
    'get_detailed_mcp_status',
]

