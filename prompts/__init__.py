"""
===============================================================================
MODULE: prompts/__init__.py
===============================================================================

PURPOSE:
    Package marker for the prompts module.
    Provides simple exports for prompt-related functionality.

WHAT THIS MODULE DOES:
    - Marks this directory as a Python package
    - Provides convenient imports for prompt functionality

USAGE EXAMPLES:
    from prompts.cloud_engineer.system_prompt import get_system_prompt
    from prompts.cloud_engineer.predefined_tasks import PREDEFINED_TASKS

RELATED FILES:
    - prompts/cloud_engineer/ - Cloud engineer agent prompts

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# Export prompt functions for convenience
from prompts.cloud_engineer.system_prompt import get_system_prompt
from prompts.cloud_engineer.predefined_tasks import PREDEFINED_TASKS

__all__ = [
    'get_system_prompt',
    'PREDEFINED_TASKS',
]

