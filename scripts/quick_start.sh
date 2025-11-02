#!/bin/bash
# ============================================================================
# SCRIPT: quick_start.sh
# ============================================================================
# Interactive quick start script for developers
# ============================================================================

echo "🚀 Cloud Engineer Agent - Quick Start"
echo "========================================"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI"
    exit 1
fi

echo "✅ AWS CLI found"

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

echo "✅ Virtual environment ready"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"

# Validate environment
echo "🔍 Validating environment..."
python scripts/validate_environment.py

echo ""
echo "✅ Quick start complete!"
echo "Next steps:"
echo "  1. Review IMPLEMENTATION_PLAN.md"
echo "  2. Run: python scripts/create_cognito_pool.py"
echo "  3. Run: python scripts/setup_guardrails.py"
echo "  4. Run: agentcore configure && agentcore launch"

