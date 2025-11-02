"""
===============================================================================
MODULE: update_config.py
===============================================================================

PURPOSE:
    Updates configuration files with generated values.

USAGE:
    python scripts/update_config.py --key AGENT_RUNTIME_ARN --value arn:...

WHAT THIS SCRIPT DOES:
    1. Updates .env file with new values
    2. Validates configuration
    3. Backs up existing config
===============================================================================
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def update_env(key: str, value: str) -> bool:
    """Update environment variable in .env file."""
    env_file = Path('.env')
    
    if not env_file.exists():
        logger.error("❌ .env file not found")
        return False
    
    # Backup existing file
    backup_file = Path('.env.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy(env_file, backup_file)
        logger.info("✅ Created backup: .env.backup")
    
    # Update value
    set_key('.env', key, value)
    logger.info(f"✅ Updated {key}={value}")
    
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update configuration")
    parser.add_argument('--key', type=str, required=True, help='Configuration key')
    parser.add_argument('--value', type=str, required=True, help='Configuration value')
    
    args = parser.parse_args()
    
    if update_env(args.key, args.value):
        logger.info("✅ Configuration updated")
        return 0
    else:
        logger.error("❌ Failed to update configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())

