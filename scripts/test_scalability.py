"""
===============================================================================
SCRIPT NAME: test_scalability.py
===============================================================================

PURPOSE:
    Tests scalability of the AgentCore Runtime deployment.

USAGE:
    python scripts/test_scalability.py --concurrent-users 100

WHAT THIS SCRIPT DOES:
    1. Sends concurrent requests to AgentCore Runtime
    2. Measures response times
    3. Tracks success rates
    4. Reports scalability metrics
===============================================================================
"""

import argparse
import concurrent.futures
import time
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from frontend.agent_client import AgentCoreClient

logger = setup_logger(__name__)


def send_request(session_id: str, prompt: str) -> Dict[str, Any]:
    """Send single request to agent."""
    client = AgentCoreClient()
    start_time = time.time()
    response = client.invoke_agent(prompt, session_id)
    elapsed = time.time() - start_time
    return {
        'session_id': session_id,
        'response': response,
        'elapsed': elapsed,
        'success': 'error' not in response
    }


def test_scalability(concurrent_users: int = 10, num_requests: int = 1):
    """Test scalability with concurrent users."""
    logger.info(f"🚀 Starting scalability test: {concurrent_users} concurrent users")
    
    results = []
    prompts = ["List EC2 instances"] * num_requests
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for i in range(len(prompts)):
            session_id = f"test-session-{i}"
            future = executor.submit(send_request, session_id, prompts[i])
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    # Analyze results
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    avg_time = sum(r['elapsed'] for r in results) / len(results) if results else 0
    
    logger.info(f"✅ Test complete!")
    logger.info(f"   Successful: {successful}/{len(results)}")
    logger.info(f"   Failed: {failed}/{len(results)}")
    logger.info(f"   Average response time: {avg_time:.2f}s")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Test AgentCore Runtime scalability")
    parser.add_argument('--concurrent-users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--requests-per-user', type=int, default=1, help='Requests per user')
    
    args = parser.parse_args()
    
    test_scalability(args.concurrent_users, args.requests_per_user)
    return 0


if __name__ == "__main__":
    sys.exit(main())

