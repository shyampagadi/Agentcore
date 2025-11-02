#!/bin/bash
# ============================================================================
# SCRIPT: deploy_all.sh
# ============================================================================
# One-command deployment script (shell version)
# ============================================================================

set -e  # Exit on error

echo "🚀 Starting full deployment..."

# Step 1: Validate environment
echo "Step 1: Validating environment..."
python scripts/validate_environment.py

# Step 2: Setup Cognito
echo "Step 2: Setting up Cognito..."
# python scripts/create_cognito_pool.py --pool-name cloud-engineer-agent-pool

# Step 3: Setup guardrails
echo "Step 3: Setting up guardrails..."
python scripts/setup_guardrails.py

# Step 4: Setup AgentCore resources
echo "Step 4: Setting up AgentCore resources..."
python scripts/setup_agentcore_resources.py

echo "✅ Deployment complete!"

