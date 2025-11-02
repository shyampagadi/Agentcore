"""
===============================================================================
MODULE: session_utils.py
===============================================================================

PURPOSE:
    Provides utility functions for session ID generation and validation.
    This module handles session naming conventions and session ID management
    for AgentCore Memory and Runtime sessions.

WHEN TO USE THIS MODULE:
    - Generating unique session IDs for new conversations
    - Validating session ID format
    - Creating user-friendly session names
    - Sanitizing user input for session names

USAGE EXAMPLES:
    # Generate session ID
    from utils.session_utils import generate_session_id
    
    session_id = generate_session_id(user_id="user-123", description="project-analysis")
    # Result: "user-123-project-analysis-20250115-143022"

    # Validate session ID
    from utils.session_utils import validate_session_id
    
    if validate_session_id(session_id):
        print("Valid session ID")
    else:
        print("Invalid session ID")

WHAT THIS MODULE DOES:
    1. Generates unique session IDs with timestamps
    2. Validates session ID format
    3. Sanitizes user input for session names
    4. Creates user-friendly session names
    5. Formats session IDs consistently

OUTPUTS:
    - Session IDs: Formatted strings ready for use
    - Validation results: Boolean values

TROUBLESHOOTING:
    - "Invalid session ID format": Check session ID follows naming rules
    - "Session ID too long": Use shorter description or enable truncation

RELATED FILES:
    - frontend/session_manager.py - Uses this for session management
    - memory/session_memory_handler.py - Uses this for Memory sessions

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import re
import uuid
from datetime import datetime
from typing import Optional

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
# No third-party imports needed

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
try:
    from utils.logging_config import setup_logger
except ImportError:
    import logging
    def setup_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Maximum session ID length (AWS Cognito/AgentCore limits)
MAX_SESSION_ID_LENGTH = 128

# Minimum session ID length
MIN_SESSION_ID_LENGTH = 1

# Allowed characters in session ID (alphanumeric, hyphens, underscores, dots)
# This matches AWS Cognito and AgentCore naming requirements
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')

# Default session name if none provided
DEFAULT_SESSION_NAME = "session"

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# SESSION ID GENERATION
# ============================================================================

def generate_session_id(
    user_id: str,
    description: Optional[str] = None,
    include_timestamp: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Generate a unique session ID.
    
    Creates a session ID following the naming convention:
    {user_id}-{description}-{timestamp}
    
    This ensures uniqueness while maintaining readability.
    
    WHAT HAPPENS WHEN YOU CALL THIS:
        1. Validates user_id input
        2. Sanitizes description (if provided)
        3. Adds timestamp for uniqueness (if enabled)
        4. Combines components with hyphens
        5. Truncates if exceeds max_length
    
    ARGUMENTS:
        user_id (str): User identifier (e.g., Cognito user ID)
            Example: "us-east-2_abc123def"
            Must be: Non-empty, alphanumeric + hyphens/underscores
        
        description (Optional[str]): Descriptive name for the session
            Default: None (uses DEFAULT_SESSION_NAME)
            Example: "project-analysis" or "vpc-troubleshooting"
            Will be sanitized automatically
        
        include_timestamp (bool): Include timestamp in session ID
            Default: True (ensures uniqueness)
            False: No timestamp (may cause duplicates if same user+description)
        
        max_length (Optional[int]): Maximum session ID length
            Default: None (uses MAX_SESSION_ID_LENGTH)
            Example: 100 (for custom limits)
    
    RETURNS:
        str: Generated session ID
            Format: "{user_id}-{description}-{timestamp}"
            Example: "us-east-2_abc123def-project-analysis-20250115-143022"
    
    RAISES:
        ValueError: If user_id is empty or invalid
    
    EXAMPLE:
        >>> from utils.session_utils import generate_session_id
        >>> session_id = generate_session_id(
        ...     user_id="user-123",
        ...     description="project-analysis"
        ... )
        >>> print(session_id)
        user-123-project-analysis-20250115-143022
        
        >>> # Without timestamp
        >>> session_id = generate_session_id(
        ...     user_id="user-123",
        ...     description="project-analysis",
        ...     include_timestamp=False
        ... )
        >>> print(session_id)
        user-123-project-analysis
    
    NOTES:
        - Session IDs are case-sensitive
        - Timestamp format: YYYYMMDD-HHMMSS (no spaces, no colons)
        - Description is sanitized (special characters removed/replaced)
        - Result is truncated if exceeds max_length
    """
    # Validate user_id
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")
    
    # Sanitize user_id (remove invalid characters)
    user_id = sanitize_session_name(user_id)
    
    # Get description or use default
    if description:
        description = sanitize_session_name(description)
    else:
        description = DEFAULT_SESSION_NAME
    
    # Build session ID components
    components = [user_id, description]
    
    # Add timestamp if requested
    if include_timestamp:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        components.append(timestamp)
    
    # Join components with hyphens
    session_id = '-'.join(components)
    
    # Apply max length limit
    if max_length is None:
        max_length = MAX_SESSION_ID_LENGTH
    
    if len(session_id) > max_length:
        logger.warning(f"⚠️  Session ID exceeds max length ({max_length}), truncating...")
        # Truncate from the end (keep user_id and description, truncate timestamp)
        session_id = session_id[:max_length]
        logger.info(f"   Truncated session ID: {session_id}")
    
    logger.debug(f"Generated session ID: {session_id}")
    return session_id


