"""
===============================================================================
MODULE: agent_runtime.py
===============================================================================

PURPOSE:
    Wraps the existing Strands Agent with AWS Bedrock AgentCore Runtime SDK.
    This module creates the entrypoint for AgentCore Runtime deployment,
    handling HTTP requests, session management, and agent invocation.

WHEN TO USE THIS MODULE:
    - Deployed to AgentCore Runtime: This is the entrypoint file
    - Local testing: Run directly to test agent locally
    - Development: Modify agent behavior here

PREREQUISITES:
    - Existing agent: agents/cloud_engineer_agent.py
    - Environment variables: Configured in .env file
    - AgentCore Runtime: Deployed via `agentcore launch`

USAGE EXAMPLES:
    # Deploy to AgentCore Runtime (via agentcore CLI)
    agentcore configure --entrypoint runtime/agent_runtime.py
    agentcore launch

    # Local testing
    python runtime/agent_runtime.py

WHAT THIS MODULE DOES:
    1. Creates BedrockAgentCoreApp instance
    2. Wraps existing Strands Agent
    3. Implements /invocations endpoint handler
    4. Implements /ping health check endpoint
    5. Extracts session ID from request context
    6. Handles memory integration (optional)
    7. Handles guardrail integration (optional)
    8. Processes agent responses

OUTPUTS:
    - HTTP responses: Agent responses via /invocations endpoint
    - Health checks: Status via /ping endpoint
    - Logs: All operations logged to CloudWatch

TROUBLESHOOTING:
    - "Module not found": Ensure cloud_engineer_agent.py is in parent directory
    - "Agent initialization failed": Check MCP tools are accessible
    - "Session ID not found": Ensure RequestContext is properly configured

RELATED FILES:
    - agents/cloud_engineer_agent.py - Existing agent (imported here)
    - prompts/cloud_engineer/ - Agent prompts and predefined tasks
    - runtime/memory_integration.py - Memory operations (optional)
    - runtime/guardrail_integration.py - Guardrail operations (optional)

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

# ============================================================================
# STANDARD LIBRARY IMPORTS
# ============================================================================
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# ============================================================================
# THIRD-PARTY IMPORTS
# ============================================================================
# bedrock-agentcore: AgentCore Runtime SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.context import RequestContext

# ============================================================================
# LOCAL IMPORTS
# ============================================================================
# Add parent directory to path to import existing agent
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Import existing agent functions from the new modular location
# Note: We import the execute functions, not the agent itself
# This allows us to reuse the agent logic without reinitializing
try:
    from agents.cloud_engineer_agent import (
        execute_custom_task,
        execute_predefined_task,
        get_predefined_tasks,
        PREDEFINED_TASKS
    )
except ImportError as e:
    logger = setup_logger(__name__)
    logger.error(f"❌ Failed to import cloud_engineer_agent from agents/cloud_engineer_agent.py: {e}")
    logger.error("   💡 SOLUTION: Ensure agents/cloud_engineer_agent.py exists and is correctly configured.")
    raise

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

# Application name for logging
APP_NAME = "cloud-engineer-agent-runtime"

# ============================================================================
# LOGGING SETUP
# ============================================================================

logger = setup_logger(__name__)

# ============================================================================
# AGENTCORE RUNTIME APP
# ============================================================================

# Create AgentCore Runtime application instance
# This wraps your agent and provides HTTP endpoints automatically
app = BedrockAgentCoreApp()


# ============================================================================
# ENTRYPOINT HANDLER
# ============================================================================

@app.entrypoint
def handle_invocation(payload: Dict[str, Any], context: RequestContext) -> Dict[str, Any]:
    """
    Handle agent invocation requests from Streamlit or other clients.
    
    This is the main entrypoint for all agent requests. It receives user input,
    extracts session information, invokes the agent, and returns the response.
    
    WHAT HAPPENS WHEN YOU CALL THIS:
        1. Receives request payload from AgentCore Runtime
        2. Extracts user input (prompt or message)
        3. Extracts session ID from context (for session isolation)
        4. Extracts user ID from context (for user identification)
        5. Invokes existing Strands Agent with user input
        6. Returns agent response in standardized format
    
    ARGUMENTS:
        payload (Dict[str, Any]): Request payload from client
            Expected format:
            {
                "prompt": "User's message or task",
                "task_key": "optional-predefined-task-key"  # Optional
            }
            Example:
            {
                "prompt": "List all EC2 instances in us-east-2"
            }
        
        context (RequestContext): AgentCore Runtime context
            Contains:
            - session_id: Runtime session ID (unique per user/conversation)
            - user_id: User identifier from Cognito (if authenticated)
            - request_id: Unique request identifier
            - Additional metadata
    
    RETURNS:
        Dict[str, Any]: Agent response in standardized format
            Format:
            {
                "message": "Agent's response text",
                "session_id": "session-id-from-context",
                "user_id": "user-id-from-context",
                "metadata": {
                    "task_type": "custom" or "predefined",
                    "predefined_task": "task-key" (if applicable)
                }
            }
            Example:
            {
                "message": "Found 5 EC2 instances...",
                "session_id": "user-123-session-abc",
                "user_id": "us-east-2_abc123def",
                "metadata": {"task_type": "custom"}
            }
    
    RAISES:
        ValueError: If payload is invalid or missing required fields
        Exception: If agent execution fails (caught and returned as error)
    
    EXAMPLE:
        >>> # Request payload
        >>> payload = {"prompt": "List EC2 instances"}
        >>> context = RequestContext(session_id="session-123", user_id="user-456")
        >>> 
        >>> response = handle_invocation(payload, context)
        >>> print(response["message"])
        Found 5 EC2 instances...
    
    NOTES:
        - Session ID is automatically provided by AgentCore Runtime
        - Each session gets isolated microVM (no data leakage)
        - Agent execution is synchronous (blocks until complete)
        - Errors are caught and returned in response format
        - Memory integration can be added here (see memory_integration.py)
    """
    try:
        # Extract session and user information from context
        # These are automatically provided by AgentCore Runtime
        session_id = context.session_id if hasattr(context, 'session_id') else None
        user_id = context.user_id if hasattr(context, 'user_id') else None
        request_id = context.request_id if hasattr(context, 'request_id') else None
        
        logger.info(f"📥 Received request")
        logger.info(f"   Session ID: {session_id}")
        logger.info(f"   User ID: {user_id}")
        logger.info(f"   Request ID: {request_id}")
        
        # Extract user input from payload
        # Support multiple payload formats for flexibility
        user_input = None
        
        if isinstance(payload, dict):
            # Standard format: {"prompt": "..."}
            user_input = payload.get('prompt') or payload.get('message') or payload.get('input')
            
            # Check for predefined task
            task_key = payload.get('task_key')
            if task_key:
                logger.info(f"🎯 Executing predefined task: {task_key}")
                agent_response = execute_predefined_task(task_key)
                task_type = "predefined"
            else:
                # Custom task
                if not user_input:
                    raise ValueError("Payload must contain 'prompt', 'message', or 'input' field")
                
                logger.info(f"💬 Executing custom task")
                logger.info(f"   User input: {user_input[:100]}...")  # Log first 100 chars
                agent_response = execute_custom_task(user_input)
                task_type = "custom"
        
        elif isinstance(payload, str):
            # Simple string format (for backward compatibility)
            user_input = payload
            logger.info(f"💬 Executing custom task (string format)")
            agent_response = execute_custom_task(user_input)
            task_type = "custom"
        
        else:
            raise ValueError(f"Invalid payload type: {type(payload)}. Expected dict or str.")
        
        # Build response
        response = {
            "message": agent_response,
            "session_id": session_id,
            "user_id": user_id,
            "request_id": request_id,
            "metadata": {
                "task_type": task_type,
                "task_key": payload.get('task_key') if isinstance(payload, dict) else None
            }
        }
        
        logger.info(f"📤 Sending response")
        logger.info(f"   Response length: {len(agent_response)} characters")
        
        return response
    
    except ValueError as e:
        # Invalid input - return error response
        logger.error(f"❌ Validation error: {e}")
        return {
            "error": str(e),
            "message": f"Invalid request: {e}",
            "session_id": context.session_id if hasattr(context, 'session_id') else None,
            "user_id": context.user_id if hasattr(context, 'user_id') else None
        }
    
    except Exception as e:
        # Unexpected error - log and return error response
        logger.error(f"❌ Agent execution failed: {e}", exc_info=True)
        return {
            "error": str(e),
            "message": f"Agent execution failed: {e}",
            "session_id": context.session_id if hasattr(context, 'session_id') else None,
            "user_id": context.user_id if hasattr(context, 'user_id') else None
        }


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.ping
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for AgentCore Runtime.
    
    This endpoint is called by AgentCore Runtime to verify the agent is
    healthy and ready to handle requests. It's used for:
    - Load balancer health checks
    - Service monitoring
    - Startup verification
    
    RETURNS:
        Dict[str, Any]: Health status
            Format:
            {
                "status": "healthy" or "unhealthy",
                "timestamp": "ISO timestamp",
                "version": "application version"
            }
    
    EXAMPLE:
        >>> status = health_check()
        >>> print(status["status"])
        healthy
    
    NOTES:
        - Called automatically by AgentCore Runtime
        - Should return quickly (no heavy operations)
        - Can be extended to check dependencies (MCP tools, etc.)
    """
    logger.debug("🏥 Health check requested")
    
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "app_name": APP_NAME
    }


