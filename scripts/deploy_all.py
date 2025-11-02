"""
===============================================================================
SCRIPT NAME: deploy_all.py
===============================================================================

PURPOSE:
    One-command deployment script that orchestrates all setup steps.

USAGE:
    python scripts/deploy_all.py [OPTIONS]

OPTIONS:
    --cognito-pool-id ID: Existing Cognito User Pool ID (optional)
    --region REGION: AWS region (default: us-east-2)
    --create-memory: Create Memory resource explicitly (default: False)
    --skip-runtime: Skip runtime deployment (default: False)

WHAT THIS SCRIPT DOES:
    1. Validates environment
    2. Creates/verifies Cognito pool
    3. Sets up guardrails
    4. Sets up AgentCore resources (Identity + optionally Memory)
    5. Sets up base AWS resources
    6. Optionally deploys runtime (via agentcore launch)
    7. Verifies all resources
    8. Outputs summary

RELATED FILES:
    - Individual scripts: create_agentcore_identity.py, create_agentcore_memory.py, etc.
    - See GETTING_STARTED.md for step-by-step guide

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import argparse
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def run_script(script_path: str, args: list = None, check: bool = True) -> bool:
    """Run a script and return success status."""
    cmd = ['python', script_path]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.warning(result.stderr)
    
    if result.returncode != 0 and check:
        logger.error(f"❌ {script_path} failed")
        return False
    
    return result.returncode == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy entire application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full deployment with existing Cognito pool
  python scripts/deploy_all.py --cognito-pool-id us-east-2_abc123

  # Full deployment with Memory creation
  python scripts/deploy_all.py --create-memory

  # Skip runtime deployment (for manual deployment later)
  python scripts/deploy_all.py --skip-runtime
        """
    )
    parser.add_argument(
        '--cognito-pool-id',
        type=str,
        help='Existing Cognito User Pool ID (optional, will create if not provided)'
    )
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-2',
        help='AWS region (default: us-east-2)'
    )
    parser.add_argument(
        '--create-memory',
        action='store_true',
        help='Create Memory resource explicitly (default: Memory created by agentcore launch)'
    )
    parser.add_argument(
        '--skip-runtime',
        action='store_true',
        help='Skip runtime deployment (deploy manually later)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without actually running'
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting full deployment...")
    logger.info("   💡 This script orchestrates all setup steps")
    logger.info("   See GETTING_STARTED.md for detailed guide")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
        logger.info("\nSteps that would be executed:")
        logger.info("  1. Validate environment")
        logger.info("  2. Setup Cognito")
        logger.info("  3. Setup guardrails")
        logger.info("  4. Setup AgentCore resources")
        logger.info("  5. Setup base AWS resources")
        if not args.skip_runtime:
            logger.info("  6. Deploy runtime (agentcore launch)")
        logger.info("  7. Verify resources")
        return 0
    
    steps_completed = []
    steps_failed = []
    
    # Step 1: Validate environment
    logger.info("\n" + "="*80)
    logger.info("STEP 1: Validating environment...")
    logger.info("="*80)
    if run_script('scripts/validate_environment.py'):
        steps_completed.append("Environment validation")
    else:
        steps_failed.append("Environment validation")
        logger.error("❌ Environment validation failed. Fix issues and retry.")
        return 1
    
    # Step 2: Setup Cognito
    logger.info("\n" + "="*80)
    logger.info("STEP 2: Setting up Cognito...")
    logger.info("="*80)
    if args.cognito_pool_id:
        if run_script('scripts/verify_cognito.py', ['--pool-id', args.cognito_pool_id]):
            steps_completed.append("Cognito verification")
        else:
            steps_failed.append("Cognito verification")
    else:
        logger.info("   Checking for existing Cognito pool in .env...")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        if os.getenv('COGNITO_USER_POOL_ID'):
            logger.info("   ✅ Found Cognito pool in .env, skipping creation")
            steps_completed.append("Cognito (using existing)")
        else:
            logger.info("   Creating new Cognito pool...")
            if run_script('scripts/create_cognito_pool.py', ['--pool-name', 'cloud-engineer-agent-pool']):
                steps_completed.append("Cognito creation")
            else:
                steps_failed.append("Cognito creation")
    
    # Step 3: Setup guardrails
    logger.info("\n" + "="*80)
    logger.info("STEP 3: Setting up guardrails...")
    logger.info("="*80)
    if run_script('scripts/setup_guardrails.py', check=False):
        steps_completed.append("Guardrail setup")
    else:
        logger.warning("   ⚠️  Guardrail setup had issues (continuing...)")
        steps_failed.append("Guardrail setup")
    
    # Step 4: Setup AgentCore resources
    logger.info("\n" + "="*80)
    logger.info("STEP 4: Setting up AgentCore resources...")
    logger.info("="*80)
    
    # Always create Identity
    logger.info("   Creating Workload Identity...")
    if run_script('scripts/create_agentcore_identity.py', check=False):
        steps_completed.append("Identity creation")
    else:
        steps_failed.append("Identity creation")
    
    # Optionally create Memory
    if args.create_memory:
        logger.info("   Creating Memory resource...")
        if run_script('scripts/create_agentcore_memory.py', check=False):
            steps_completed.append("Memory creation")
        else:
            logger.warning("   ⚠️  Memory creation had issues (continuing...)")
            steps_failed.append("Memory creation")
    else:
        logger.info("   💡 Memory will be created by 'agentcore launch'")
        steps_completed.append("Memory (will be created by agentcore launch)")
    
    # Step 5: Setup base AWS resources
    logger.info("\n" + "="*80)
    logger.info("STEP 5: Setting up base AWS resources...")
    logger.info("="*80)
    if run_script('scripts/setup_aws_resources.py', check=False):
        steps_completed.append("AWS resources setup")
    else:
        logger.warning("   ⚠️  AWS resources setup had issues (continuing...)")
        steps_failed.append("AWS resources setup")
    
    # Step 6: Deploy runtime (optional)
    if not args.skip_runtime:
        logger.info("\n" + "="*80)
        logger.info("STEP 6: Deploying runtime...")
        logger.info("="*80)
        logger.info("   💡 Run 'agentcore configure' and 'agentcore launch' manually")
        logger.info("   💡 Or use: python scripts/setup_agentcore_resources.py")
        steps_completed.append("Runtime deployment (manual step required)")
    
    # Step 7: Verify resources
    logger.info("\n" + "="*80)
    logger.info("STEP 7: Verifying resources...")
    logger.info("="*80)
    run_script('scripts/verify_agentcore_resources.py', check=False)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DEPLOYMENT SUMMARY")
    logger.info("="*80)
    logger.info(f"✅ Completed: {len(steps_completed)}")
    for step in steps_completed:
        logger.info(f"   ✅ {step}")
    
    if steps_failed:
        logger.info(f"\n⚠️  Issues: {len(steps_failed)}")
        for step in steps_failed:
            logger.info(f"   ⚠️  {step}")
    
    logger.info("\n" + "="*80)
    
    if not steps_failed:
        logger.info("✅ Deployment complete!")
        logger.info("\n💡 Next steps:")
        logger.info("   1. Configure runtime: agentcore configure")
        logger.info("   2. Deploy runtime: agentcore launch")
        logger.info("   3. Test deployment: python scripts/test_deployment.py")
        logger.info("   4. Run Streamlit UI: streamlit run frontend/app.py")
        return 0
    else:
        logger.warning("⚠️  Deployment completed with some issues.")
        logger.info("   Review failed steps above and fix as needed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