def sanitize_session_name(name: str) -> str:
    """
    Sanitize session name for use in session ID.
    
    Removes or replaces invalid characters to ensure session ID follows
    AWS naming requirements (alphanumeric, hyphens, underscores, dots).
    
    WHAT HAPPENS WHEN YOU CALL THIS:
        1. Converts to lowercase (for consistency)
        2. Replaces spaces with hyphens
        3. Removes invalid characters
        4. Removes consecutive hyphens/underscores
        5. Trims hyphens/underscores from start/end
    
    ARGUMENTS:
        name (str): Raw session name from user input
            Example: "My Project Analysis!" or "VPC Troubleshooting"
    
    RETURNS:
        str: Sanitized session name
            Example: "my-project-analysis" or "vpc-troubleshooting"
    
    EXAMPLE:
        >>> from utils.session_utils import sanitize_session_name
        >>> sanitized = sanitize_session_name("My Project Analysis!")
        >>> print(sanitized)
        my-project-analysis
        
        >>> sanitized = sanitize_session_name("VPC_Troubleshooting-Session")
        >>> print(sanitized)
        vpc-troubleshooting-session
    """
    if not name:
        return DEFAULT_SESSION_NAME
    
    # Convert to lowercase for consistency
    sanitized = name.lower()
    
    # Replace spaces with hyphens
    sanitized = sanitized.replace(' ', '-')
    
    # Replace underscores with hyphens (standardize separator)
    sanitized = sanitized.replace('_', '-')
    
    # Remove invalid characters (keep only alphanumeric, hyphens, dots)
    sanitized = re.sub(r'[^a-z0-9.-]', '', sanitized)
    
    # Remove consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove consecutive dots
    sanitized = re.sub(r'\.+', '.', sanitized)
    
    # Remove leading/trailing hyphens and dots
    sanitized = sanitized.strip('-.')
    
    # If empty after sanitization, use default
    if not sanitized:
        sanitized = DEFAULT_SESSION_NAME
    
    return sanitized


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Checks if session ID follows AWS naming requirements:
    - Alphanumeric characters
    - Hyphens, underscores, dots allowed
    - Length between MIN and MAX
    
    ARGUMENTS:
        session_id (str): Session ID to validate
            Example: "user-123-project-analysis-20250115-143022"
    
    RETURNS:
        bool: True if valid, False otherwise
            True: Session ID follows naming rules
            False: Session ID invalid (contains invalid characters or wrong length)
    
    EXAMPLE:
        >>> from utils.session_utils import validate_session_id
        >>> if validate_session_id("user-123-project"):
        ...     print("Valid session ID")
        ... else:
        ...     print("Invalid session ID")
        Valid session ID
        
        >>> validate_session_id("user@123#project")  # Invalid characters
        False
    """
    if not session_id or not isinstance(session_id, str):
        return False
    
    # Check length
    if len(session_id) < MIN_SESSION_ID_LENGTH or len(session_id) > MAX_SESSION_ID_LENGTH:
        logger.debug(f"Session ID length invalid: {len(session_id)} (must be {MIN_SESSION_ID_LENGTH}-{MAX_SESSION_ID_LENGTH})")
        return False
    
    # Check pattern (alphanumeric, hyphens, underscores, dots)
    if not SESSION_ID_PATTERN.match(session_id):
        logger.debug(f"Session ID contains invalid characters: {session_id}")
        return False
    
    return True


def generate_uuid_session_id() -> str:
    """
    Generate a UUID-based session ID.
    
    Creates a session ID using UUID v4. This ensures uniqueness but
    is not human-readable. Use when you need guaranteed uniqueness
    and don't need descriptive names.
    
    RETURNS:
        str: UUID-based session ID
            Format: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            Length: 36 characters (with hyphens)
    
    EXAMPLE:
        >>> from utils.session_utils import generate_uuid_session_id
        >>> session_id = generate_uuid_session_id()
        >>> print(session_id)
        a1b2c3d4-e5f6-7890-abcd-ef1234567890
    
    NOTES:
        - UUIDs are guaranteed unique
        - Not human-readable (use generate_session_id for readable IDs)
        - Suitable for system-generated sessions
    """
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated UUID session ID: {session_id}")
    return session_id


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test session utility functions.
    
    Run this file directly to test session utilities:
        python utils/session_utils.py
    """
    print("="*70)
    print("Testing Session Utility Functions")
    print("="*70)
    
    # Test session ID generation
    print("\n1. Testing Session ID Generation:")
    session_id = generate_session_id(
        user_id="user-123",
        description="project-analysis"
    )
    print(f"   Generated: {session_id}")
    
    # Test sanitization
    print("\n2. Testing Session Name Sanitization:")
    test_names = [
        "My Project Analysis!",
        "VPC_Troubleshooting-Session",
        "user@123#project",
        "Normal-Session-Name"
    ]
    for name in test_names:
        sanitized = sanitize_session_name(name)
        print(f"   '{name}' -> '{sanitized}'")
    
    # Test validation
    print("\n3. Testing Session ID Validation:")
    test_ids = [
        "user-123-project-analysis-20250115-143022",  # Valid
        "user@123#project",  # Invalid characters
        "a" * 200,  # Too long
        "user-123-project"  # Valid
    ]
    for test_id in test_ids:
        is_valid = validate_session_id(test_id)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {status}: {test_id[:50]}...")
    
    # Test UUID generation
    print("\n4. Testing UUID Session ID Generation:")
    uuid_id = generate_uuid_session_id()
    print(f"   Generated: {uuid_id}")
    
    print("\n" + "="*70)
    print("Session Utility Functions Test Complete!")
    print("="*70)