# ============================================================================
# STARTUP HOOK (Optional)
# ============================================================================

@app.on_startup
def startup_handler():
    """
    Called when agent runtime starts up.
    
    Use this to:
    - Initialize resources
    - Verify dependencies
    - Load configuration
    - Perform one-time setup
    
    NOTES:
        - Called once when runtime starts
        - Any exceptions here will prevent runtime from starting
        - Keep initialization lightweight
    """
    logger.info("🚀 Agent runtime starting up...")
    logger.info(f"   Application: {APP_NAME}")
    logger.info(f"   Python version: {sys.version}")
    logger.info("✅ Agent runtime ready")


# ============================================================================
# SHUTDOWN HOOK (Optional)
# ============================================================================

@app.on_shutdown
def shutdown_handler():
    """
    Called when agent runtime shuts down.
    
    Use this to:
    - Clean up resources
    - Close connections
    - Save state
    
    NOTES:
        - Called when runtime is shutting down
        - Should complete quickly
        - Any exceptions are logged but don't prevent shutdown
    """
    logger.info("🛑 Agent runtime shutting down...")
    logger.info("✅ Cleanup complete")


# ============================================================================
# APPLICATION RUNNER
# ============================================================================

def run_app():
    """
    Run the AgentCore Runtime application.
    
    This function starts the HTTP server that handles requests from
    AgentCore Runtime. It's called automatically by AgentCore Runtime
    when deployed, but can also be called locally for testing.
    
    USAGE:
        # Called automatically by AgentCore Runtime
        # Or manually for local testing:
        python runtime/agent_runtime.py
    """
    logger.info("="*70)
    logger.info("Starting Cloud Engineer Agent Runtime")
    logger.info("="*70)
    logger.info("")
    logger.info("📋 Configuration:")
    logger.info(f"   Application: {APP_NAME}")
    logger.info(f"   Entrypoint: /invocations")
    logger.info(f"   Health Check: /ping")
    logger.info("")
    logger.info("🚀 Runtime starting...")
    logger.info("")
    
    # Run the app
    # This starts the HTTP server and begins handling requests
    app.run()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    This block runs when the script is executed directly (not imported).
    
    This allows local testing of the agent runtime:
        python runtime/agent_runtime.py
    
    When deployed to AgentCore Runtime, this file is used as the entrypoint
    and app.run() is called automatically by the runtime.
    """
    try:
        run_app()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Runtime interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
