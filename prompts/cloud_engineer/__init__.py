"""
===============================================================================
MODULE: prompts/cloud_engineer/__init__.py
===============================================================================

PURPOSE:
    Package marker for cloud engineer agent prompts.
    Provides simple exports for cloud engineer prompt functionality.

WHAT THIS MODULE DOES:
    - Marks this directory as a Python package
    - Provides convenient imports for cloud engineer prompts

USAGE EXAMPLES:
    from prompts.cloud_engineer import get_system_prompt, PREDEFINED_TASKS

RELATED FILES:
    - prompts/cloud_engineer/system_prompt.py - System prompt
    - prompts/cloud_engineer/predefined_tasks.py - Predefined tasks

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# Export cloud engineer prompt functions
from prompts.cloud_engineer.system_prompt import get_system_prompt
from prompts.cloud_engineer.predefined_tasks import PREDEFINED_TASKS

__all__ = [
    'get_system_prompt',
    'PREDEFINED_TASKS',
]

