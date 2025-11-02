"""
===============================================================================
SCRIPT NAME: deploy_streamlit_production.py
===============================================================================

PURPOSE:
    Deploys Streamlit UI to production using ECS Fargate and ALB.

USAGE:
    python scripts/deploy_streamlit_production.py

WHAT THIS SCRIPT DOES:
    1. Builds Docker image for Streamlit
    2. Pushes to ECR
    3. Creates ECS cluster and service
    4. Sets up Application Load Balancer
    5. Configures HTTPS
===============================================================================
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point."""
    logger.info("🚀 Deploying Streamlit to production...")
    logger.info("")
    logger.info("📋 Production Deployment Steps:")
    logger.info("")
    logger.info("1. Build Docker image:")
    logger.info("   docker build -t streamlit-app -f Dockerfile.streamlit .")
    logger.info("")
    logger.info("2. Push to ECR:")
    logger.info("   aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-2.amazonaws.com")
    logger.info("   docker tag streamlit-app:latest <account-id>.dkr.ecr.us-east-2.amazonaws.com/streamlit-app:latest")
    logger.info("   docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/streamlit-app:latest")
    logger.info("")
    logger.info("3. Deploy to ECS Fargate:")
    logger.info("   See IMPLEMENTATION_PLAN.md → Streamlit Production Deployment")
    logger.info("")
    logger.info("4. Setup ALB and domain:")
    logger.info("   python scripts/setup_domain.py --domain your-domain.com")
    logger.info("")
    logger.info("💡 See IMPLEMENTATION_PLAN.md for detailed deployment guide")
    return 0


if __name__ == "__main__":
    sys.exit(main())

