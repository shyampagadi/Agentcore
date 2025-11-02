"""
===============================================================================
MODULE: memory/memory_resource_manager.py
===============================================================================

PURPOSE:
    Manages AgentCore Memory resource creation and configuration.
    Provides functions to create Memory resources programmatically.

WHEN TO USE THIS MODULE:
    - Before deploying runtime: Create Memory resource separately
    - Automation scripts: Create Memory resources programmatically
    - Resource management: Manage Memory resource lifecycle

USAGE EXAMPLES:
    from memory.memory_resource_manager import create_memory_resource
    
    memory_result = create_memory_resource(
        name="cloud-engineer-agent-memory",
        description="Memory for Cloud Engineer Agent",
        enable_ltm=True
    )
    print(f"Memory ARN: {memory_result['memory_arn']}")

WHAT THIS MODULE DOES:
    1. Creates Memory resource using Bedrock AgentCore SDK
    2. Configures Memory with STM (Short-Term Memory) and optionally LTM (Long-Term Memory)
    3. Returns Memory ARN and ID for use in configuration

OUTPUTS:
    - Memory resource ARN
    - Memory resource ID
    - Memory status

TROUBLESHOOTING:
    - Ensure bedrock-agentcore-starter-toolkit is installed
    - Verify AWS credentials have bedrock-agentcore permissions
    - Check region is correct (us-east-2)

RELATED FILES:
    - scripts/setup_agentcore_resources.py - Uses this module
    - memory/memory_manager.py - Uses Memory resource created here

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import boto3
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def create_memory_resource(
    name: str,
    description: Optional[str] = None,
    enable_ltm: bool = True,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create AgentCore Memory resource.
    
    ARGUMENTS:
        name (str): Memory resource name
        description (Optional[str]): Memory resource description
        enable_ltm (bool): Enable Long-Term Memory (default: True)
        region (Optional[str]): AWS region (default: from env or us-east-2)
    
    RETURNS:
        Dict[str, Any]: Memory resource details with 'memory_arn', 'memory_id', 'status'
    
    RAISES:
        Exception: If Memory creation fails
    """
    region = region or os.getenv('AWS_REGION', 'us-east-2')
    
    try:
        # Try using Bedrock AgentCore SDK
        try:
            from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
            from bedrock_agentcore_starter_toolkit.operations.memory.models.strategies import (
                EventStrategy,
                SemanticStrategy
            )
            
            logger.info(f"🚀 Creating Memory resource: {name}")
            logger.info(f"   Region: {region}")
            logger.info(f"   Long-Term Memory: {'Enabled' if enable_ltm else 'Disabled'}")
            
            memory_manager = MemoryManager(region_name=region)
            
            # Build strategies list
            strategies = [
                EventStrategy(
                    name="eventShortTermMemory",
                    namespaces=['/strategies/{memoryStrategyId}/actors/{actorId}']
                )
            ]
            
            if enable_ltm:
                strategies.append(
                    SemanticStrategy(
                        name="semanticLongTermMemory",
                        namespaces=['/strategies/{memoryStrategyId}/actors/{actorId}']
                    )
                )
            
            # Create or get existing memory
            memory = memory_manager.get_or_create_memory(
                name=name,
                description=description or f"Memory resource for {name}",
                strategies=strategies
            )
            
            memory_id = memory.get('id') or memory.get('memory_id')
            memory_arn = memory.get('arn') or memory.get('memory_arn')
            
            if not memory_arn and memory_id:
                # Construct ARN if not provided
                account_id = boto3.client('sts').get_caller_identity()['Account']
                memory_arn = f"arn:aws:bedrock-agentcore:{region}:{account_id}:memory-resource/{memory_id}"
            
            logger.info(f"✅ Memory resource created successfully!")
            logger.info(f"   Memory ID: {memory_id}")
            logger.info(f"   Memory ARN: {memory_arn}")
            
            return {
                'memory_id': memory_id,
                'memory_arn': memory_arn,
                'status': memory.get('status', 'CREATING'),
                'name': name,
                'strategies': [s.name for s in strategies]
            }
            
        except ImportError:
            # Fallback: Use boto3 directly if SDK not available
            logger.warning("⚠️  bedrock-agentcore-starter-toolkit not available, using boto3")
            return _create_memory_via_boto3(name, description, enable_ltm, region)
            
    except Exception as e:
        logger.error(f"❌ Failed to create Memory resource: {e}")
        raise


def _create_memory_via_boto3(
    name: str,
    description: Optional[str],
    enable_ltm: bool,
    region: str
) -> Dict[str, Any]:
    """
    Create Memory resource using boto3 (fallback method).
    
    ARGUMENTS:
        name (str): Memory resource name
        description (Optional[str]): Memory resource description
        enable_ltm (bool): Enable Long-Term Memory
        region (str): AWS region
    
    RETURNS:
        Dict[str, Any]: Memory resource details
    
    NOTE:
        This is a fallback method. The preferred method uses the AgentCore SDK.
    """
    try:
        # Note: AgentCore Control Plane API might require different client initialization
        # This is a placeholder - actual implementation depends on boto3 API availability
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        
        # Build memory configuration
        memory_config = {
            'name': name,
            'description': description or f"Memory resource for {name}",
            'strategies': [
                {
                    'name': 'eventShortTermMemory',
                    'type': 'EVENT',
                    'namespaces': ['/strategies/{memoryStrategyId}/actors/{actorId}']
                }
            ]
        }
        
        if enable_ltm:
            memory_config['strategies'].append({
                'name': 'semanticLongTermMemory',
                'type': 'SEMANTIC',
                'namespaces': ['/strategies/{memoryStrategyId}/actors/{actorId}']
            })
        
        # Create memory resource
        # Note: Actual API call depends on available boto3 methods
        # This might need to be updated based on actual AWS API
        response = client.create_memory_resource(**memory_config)
        
        return {
            'memory_id': response.get('memoryId') or response.get('id'),
            'memory_arn': response.get('memoryArn') or response.get('arn'),
            'status': response.get('status', 'CREATING'),
            'name': name
        }
        
    except Exception as e:
        logger.error(f"❌ boto3 fallback failed: {e}")
        logger.info("   💡 Install bedrock-agentcore-starter-toolkit for better support:")
        logger.info("      pip install bedrock-agentcore-starter-toolkit")
        raise


def get_memory_resource(memory_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get existing Memory resource details.
    
    ARGUMENTS:
        memory_id (str): Memory resource ID
        region (Optional[str]): AWS region
    
    RETURNS:
        Dict[str, Any]: Memory resource details
    """
    region = region or os.getenv('AWS_REGION', 'us-east-2')
    
    try:
        from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
        
        memory_manager = MemoryManager(region_name=region)
        memory = memory_manager.get_memory(memory_id)
        
        return {
            'memory_id': memory.get('id') or memory_id,
            'memory_arn': memory.get('arn'),
            'status': memory.get('status'),
            'name': memory.get('name')
        }
    except Exception as e:
        logger.error(f"❌ Failed to get Memory resource: {e}")
        raise

