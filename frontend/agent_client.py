"""
===============================================================================
MODULE: agent_client.py
===============================================================================

PURPOSE:
    Client for invoking AgentCore Runtime from Streamlit UI.
    Handles API calls to AgentCore Runtime and manages responses.

WHEN TO USE THIS MODULE:
    - In Streamlit app: Call agent from UI
    - Handle agent responses: Process and display results

USAGE EXAMPLES:
    from frontend.agent_client import AgentCoreClient
    
    client = AgentCoreClient()
    response = client.invoke_agent(
        prompt="List EC2 instances",
        session_id="session-123",
        access_token="jwt-token"
    )

WHAT THIS MODULE DOES:
    1. Creates boto3 client for AgentCore Runtime
    2. Invokes runtime with user prompts
    3. Handles streaming responses
    4. Manages errors and retries
    5. Processes response format

RELATED FILES:
    - frontend/app.py - Uses this client
    - frontend/session_manager.py - Provides session IDs

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import json
import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

from utils.logging_config import setup_logger
from utils.aws_helpers import get_aws_region

logger = setup_logger(__name__)


class AgentCoreClient:
    """
    Client for invoking AgentCore Runtime from Streamlit.
    """
    
    def __init__(self):
        """Initialize AgentCore client."""
        self.runtime_arn = os.getenv('AGENT_RUNTIME_ARN')
        self.region = get_aws_region()
        
        if not self.runtime_arn:
            logger.warning("⚠️  AGENT_RUNTIME_ARN not set. Agent calls will fail.")
        
        self.client = boto3.client('bedrock-agentcore', region_name=self.region)
    
    def invoke_agent(
        self,
        prompt: str,
        session_id: str,
        access_token: Optional[str] = None,
        task_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke AgentCore Runtime with user prompt.
        
        ARGUMENTS:
            prompt (str): User's message/prompt
            session_id (str): Runtime session ID
            access_token (Optional[str]): JWT token from Cognito
            task_key (Optional[str]): Predefined task key
        
        RETURNS:
            Dict[str, Any]: Agent response
        """
        if not self.runtime_arn:
            return {
                'error': 'Agent Runtime ARN not configured',
                'message': 'Please configure AGENT_RUNTIME_ARN in .env file'
            }
        
        try:
            # Prepare payload
            payload = {"prompt": prompt}
            if task_key:
                payload["task_key"] = task_key
            
            payload_bytes = json.dumps(payload).encode('utf-8')
            
            # Invoke runtime
            invoke_params = {
                'agentRuntimeArn': self.runtime_arn,
                'runtimeSessionId': session_id,
                'payload': payload_bytes,
                'qualifier': 'DEFAULT'
            }
            
            # Add access token if provided (for OAuth)
            if access_token:
                invoke_params['accessToken'] = access_token
            
            response = self.client.invoke_agent_runtime(**invoke_params)
            
            # Process streaming response
            content = []
            for chunk in response.get('response', []):
                if isinstance(chunk, bytes):
                    content.append(chunk.decode('utf-8'))
                else:
                    content.append(str(chunk))
            
            # Parse response
            result_str = ''.join(content)
            try:
                result = json.loads(result_str)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                result = {"message": result_str}
            
            logger.info(f"✅ Agent response received for session {session_id}")
            return result
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"❌ Error invoking agent: {error_code} - {error_message}")
            return {
                'error': error_code,
                'message': error_message,
                'session_id': session_id
            }
        
        except Exception as e:
            logger.error(f"❌ Unexpected error invoking agent: {e}", exc_info=True)
            return {
                'error': str(e),
                'message': f'Failed to invoke agent: {e}',
                'session_id': session_id
            }
