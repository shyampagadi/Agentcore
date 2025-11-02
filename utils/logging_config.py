"""
===============================================================================
MODULE: logging_config.py
===============================================================================

PURPOSE:
    Provides centralized logging configuration for the entire application.
    This module ensures consistent logging format and behavior across all
    scripts and modules.

WHEN TO USE THIS MODULE:
    - Import at the start of any script or module that needs logging
    - Use instead of creating new loggers manually
    - Ensures consistent log format across the entire application

USAGE EXAMPLES:
    # Basic usage in any script
    from utils.logging_config import setup_logger
    
    logger = setup_logger(__name__)
    logger.info("This is an info message")
    logger.error("This is an error message")

    # Advanced usage with custom log level
    logger = setup_logger(__name__, log_level=logging.DEBUG)

WHAT THIS MODULE DOES:
    1. Creates logger instances with consistent formatting
    2. Configures log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    3. Sets up console handlers with colored output
    4. Provides file logging capability (optional)
    5. Ensures all logs follow the same format

OUTPUTS:
    - Console: Formatted log messages with timestamps
    - File (optional): Log file with all messages

TROUBLESHOOTING:
    - "No module named 'utils'": Add parent directory to PYTHONPATH or use sys.path
    - "Logs not appearing": Check log level configuration
    - "Too many logs": Adjust log level in .env file or code

RELATED FILES:
    - .env - LOG_LEVEL configuration
    - All other modules - Import this for logging

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import logging
import sys
import os
from typing import Optional
from pathlib import Path

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
# No third-party imports needed for basic logging

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Default log format - includes timestamp, logger name, level, and message
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Default date format for timestamps
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Default log level (can be overridden by environment variable)
DEFAULT_LOG_LEVEL = logging.INFO

# Log file directory (if file logging is enabled)
LOG_DIR = Path("logs")

# ============================================================================
# LOGGING SETUP
# ============================================================================

# Create logs directory if it doesn't exist
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(
    name: str,
    log_level: Optional[int] = None,
    log_to_file: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Create and configure a logger instance.
    
    This function creates a logger with consistent formatting and configuration.
    It sets up console output by default, and optionally file output.
    
    WHAT HAPPENS WHEN YOU CALL THIS:
        1. Creates logger instance with given name
        2. Sets log level from parameter or environment variable
        3. Configures console handler with formatted output
        4. Optionally configures file handler
        5. Returns configured logger ready to use
    
    ARGUMENTS:
        name (str): Logger name (usually __name__ of calling module)
            Example: "scripts.create_cognito_pool"
            Convention: Use module path (e.g., "utils.logging_config")
        
        log_level (Optional[int]): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            Default: None (uses environment variable or DEFAULT_LOG_LEVEL)
            Values: logging.DEBUG, logging.INFO, logging.WARNING, etc.
            Example: logging.DEBUG (for verbose output)
        
        log_to_file (bool): Whether to also log to file
            Default: False (only console output)
            True: Creates log file in logs/ directory
        
        log_file (Optional[str]): Custom log file name
            Default: None (uses {name}.log)
            Example: "cognito_operations.log"
            Only used if log_to_file=True
    
    RETURNS:
        logging.Logger: Configured logger instance ready to use
    
    RAISES:
        ValueError: If name is empty or invalid
        OSError: If log directory cannot be created
    
    EXAMPLE:
        >>> from utils.logging_config import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
        2025-01-15 10:30:45 - __main__ - INFO - Application started
        
        >>> # With debug level
        >>> logger = setup_logger(__name__, log_level=logging.DEBUG)
        >>> logger.debug("Debug message")
        2025-01-15 10:30:45 - __main__ - DEBUG - Debug message
        
        >>> # With file logging
        >>> logger = setup_logger(__name__, log_to_file=True)
        >>> # Logs will appear in console AND logs/__main__.log file
    
    NOTES:
        - Logger name should match module path for easy debugging
        - Log level can be set via LOG_LEVEL environment variable
        - File logging appends to existing log files
        - Console output uses standard format (no colors by default)
    """
    # Validate input
    if not name or not isinstance(name, str):
        raise ValueError("Logger name must be a non-empty string")
    
    # Get log level from parameter, environment variable, or default
    if log_level is None:
        # Try to get from environment variable
        env_log_level = os.getenv('LOG_LEVEL', '').upper()
        
        # Map string to logging constant
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level = log_level_map.get(env_log_level, DEFAULT_LOG_LEVEL)
    
    # Create logger instance
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        # Logger already configured, just update level
        logger.setLevel(log_level)
        return logger
    
    # Set logger level
    logger.setLevel(log_level)
    
    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False
    
    # Create formatter - defines how log messages look
    formatter = logging.Formatter(
        fmt=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT
    )
    
    # ========================================================================
    # CONSOLE HANDLER (Always added)
    # ========================================================================
    # Console handler outputs logs to terminal/console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ========================================================================
    # FILE HANDLER (Optional)
    # ========================================================================
    # File handler outputs logs to file (useful for debugging and audit)
    if log_to_file:
        # Determine log file name
        if log_file is None:
            # Use sanitized logger name as filename
            # Replace dots and slashes with underscores
            safe_name = name.replace('.', '_').replace('/', '_')
            log_file = LOG_DIR / f"{safe_name}.log"
        else:
            log_file = LOG_DIR / log_file
        
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file handler (append mode)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"📝 Logging to file: {log_file}")
    
    return logger


def get_log_level_from_env() -> int:
    """
    Get log level from environment variable.
    
    Reads LOG_LEVEL from environment and converts to logging constant.
    Useful for configuration-based log level management.
    
    RETURNS:
        int: Logging level constant (e.g., logging.INFO)
    
    EXAMPLE:
        >>> level = get_log_level_from_env()
        >>> logger.setLevel(level)
    """
    env_log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    log_level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return log_level_map.get(env_log_level, DEFAULT_LOG_LEVEL)


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    """
    Test the logging configuration.
    
    Run this file directly to test logging setup:
        python utils/logging_config.py
    """
    # Create test logger
    test_logger = setup_logger(__name__, log_level=logging.DEBUG)
    
    # Test all log levels
    test_logger.debug("🐛 This is a DEBUG message")
    test_logger.info("✅ This is an INFO message")
    test_logger.warning("⚠️  This is a WARNING message")
    test_logger.error("❌ This is an ERROR message")
    test_logger.critical("💥 This is a CRITICAL message")
    
    print("\n" + "="*70)
    print("Logging configuration test complete!")
    print("="*70)

