# Enterprise Cloud Engineer Agent - Implementation Plan
## Migration from Strands Agents to AWS Bedrock AgentCore

**Version:** 1.1  
**Date:** 2025-01-XX  
**Status:** Planning Phase - Requirements Confirmed  
**Target:** Enterprise-grade multi-user cloud engineering agent with high security and scalability

**Configuration:**
- **Region**: us-east-2
- **Cognito User Pool**: Create new OR use existing (will be created/verified)
- **Concurrent Users**: 100+ users
- **Compliance**: Guardrails implementation required

---

## Table of Contents

1. [Prerequisites & Getting Started](#prerequisites--getting-started) ⭐ **START HERE**
2. [Executive Summary](#executive-summary)
3. [Current State Analysis](#current-state-analysis)
4. [Target Architecture & Recommendations](#target-architecture--recommendations)
5. [AgentCore Modules Overview](#agentcore-modules-overview)
6. [Project Structure](#project-structure) ⭐ **UPDATED: Modular Structure**
7. [Implementation Phases](#implementation-phases)
8. [Step-by-Step Implementation Guide](#step-by-step-implementation-guide) ⭐ **CRITICAL**
9. [Detailed Script & Component Documentation](#detailed-script--component-documentation)
10. [Configuration Files](#configuration-files) ⭐ **SETUP REQUIRED**
11. [Security & Compliance](#security--compliance)
12. [Guardrails & Content Safety](#guardrails--content-safety)
13. [Troubleshooting Guide](#troubleshooting-guide) ⭐ **CRITICAL**
14. [Cost Estimation](#cost-estimation)
15. [Scalability & Performance](#scalability--performance)
16. [SSO Preparation (Phase 2)](#sso-preparation-phase-2)
17. [Testing Strategy](#testing-strategy)
18. [Deployment & Rollout](#deployment--rollout)
19. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites & Getting Started ⭐ **START HERE**

### Who Should Read This First?

If you're a **newbie** starting this project:
1. ✅ Read this entire section FIRST
2. ✅ Complete all prerequisites BEFORE starting
3. ✅ Follow the "Day 1 Setup" step-by-step
4. ✅ Verify each step before moving to next

### Prerequisites Checklist

**Required Software:**
- [ ] **Python 3.10 or higher** (3.11+ recommended)
  ```bash
  python --version  # Should show 3.10+ or 3.11+
  ```
- [ ] **AWS CLI 2.x** installed and configured
  ```bash
  aws --version  # Should show aws-cli/2.x.x
  aws configure  # Configure your credentials
  ```
- [ ] **Docker Desktop** installed and running
  ```bash
  docker --version  # Should show Docker version
  docker ps  # Should work without errors
  ```
- [ ] **Git** installed
  ```bash
  git --version  # Should show git version
  ```
- [ ] **Code Editor** (VS Code recommended)

**Required AWS Access:**
- [ ] **AWS Account** with admin access or sufficient permissions
- [ ] **AWS CLI configured** with credentials
  ```bash
  aws sts get-caller-identity  # Should return your account info
  ```
- [ ] **Bedrock Model Access Enabled**
  - Go to: AWS Console → Bedrock → Model access
  - Enable: Claude Sonnet 3.7 (or your preferred model)
  - Wait 2-5 minutes for propagation
  - Verify:
    ```bash
    aws bedrock list-foundation-models --region us-east-2 | grep claude
    ```
- [ ] **Cognito User Pool ID** available
  - Find it: AWS Console → Cognito → User Pools → Select pool → Copy Pool ID
  - Or via CLI:
    ```bash
    aws cognito-idp list-user-pools --max-results 10 --region us-east-2
    ```
- [ ] **IAM Permissions** (see IAM Permissions section below)

**Required Knowledge:**
- Basic Python programming
- Basic AWS services understanding
- Docker basics
- Command line basics

### Day 1: Environment Setup (Step-by-Step)

#### Step 1: Verify Python Installation

```bash
# Check Python version
python --version
# Expected: Python 3.10.x or 3.11.x

# If not installed or wrong version:
# Windows: Download from python.org
# Mac: brew install python@3.11
# Linux: sudo apt-get install python3.11
```

#### Step 2: Install AWS CLI

```bash
# Windows: Download MSI installer from AWS website
# Mac: brew install awscli
# Linux: sudo apt-get install awscli

# Verify installation
aws --version
# Expected: aws-cli/2.x.x
```

#### Step 3: Configure AWS Credentials

```bash
# Run AWS configure
aws configure

# Enter when prompted:
# AWS Access Key ID: <your-access-key>
# AWS Secret Access Key: <your-secret-key>
# Default region name: us-east-2
# Default output format: json

# Verify configuration
aws sts get-caller-identity
# Expected: Returns your AWS account details
```

**How to Get AWS Credentials:**
1. Go to AWS Console → IAM → Users → Your User → Security Credentials
2. Create Access Key
3. Download CSV file (save securely!)
4. Use Access Key ID and Secret Access Key in `aws configure`

#### Step 4: Enable Bedrock Model Access

```bash
# Check current model access
aws bedrock list-foundation-models --region us-east-2 --query 'modelSummaries[?contains(modelId, `claude`)].modelId'

# If no models found, enable via Console:
# 1. Go to: https://console.aws.amazon.com/bedrock/
# 2. Click: "Model access" in left menu
# 3. Click: "Edit" button
# 4. Enable: "Anthropic Claude Sonnet 3.7"
# 5. Click: "Save changes"
# 6. Wait 2-5 minutes
# 7. Verify again with command above
```

#### Step 5: Get Cognito User Pool ID

**Option 1: AWS Console**
1. Go to: https://console.aws.amazon.com/cognito/
2. Click: "User pools" in left menu
3. Click on your user pool
4. Copy the "User pool ID" (format: `us-east-2_XXXXXXXXX`)

**Option 2: AWS CLI**
```bash
aws cognito-idp list-user-pools --max-results 10 --region us-east-2
# Copy the Id value from output
```

**Save this ID** - you'll need it throughout the setup!

#### Step 6: Setup Project Directory

```bash
# Clone or navigate to project directory
cd maygum-agentcore

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Verify activation (should show (.venv) in prompt)
# Your prompt should now show: (.venv) $ 
```

#### Step 7: Install Dependencies

**Create `requirements.txt` file:**
```txt
# Core Dependencies
bedrock-agentcore>=0.1.0
bedrock-agentcore-starter-toolkit>=0.1.21  # Required for agentcore CLI
strands-agents>=0.1.0
boto3>=1.34.0
botocore>=1.34.0

# Streamlit
streamlit>=1.28.0
streamlit-authenticator>=0.2.3

# Observability
aws-opentelemetry-distro>=0.1.0
opentelemetry-api>=1.21.0
opentelemetry-sdk>=1.21.0

# MCP Tools (existing)
mcp>=0.1.0
strands-tools>=0.1.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0
requests>=2.31.0

# Testing
pytest>=7.4.0
pytest-mock>=3.12.0

# Load Testing (for scalability tests)
locust>=2.17.0

**Install dependencies:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify critical packages
python -c "import bedrock_agentcore; print('✅ AgentCore installed')"
python -c "import strands; print('✅ Strands installed')"
python -c "import boto3; print('✅ Boto3 installed')"
python -c "import streamlit; print('✅ Streamlit installed')"
```

#### Step 8: Create Configuration File

```bash
# Copy example file
cp .env.example .env

# Edit .env file with your values
# Windows: notepad .env
# Mac/Linux: nano .env or vim .env
```

**Get your AWS Account ID:**
```bash
aws sts get-caller-identity --query Account --output text
# Copy this value
```

**Populate .env file:**
```bash
# Replace these values in .env:
AWS_REGION=us-east-2
AWS_ACCOUNT_ID=<paste-your-account-id>
COGNITO_USER_POOL_ID=<paste-your-pool-id>
COGNITO_REGION=us-east-2

# Leave other values as-is (will be populated by scripts)
```

#### Step 9: Validate Environment

```bash
# Run validation script
python scripts/validate_environment.py

# Expected output:
✅ AWS credentials configured
✅ Region us-east-2 accessible
✅ Bedrock access verified
✅ Cognito User Pool accessible
✅ Python dependencies installed
✅ Configuration file found

# If any checks fail, fix them before proceeding
```

### Verification Checklist

Before starting implementation, verify:

- [ ] Python 3.10+ installed and verified
- [ ] AWS CLI installed and configured
- [ ] AWS credentials working (`aws sts get-caller-identity` works)
- [ ] Bedrock model access enabled (can list models)
- [ ] Cognito User Pool ID available
- [ ] Project directory created
- [ ] Virtual environment activated
- [ ] Dependencies installed (no import errors)
- [ ] `.env` file created with basic values
- [ ] Environment validation passes

### Common First-Time Issues

**Issue: "aws: command not found"**
- **Solution:** Install AWS CLI and add to PATH

**Issue: "Permission denied" errors**
- **Solution:** Check AWS credentials and IAM permissions

**Issue: "No module named 'bedrock_agentcore'"**
- **Solution:** Activate virtual environment and install dependencies

**Issue: "Bedrock model access denied"**
- **Solution:** Enable model access in AWS Console (see Step 4)

**Issue: "Cognito User Pool not found"**
- **Solution:** Verify pool ID and region are correct

### Next Steps After Setup

Once prerequisites are complete:
1. ✅ Read "Project Structure" section
2. ✅ Review "Step-by-Step Implementation Guide"
3. ✅ Start with Phase 1: Foundation Setup
4. ✅ Follow each phase sequentially

---

## Executive Summary

### Objective
Transform the existing single-user Strands Agents-based cloud engineer agent into an enterprise-grade, multi-user application using AWS Bedrock AgentCore. The new system will support concurrent users, provide enterprise security with Cognito authentication, and leverage all AgentCore modules for scalability, observability, and persistent memory.

### Key Benefits
- **Multi-user Support**: Serve 100+ concurrent users with session isolation
- **Enterprise Security**: Cognito integration with SSO-ready architecture
- **Guardrails & Compliance**: Content filtering, topic blocking, and PII protection
- **Scalability**: Auto-scaling serverless runtime with dedicated microVMs per session
- **Observability**: Complete tracing, monitoring, and debugging capabilities
- **Persistent Memory**: Conversation history and knowledge persistence across sessions
- **High Availability**: Built-in session persistence and fault tolerance

### Estimated Timeline
- **Phase 1 (Core Migration)**: 4-6 weeks
- **Phase 2 (SSO Integration)**: 2-3 weeks
- **Total Duration**: 6-9 weeks

---

## Current State Analysis

### Existing Architecture

**Components:**
1. **Streamlit UI** (`app.py`)
   - Single-user interface
   - Local session state management
   - No authentication
   - Predefined tasks dropdown
   - Chat-based interaction

2. **Strands Agent** (`cloud_engineer_agent.py`)
   - Single Agent instance with Bedrock Nova Premier model
   - MCP tools integration:
     - AWS CLI tool (`use_aws`)
     - CloudFormation MCP (resource creation/updates/deletion)
     - AWS Documentation MCP (best practices search)
     - AWS Diagram MCP (architecture visualization)
     - Cost Explorer MCP (cost analysis)
   - Complex system prompt with workflow rules
   - No session persistence
   - No user isolation

3. **Infrastructure:**
   - Local execution or single deployment
   - No load balancing
   - No user authentication
   - No observability beyond basic logging

### Current Limitations

1. **Scalability**: Single user, no concurrent support
2. **Security**: No authentication or authorization
3. **Session Management**: No persistence across sessions
4. **Observability**: Limited visibility into agent operations
5. **Multi-tenancy**: No user isolation or data separation
6. **Deployment**: Manual, not production-ready

---

## Target Architecture & Recommendations

### Recommended Architecture: **Single Agent with Runtime Enhancement**

**Decision: Single Agent Architecture** (NOT Multi-Agent Supervisor Pattern)

**Rationale:**
1. **Existing Agent Complexity**: Your current agent already handles complex workflows internally (CREATE/UPDATE/DELETE/DIAGRAM sections)
2. **Cost Efficiency**: Single agent runtime reduces infrastructure costs
3. **Simplicity**: Easier to maintain and debug
4. **AgentCore Runtime Benefits**: Runtime provides session isolation and scaling automatically
5. **Future Flexibility**: Can evolve to multi-agent if needed without major refactoring

**When to Consider Multi-Agent Supervisor Pattern:**
- If you need specialized agents for different domains (e.g., Security Specialist, Cost Analyst, Infrastructure Architect)
- If concurrent workloads exceed single agent capacity
- If you want to implement parallel processing for complex tasks

**Current Assessment:** Your agent already operates as a comprehensive cloud engineer with internal routing logic. The AgentCore Runtime will handle the multi-user scaling and session isolation.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer (Frontend)                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Streamlit Web App (runs on localhost:8501 or ECS/ALB)     │  │
│  │  - Authentication UI (Cognito login)                       │  │
│  │  - Chat Interface                                           │  │
│  │  - User Session Management (Client-side)                   │  │
│  │                                                              │  │
│  │  When User Types Message:                                   │  │
│  │  1. User authenticates → Gets JWT token                     │  │
│  │  2. User sends message → Streamlit makes HTTP request       │  │
│  │  3. Streamlit calls AgentCore Runtime API                  │  │
│  └───────────────┬─────────────────────────────────────────────┘  │
└───────────────────┼───────────────────────────────────────────────┘
                    │
                    │ HTTPS Request with JWT Token
                    │ InvokeAgentRuntime API Call
                    │
┌───────────────────▼───────────────────────────────────────────────┐
│           AgentCore Runtime (Serverless Backend)                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Runtime Request Handler                                    │  │
│  │  - Validates JWT token (via Cognito)                        │  │
│  │  - Extracts session ID from request                        │  │
│  │  - Creates/retrieves microVM for this session              │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Session 1: User A, Session ID: abc-123              │  │  │
│  │  │  ┌────────────────────────────────────────────────┐  │  │  │
│  │  │  │  MicroVM 1 (Isolated)                         │  │  │  │
│  │  │  │  - Cloud Engineer Agent                       │  │  │  │
│  │  │  │  - Bedrock Model                              │  │  │  │
│  │  │  │  - MCP Tools                                  │  │  │  │
│  │  │  │  - Memory Context (User A's data)             │  │  │  │
│  │  │  └────────────────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Session 2: User B, Session ID: xyz-789              │  │  │
│  │  │  ┌────────────────────────────────────────────────┐  │  │  │
│  │  │  │  MicroVM 2 (Isolated)                         │  │  │  │
│  │  │  │  - Cloud Engineer Agent                       │  │  │  │
│  │  │  │  - Bedrock Model                              │  │  │  │
│  │  │  │  - MCP Tools                                  │  │  │  │
│  │  │  │  - Memory Context (User B's data)             │  │  │  │
│  │  │  └────────────────────────────────────────────────┘  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                              │  │
│  │  Session Isolation: Each RUNTIME SESSION gets dedicated     │  │
│  │  microVM (not each Streamlit user - multiple Streamlit     │  │
│  │  users can share same runtime session if same session ID)  │  │
│  │                                                              │  │
│  │  Auto-scaling: Creates new microVMs as needed for          │  │
│  │  concurrent runtime sessions                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                    │
                    │
┌───────────────────▼───────────────────────────────────────────────┐
│                    AgentCore Services Layer                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  Memory Service  │  │  Identity Service│  │  Observability │ │
│  │  - Event Memory  │  │  - Cognito Auth  │  │  - CloudWatch  │ │
│  │  - Semantic Mem  │  │  - JWT Validation│  │  - X-Ray Trace │ │
│  └──────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                    │
                    │
┌───────────────────▼───────────────────────────────────────────────┐
│                      AWS Services Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │   Cognito    │  │ CloudWatch   │  │  AWS Services        │    │
│  │ User Pools   │  │ Logs/Metrics │  │  (EC2, S3, RDS, etc)│    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

### Key Architecture Decisions

1. **Single Agent Runtime**: One Cloud Engineer Agent deployed to AgentCore Runtime
2. **Session-Based Isolation**: AgentCore Runtime provides per-runtime-session microVM isolation
3. **Memory Persistence**: AgentCore Memory for conversation history and knowledge
4. **Cognito Integration**: User authentication via Cognito User Pools
5. **Observability**: Full OpenTelemetry instrumentation with CloudWatch integration
6. **Streamlit Frontend**: Maintained but enhanced with authentication and session management

### Architecture Clarification: How Streamlit UI Connects to AgentCore Runtime

**Important Understanding**: Streamlit UI and AgentCore Runtime are **separate services** that communicate via HTTP API calls.

**Flow When User Accesses Streamlit UI:**

1. **User opens Streamlit UI** (http://localhost:8501 or production URL)
   - Streamlit renders login page if not authenticated
   - User enters credentials → Streamlit calls Cognito → Gets JWT token
   - Streamlit stores token in session state

2. **User sends message in chat**
   - Streamlit UI captures user input
   - Streamlit code calls AgentCore Runtime API:
     ```python
     # In frontend/agent_client.py
     response = agentcore_client.invoke_agent_runtime(
         agentRuntimeArn=<runtime-arn>,
         runtimeSessionId=<session-id>,  # Generated by Streamlit per user/conversation
         payload=json.dumps({"prompt": user_message}),
         qualifier="DEFAULT"
     )
     ```

3. **AgentCore Runtime receives request**
   - Validates JWT token (if OAuth configured)
   - Creates/retrieves microVM for the runtime session ID
   - Runs agent code in isolated microVM
   - Returns response to Streamlit

4. **Streamlit displays response**
   - Receives response from AgentCore Runtime
   - Displays in chat interface
   - Stores in conversation history (client-side)

**Key Points:**

- **Streamlit runs separately** from AgentCore Runtime
- **Each runtime session** (identified by session ID) gets its own microVM
- **Multiple Streamlit users** can call the same AgentCore Runtime simultaneously
- **Session ID strategy**: Streamlit generates unique session IDs per user/conversation
- **Scalability**: AgentCore Runtime auto-scales microVMs based on concurrent sessions

**Example Scenario: 100 Users Access Streamlit UI**

**Scenario: 100 concurrent users accessing http://localhost:8501**

1. **100 users open Streamlit UI simultaneously**
   - Each user has their own browser session
   - Each user logs in → Gets unique JWT token from Cognito
   - Streamlit generates unique session ID per user: `user-1-session-abc`, `user-2-session-xyz`, etc.

2. **Each user sends a message**
   - User 1 sends message → Streamlit calls AgentCore Runtime with:
     - JWT token (User 1's token)
     - Session ID: `user-1-session-abc`
     - Payload: User 1's message
   
   - User 2 sends message (concurrently) → Streamlit calls AgentCore Runtime with:
     - JWT token (User 2's token)
     - Session ID: `user-2-session-xyz` (different session ID)
     - Payload: User 2's message

3. **AgentCore Runtime handles requests**
   - **Request 1** (User 1): 
     - Validates User 1's JWT token
     - Checks if session `user-1-session-abc` exists → No
     - **Creates MicroVM 1** (isolated)
     - Runs agent in MicroVM 1 with User 1's context
     - Stores User 1's data in Memory (scoped to User 1's user ID)
   
   - **Request 2** (User 2, concurrent):
     - Validates User 2's JWT token
     - Checks if session `user-2-session-xyz` exists → No
     - **Creates MicroVM 2** (separate from MicroVM 1)
     - Runs agent in MicroVM 2 with User 2's context
     - Stores User 2's data in Memory (scoped to User 2's user ID)

4. **Result**
   - 100 concurrent users → Up to 100 microVMs created
   - Each microVM is completely isolated
   - No data leakage between users
   - AgentCore Runtime auto-scales microVMs as needed

**Important Clarifications:**

- **Streamlit UI**: Runs on ONE server (localhost:8501 or ECS). Multiple users access the SAME Streamlit instance.
- **AgentCore Runtime**: Receives API calls from Streamlit. Creates separate microVM per RUNTIME SESSION ID.
- **Session ID Strategy**: Streamlit generates unique session IDs per user/conversation to ensure isolation.
- **MicroVM Creation**: Happens automatically by AgentCore Runtime when new session ID is provided.
- **No Manual VM Management**: You don't create VMs manually - AgentCore Runtime handles it automatically.

**How to Verify Scalability:**

```bash
# Run scalability test
python scripts/test_scalability.py \
  --concurrent-users 100 \
  --runtime-arn <your-runtime-arn>

# Expected Result:
# - 100 concurrent requests sent
# - AgentCore Runtime creates up to 100 microVMs
# - All requests succeed
# - Response times acceptable
# - No errors or data leakage
```

---

## AgentCore Modules Overview

### Module 1: AgentCore Runtime ⭐ PRIMARY MODULE

**Purpose**: Serverless runtime environment for agent deployment

**What It Does:**
- Deploys your Strands Agent as a serverless, production-ready service
- Provides automatic HTTP service wrapper with `/invocations` and `/ping` endpoints
- Handles session management with automatic 15-minute timeout
- Provides **dedicated microVM per user session** (complete isolation)
- Auto-scales based on concurrent requests (handles 100+ users)
- Built-in health checks and status management
- Supports ARM64 container deployment

**Key Features:**
- Automatic HTTP service wrapper (`/invocations`, `/ping` endpoints)
- Session management with automatic 15-minute timeout
- Dedicated microVM per user session (complete isolation)
- Auto-scaling based on concurrent requests
- Built-in health checks and status management
- ARM64 container support

**Key Benefits:**
- **Multi-user Support**: Each user gets isolated microVM (no data leakage)
- **Auto-scaling**: Handles spikes in concurrent users automatically
- **High Availability**: Built-in fault tolerance and session persistence
- **Serverless**: No infrastructure management needed

**What You Get:**
- HTTP endpoints for agent invocation
- Session isolation (critical for multi-user)
- Automatic scaling
- Health monitoring

**Integration Points:**
- Wrap existing Strands Agent with `BedrockAgentCoreApp`
- Deploy as containerized runtime to ECR
- Configure IAM roles for AWS service access
- Set up network configuration (PUBLIC or VPC)

**Scripts Required:**
- `runtime/agent_runtime.py` - Main agent wrapper
- `runtime/Dockerfile` - ARM64 container definition
- `runtime/deploy_runtime.py` - Deployment automation

---

### Module 2: AgentCore Memory ⭐ ESSENTIAL

**Purpose**: Persistent storage for conversation context and knowledge

**What It Does:**
- **Event Memory**: Stores conversation history per user session
- **Semantic Memory**: Long-term knowledge persistence with vector search
- **User Isolation**: Separate memory spaces per user (no cross-user data access)
- **Memory Strategies**: Event-based or semantic-based retrieval

**Key Features:**
- **Event Memory**: Store conversation history per user session
- **Semantic Memory**: Long-term knowledge persistence with vector search
- **User Isolation**: Separate memory spaces per user
- **Memory Strategies**: Event-based or semantic-based retrieval

**Key Benefits:**
- Store conversation context after each interaction
- Retrieve relevant past conversations for context awareness
- Semantic search for knowledge base queries
- User-specific memory isolation

**What You Get:**
- Persistent conversation history across sessions
- Context awareness (agent remembers past conversations)
- Knowledge persistence (learns from user interactions)
- User data isolation (GDPR compliance)

**Use Cases:**
- "What did we discuss yesterday about EC2 costs?"
- "Remember my VPC configuration preferences"
- "Search previous conversations about security best practices"

**Integration Points:**
- Initialize memory resource per user or per organization
- Store conversation context after each agent interaction
- Retrieve relevant past conversations for context awareness
- Implement semantic search for knowledge base queries

**Scripts Required:**
- `memory/memory_manager.py` - Memory operations wrapper
- `memory/memory_config.py` - Memory resource configuration
- `memory/session_memory_handler.py` - Session-specific memory handling

---

### 📋 Session Management: How Sessions Work, Retrieve Previous Sessions, and Name Sessions

**Purpose**: Understanding how AgentCore Memory manages user sessions, retrieving past conversations, and custom session naming

#### **What is a Session in AgentCore Memory?**

A **session** is a logical grouping of conversation events (turns) for a specific user (actor). Think of it as a conversation thread:

- **Actor ID**: Identifies the user (e.g., Cognito user ID: `user-123` or `us-east-2_abc123def`)
- **Session ID**: Identifies a specific conversation (e.g., `project-analysis-2025-01-15` or `troubleshooting-vpc`)
- **Events**: Individual conversation turns stored in the session

#### **Session Lifecycle**

1. **Creating a Session**: Automatically created when first event is stored
   ```python
   # Session is created automatically when you add the first turn
   manager.add_turns(
       actor_id="user-123",
       session_id="my-project-analysis",  # Custom session name
       messages=[...]
   )
   ```

2. **Continuing a Session**: Use the same `session_id` to continue a conversation
   ```python
   # Continue the same session
   manager.add_turns(
       actor_id="user-123",
       session_id="my-project-analysis",  # Same session ID
       messages=[...]  # New messages added to existing session
   )
   ```

3. **Creating New Sessions**: Use different `session_id` for new conversations
   ```python
   # Start a new session with a different name
   manager.add_turns(
       actor_id="user-123",
       session_id="new-troubleshooting-session",  # Different session ID
       messages=[...]
   )
   ```

#### **Retrieving Previous Sessions**

**Question: Can users go back to previous sessions?**

**Answer: YES!** Users can retrieve and continue any previous session.

**Method 1: List All Sessions for a User**
```python
from bedrock_agentcore.memory.session import MemorySessionManager

manager = MemorySessionManager(memory_id="mem-xyz", region_name="us-east-2")

# List all sessions for a specific user (actor)
sessions = manager.list_actor_sessions(actor_id="user-123")

# Returns: List of SessionSummary objects with:
# - session_id: The session identifier
# - first_event_timestamp: When the session started
# - last_event_timestamp: Last activity in the session
# - event_count: Number of events in the session

for session in sessions:
    print(f"Session: {session['sessionId']}")
    print(f"  Started: {session['firstEventTimestamp']}")
    print(f"  Last Activity: {session['lastEventTimestamp']}")
    print(f"  Events: {session['eventCount']}")
```

**Method 2: Retrieve Session History**
```python
# Get all events from a specific session
events = manager.list_events(
    actor_id="user-123",
    session_id="my-project-analysis",
    max_results=100
)

# Get the last K conversation turns from a session
turns = manager.get_last_k_turns(
    actor_id="user-123",
    session_id="my-project-analysis",
    k=10  # Last 10 conversation turns
)
```

**Method 3: Get Specific Event**
```python
# Retrieve a specific event by ID
event = manager.get_event(
    actor_id="user-123",
    session_id="my-project-analysis",
    event_id="evt-abc123"
)
```

#### **Naming Sessions**

**Question: Can users name sessions?**

**Answer: YES!** Session IDs are customizable strings. You can use any naming convention you want.

**Naming Strategies:**

1. **Descriptive Names** (Recommended for User-Facing Apps)
   ```python
   session_id = "project-analysis-2025-01-15"
   session_id = "vpc-troubleshooting-session"
   session_id = "cost-optimization-review"
   session_id = "security-audit-qa"
   ```

2. **User-Friendly Names** (From UI Input)
   ```python
   # User types: "My VPC Setup Session"
   session_id = "my-vpc-setup-session"  # Sanitized user input
   ```

3. **Timestamp-Based** (Auto-Generated)
   ```python
   from datetime import datetime
   session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
   # Result: "session-20250115-143022"
   ```

4. **UUID-Based** (Unique but Not Human-Readable)
   ```python
   import uuid
   session_id = str(uuid.uuid4())
   # Result: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
   ```

5. **Hybrid Approach** (Recommended)
   ```python
   # Combine user-friendly name with timestamp for uniqueness
   user_name = "project-analysis"  # User-provided or auto-generated
   timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
   session_id = f"{user_name}-{timestamp}"
   # Result: "project-analysis-20250115-143022"
   ```

#### **Integration with Streamlit UI**

**How to Implement Session Management in Streamlit:**

```python
# frontend/session_manager.py
import streamlit as st
from bedrock_agentcore.memory.session import MemorySessionManager
from datetime import datetime

class StreamlitSessionManager:
    def __init__(self, memory_id: str, region_name: str):
        self.memory_manager = MemorySessionManager(
            memory_id=memory_id,
            region_name=region_name
        )
    
    def get_current_session_id(self, user_id: str) -> str:
        """Get or create current session ID"""
        if 'current_session_id' not in st.session_state:
            # Create new session with timestamp
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            st.session_state['current_session_id'] = f"{user_id}-{timestamp}"
        return st.session_state['current_session_id']
    
    def list_user_sessions(self, user_id: str):
        """List all sessions for the current user"""
        return self.memory_manager.list_actor_sessions(actor_id=user_id)
    
    def switch_session(self, session_id: str):
        """Switch to a different session"""
        st.session_state['current_session_id'] = session_id
        st.session_state['messages'] = []  # Clear current messages
        # Load messages from new session
        self.load_session_history(user_id=st.session_state['user_id'], session_id=session_id)
    
    def load_session_history(self, user_id: str, session_id: str):
        """Load conversation history from a session"""
        turns = self.memory_manager.get_last_k_turns(
            actor_id=user_id,
            session_id=session_id,
            k=50  # Load last 50 turns
        )
        # Convert to Streamlit message format
        messages = []
        for turn in turns:
            for msg in turn:
                role = "user" if msg['role'] == 'USER' else "assistant"
                messages.append({
                    "role": role,
                    "content": msg['content']['text']
                })
        st.session_state['messages'] = messages
```

**Streamlit UI Example:**

```python
# In app.py
import streamlit as st
from frontend.session_manager import StreamlitSessionManager

# Initialize session manager
session_manager = StreamlitSessionManager(
    memory_id=os.getenv("MEMORY_ID"),
    region_name="us-east-2"
)

# Sidebar: Session Management
with st.sidebar:
    st.header("📋 My Sessions")
    
    # List all user sessions
    user_id = st.session_state.get('user_id')
    if user_id:
        sessions = session_manager.list_user_sessions(user_id)
        
        # Display session list
        for session in sessions:
            session_name = session['sessionId']
            last_activity = session['lastEventTimestamp']
            event_count = session['eventCount']
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📁 {session_name[:30]}...", key=f"session-{session_name}"):
                    session_manager.switch_session(session_name)
                    st.rerun()
            with col2:
                st.caption(f"{event_count} msgs")
        
        # Create new session button
        if st.button("➕ New Session"):
            # Clear current session
            if 'current_session_id' in st.session_state:
                del st.session_state['current_session_id']
            if 'messages' in st.session_state:
                st.session_state['messages'] = []
            st.rerun()
        
        # Name current session
        current_session = st.session_state.get('current_session_id', 'Unnamed')
        new_name = st.text_input("Rename Session:", value=current_session)
        if st.button("💾 Save Name") and new_name != current_session:
            # Note: You can't rename an existing session_id, but you can create a new one
            # and copy events, or store metadata separately
            st.info("Session renamed (will create new session with new name)")
```

#### **Session Metadata and Custom Attributes**

You can attach custom metadata to sessions using event metadata:

```python
from bedrock_agentcore.memory.constants import MetadataValue

# Store session with custom metadata
manager.add_turns(
    actor_id="user-123",
    session_id="project-analysis-2025-01-15",
    messages=[...],
    metadata={
        "session_name": MetadataValue(string_value="My Project Analysis"),
        "project_id": MetadataValue(string_value="proj-12345"),
        "created_by": MetadataValue(string_value="user-123"),
        "tags": MetadataValue(string_value="analysis,cloud-architecture")
    }
)

# Query sessions by metadata
events = manager.list_events(
    actor_id="user-123",
    session_id="project-analysis-2025-01-15",
    eventMetadata=[
        {
            'left': {'metadataKey': 'project_id'},
            'operator': 'EQUALS_TO',
            'right': {'metadataValue': {'stringValue': 'proj-12345'}}
        }
    ]
)
```

#### **Best Practices for Session Management**

1. **Session Naming Convention**:
   - Use descriptive names: `"project-{project-name}-{date}"`
   - Include timestamps for uniqueness: `"{description}-{YYYYMMDD-HHMMSS}"`
   - Sanitize user input: Remove special characters, limit length

2. **Session Lifecycle**:
   - Create sessions when user starts a new conversation topic
   - Continue sessions for related conversations
   - Archive old sessions after inactivity (e.g., 90 days)

3. **Session Retrieval**:
   - Display session list in UI sidebar
   - Show session metadata (date, message count, last activity)
   - Allow search/filter by session name or metadata

4. **Session Limits**:
   - Consider limiting active sessions per user (e.g., 50)
   - Implement session archiving for old sessions
   - Use memory event expiry (default: 90 days)

5. **Integration with AgentCore Runtime**:
   - Map Streamlit session IDs to AgentCore Memory session IDs
   - Use Cognito user ID as `actor_id`
   - Generate unique `session_id` per conversation thread

#### **Scripts Required for Session Management**

- `frontend/session_manager.py` - Session management wrapper for Streamlit
- `memory/session_memory_handler.py` - Memory session operations
- `utils/session_utils.py` - Session naming and validation utilities

#### **Example: Complete Session Management Flow**

```python
# Example: User starts new session, names it, retrieves old sessions

# 1. User authenticates and gets actor_id
actor_id = "us-east-2_abc123def"  # From Cognito JWT token

# 2. User creates new session with custom name
session_name = "vpc-troubleshooting-2025-01-15"
session_manager.create_memory_session(
    actor_id=actor_id,
    session_id=session_name
)

# 3. User has conversation
manager.add_turns(
    actor_id=actor_id,
    session_id=session_name,
    messages=[
        ConversationalMessage("How do I troubleshoot VPC connectivity?", MessageRole.USER),
        ConversationalMessage("Here's how to troubleshoot...", MessageRole.ASSISTANT)
    ]
)

# 4. Later, user wants to see all their sessions
all_sessions = manager.list_actor_sessions(actor_id=actor_id)
# Returns: List of all sessions for this user

# 5. User selects a previous session to continue
previous_session = "project-analysis-2025-01-10"
events = manager.list_events(
    actor_id=actor_id,
    session_id=previous_session,
    max_results=100
)
# User can now see and continue previous conversation
```

---

### Module 3: AgentCore Identity ⭐ ESSENTIAL FOR SECURITY

**Purpose**: Authentication and authorization integration

**What It Does:**
- **Cognito Integration**: Integrates with your existing Cognito User Pool
- **JWT Token Validation**: Validates tokens from Streamlit frontend
- **Workload Identity**: Creates workload identity for agent runtime
- **OAuth2 Support**: Ready for SSO integration (Phase 2)
- **User Mapping**: Maps Cognito user IDs to agent sessions

**Key Features:**
- Cognito User Pool integration
- JWT token validation
- Workload identity management
- OAuth2 credential provider support (for SSO phase 2)
- API key management

**Key Benefits:**
- Validates user authentication tokens
- Maps authenticated users to agent sessions
- Provides workload identity for runtime
- OAuth2 credential provider support (for SSO later)

**What You Get:**
- Secure authentication integration
- User-to-session mapping
- SSO-ready architecture
- Access control foundation

**Integration Points:**
- Configure Cognito User Pool as identity provider
- Validate JWT tokens from Streamlit frontend
- Create workload identity for agent runtime
- Map Cognito user IDs to agent sessions

**Scripts Required:**
- `identity/cognito_integration.py` - Cognito setup and validation
- `identity/jwt_validator.py` - Token validation logic
- `identity/workload_identity_manager.py` - Workload identity operations

---

### Module 4: AgentCore Observability ⭐ ESSENTIAL FOR MONITORING

**Purpose**: Monitoring, tracing, and debugging

**What It Does:**
- **OpenTelemetry Integration**: Automatic instrumentation for tracing
- **CloudWatch Integration**: Sends traces and metrics to CloudWatch
- **GenAI Observability Dashboard**: Specialized dashboard for AI agents
- **Session Tracking**: Correlates traces across user sessions
- **Performance Metrics**: Tracks latency, token usage, error rates

**Key Features:**
- OpenTelemetry automatic instrumentation
- CloudWatch integration for traces and metrics
- GenAI Observability dashboard
- Session tracking and correlation
- Performance metrics (latency, token usage, error rates)

**Key Benefits:**
- Automatic instrumentation (no code changes needed)
- Distributed tracing across agent operations
- Performance metrics (response time, token usage)
- Error tracking and debugging
- Session correlation

**What You Get:**
- Complete visibility into agent operations
- Performance monitoring
- Debugging capabilities
- Production monitoring dashboards
- Cost tracking (token usage)

**Metrics Tracked:**
- Agent response time
- Token usage per request
- Error rates
- Session counts
- Concurrent users
- Memory operations

**Integration Points:**
- Enable OpenTelemetry instrumentation for Strands Agent
- Configure CloudWatch Transaction Search
- Add OTEL baggage for session ID propagation
- Set up CloudWatch dashboards for monitoring

**Scripts Required:**
- `observability/otel_config.py` - OpenTelemetry configuration
- `observability/metrics_collector.py` - Custom metrics collection
- `observability/dashboard_setup.py` - CloudWatch dashboard creation

---

### Module 5: AgentCore Gateway ⭐ RECOMMENDED FOR PHASE 2

**Purpose**: Transform existing APIs into agent tools via MCP (Model Context Protocol)

**What It Does:**
- Transforms existing APIs into agent tools via MCP (Model Context Protocol)
- **Smithy Model Support**: Convert AWS service APIs (350+ available) to MCP tools ⭐ **KEY FEATURE**
- **OpenAPI Support**: Convert REST APIs to MCP tools
- **Lambda Support**: Convert Lambda functions to MCP tools
- OAuth authentication and API key management
- Semantic search for tool discovery

**Key Features:**
- **OpenAPI Support**: Convert REST APIs to MCP tools
- **Smithy Model Support**: Convert AWS service APIs (350+ available) to MCP tools ⭐ **KEY FEATURE**
- **Lambda Support**: Convert Lambda functions to MCP tools
- **OAuth Authentication**: Secure API access with OAuth2
- **API Key Support**: Standard API key authentication
- **Semantic Search**: Enable tool discovery via semantic search
- **Fully Managed**: No infrastructure to manage

**Key Benefits:**
- **Smithy Model Support**: Directly convert AWS service APIs (DynamoDB, S3, EC2, Lambda, etc.) to agent tools
- **350+ AWS Services**: Access to AWS-maintained repository of service models
- **No Custom Code**: Just point Gateway to Smithy model (S3 URI or inline)
- **Quick Setup**: Add any AWS service as agent tools with one command

**Use Cases:**
- **AWS Services**: Convert AWS service APIs (EC2, S3, RDS, DynamoDB, etc.) to agent tools using Smithy models
- **Internal APIs**: Expose internal company APIs as agent tools using OpenAPI specs
- **Third-party Services**: Integrate third-party services (Slack, Jira, etc.) via OAuth
- **Custom Tools**: Convert Lambda functions to agent tools

**Why Gateway is Valuable for Your Use Case:**
1. **AWS Service Integration**: Many AWS services use Smithy models - Gateway can convert them directly to tools
2. **Consistency**: Standardize all API access through MCP protocol
3. **Security**: Built-in OAuth and API key management
4. **Discovery**: Semantic search helps agents find the right tools
5. **Scale**: Supports 350+ AWS service models from AWS-maintained repository

**Smithy Model Support** ⭐ **HIGH VALUE**:
- **AWS Services**: 350+ AWS service models available from [aws/api-models-aws](https://github.com/aws/api-models-aws)
- **Direct Integration**: Convert AWS service APIs (DynamoDB, S3, EC2, Lambda, etc.) to MCP tools
- **No Custom Code**: Just point Gateway to Smithy model (S3 URI or inline)
- **Quick Setup**: Add DynamoDB operations as agent tools with one command
- **Example Use Case**: Add DynamoDB operations, S3 operations, or any AWS service API as agent tools

**Example Use Case:**
```python
# Add DynamoDB operations as agent tools with one command
smithy_target = client.create_mcp_gateway_target(
    gateway=gateway,
    target_type="smithyModel"
)
# Now agent can use DynamoDB operations as tools!
```

**When to Use:**
- Adding AWS service APIs as agent tools (DynamoDB, S3, EC2, etc.)
- Exposing internal company APIs as agent tools
- Integrating with third-party services (Slack, Jira, etc.)
- Standardizing API access through MCP protocol

**Integration Points:**
- Create Gateway with OAuth authorization (using Cognito)
- Add targets (OpenAPI, Smithy, Lambda)
- Configure credentials (API keys, OAuth, Gateway IAM Role)
- Connect agent to Gateway via MCP client

**Scripts Required:**
- `gateway/gateway_setup.py` - Gateway creation and configuration
- `gateway/smithy_target_setup.py` - AWS service integration via Smithy
- `gateway/openapi_target_setup.py` - OpenAPI API integration
- `gateway/gateway_client.py` - Gateway client wrapper for agent

**Current Status**: Recommended for Phase 2 to enhance agent capabilities with AWS service APIs

---

### Module 6: Code Interpreter & Browser (Optional - Future)

**Purpose**: Secure code execution and web interaction

**Use Case**: If your agent needs to execute Python code or browse web pages

**Current Status**: Not required for cloud engineering tasks, but can enhance capabilities

---

## Complete AgentCore Functionalities Summary

### Core Modules (Required - Phase 1)

| Module | Status | Purpose | Key Benefit |
|--------|--------|---------|-------------|
| **Runtime** | ✅ Required | Serverless deployment, scaling, session isolation | Multi-user support with isolation |
| **Memory** | ✅ Required | Conversation persistence, context awareness | Persistent conversation history |
| **Identity** | ✅ Required | Authentication, Cognito integration | Secure user authentication |
| **Observability** | ✅ Required | Monitoring, tracing, debugging | Complete visibility |
| **Guardrails** | ✅ Required | Content safety, compliance | Enterprise compliance |

### Optional Modules (Future - Phase 2+)

| Module | Status | Purpose | Key Benefit |
|--------|--------|---------|-------------|
| **Gateway** | ⏸️ Recommended | API transformation to tools, Smithy support | Expand agent capabilities |
| **Code Interpreter** | ⏸️ Optional | Secure code execution | Code execution capability |
| **Browser** | ⏸️ Optional | Web browsing capability | Web interaction |

### Enterprise Features Summary

1. **Multi-User Support**: 100+ concurrent users with session isolation
2. **Security & Authentication**: Cognito + Guardrails + session isolation
3. **Persistent Memory**: Conversation history and context awareness
4. **Observability**: Complete tracing and debugging
5. **Content Safety**: Guardrails for compliance
6. **Scalability**: Auto-scales from 1 to 1000+ users automatically

---

## Project Structure

> **📌 NEWBIE GUIDE**: 
> - **For step-by-step execution with AWS Console verification**: See **[NEWBIE_SETUP_GUIDE.md](./NEWBIE_SETUP_GUIDE.md)** ⭐ **START HERE FOR DETAILED SETUP!**
> - **For project structure and flow**: See **[GETTING_STARTED.md](./GETTING_STARTED.md)** - This explains how everything works together

### Complete Directory Structure

```
maygum-agentcore/
├── README.md                          # Project overview
├── GETTING_STARTED.md                 # Project overview and flow guide
├── NEWBIE_SETUP_GUIDE.md              # ⭐ STEP-BY-STEP SETUP GUIDE: Detailed execution with AWS Console verification
├── IMPLEMENTATION_PLAN.md             # Detailed implementation plan
├── MODULAR_STRUCTURE_PLAN.md          # Modular structure plan
├── requirements.txt                    # Python dependencies
├── .env.example                       # Configuration template
├── .env                               # Your configuration (create this)
├── .gitignore                         # Git ignore rules
│
├── agents/                             # ⭐ NEW: Modular agents
│   ├── __init__.py                    # Package marker (exports)
│   └── cloud_engineer_agent.py        # Main agent (moved from root)
│
├── prompts/                            # ⭐ NEW: Modular prompts
│   ├── __init__.py                    # Package marker (exports)
│   └── cloud_engineer/                # Cloud engineer agent prompts
│       ├── __init__.py
│       ├── system_prompt.py            # System prompt
│       └── predefined_tasks.py       # Predefined tasks dictionary
│
├── scripts/                           # Automation scripts
│   ├── deploy_all.py                  # One-command deployment
│   ├── deploy_all.sh                  # Shell version
│   ├── quick_start.sh                 # Interactive quick start
│   ├── setup_aws_resources.py         # AWS resource creation
│   ├── verify_cognito.py              # Cognito verification
│   ├── validate_environment.py        # Environment validation
│   ├── setup_guardrails.py            # Guardrail creation
│   ├── setup_agentcore_resources.py   # Memory & Identity setup
│   ├── test_deployment.py             # Deployment testing
│   ├── update_config.py               # Config file updates
│   └── rollback.py                    # Rollback procedures
│
├── runtime/                           # Agent runtime code
│   ├── agent_runtime.py               # Main runtime wrapper
│   ├── session_handler.py             # Session management
│   ├── request_validator.py           # Input validation
│   ├── memory_integration.py          # Memory integration
│   ├── guardrail_integration.py       # Guardrail integration
│   ├── context_builder.py              # Context building
│   ├── Dockerfile                     # Container definition
│   ├── build_and_push.sh              # Build & push script
│   ├── deploy_runtime.py              # Runtime deployment
│   └── test_runtime_local.py          # Local testing
│
├── memory/                            # Memory integration
│   ├── memory_manager.py              # Memory operations wrapper
│   ├── memory_config.py               # Memory configuration
│   ├── session_memory_handler.py      # Session-specific memory
│   ├── semantic_search.py             # Semantic search
│   └── memory_test.py                 # Memory testing
│
├── identity/                          # Identity & Auth
│   ├── cognito_integration.py         # Cognito setup
│   ├── jwt_validator.py               # JWT validation
│   ├── workload_identity_manager.py   # Workload identity
│   └── user_mapper.py                 # User mapping
│
├── auth/                              # Authentication
│   ├── cognito_verification.py       # Cognito verification
│   ├── cognito_client.py              # Cognito client wrapper
│   └── test_auth.py                   # Auth testing
│
├── frontend/                          # Streamlit UI
│   ├── app.py                         # Main Streamlit app (enhanced)
│   ├── auth_ui.py                     # Authentication UI
│   ├── cognito_client.py              # Cognito client for Streamlit
│   ├── agent_client.py                # AgentCore Runtime client
│   ├── chat_interface.py              # Chat interface
│   ├── session_manager.py             # Session management
│   ├── protected_route.py             # Route protection
│   ├── user_info.py                   # User info display
│   └── conversation_history.py       # History viewer
│
├── observability/                     # Monitoring
│   ├── otel_config.py                 # OpenTelemetry config
│   ├── instrumentation_setup.py       # Instrumentation setup
│   ├── session_correlation.py         # Session correlation
│   ├── metrics_collector.py           # Custom metrics
│   ├── dashboard_setup.py             # Dashboard creation
│   ├── cloudwatch_setup.py            # CloudWatch config
│   ├── alarms_setup.py                # Alarms configuration
│   └── guardrail_dashboard.py         # Guardrail dashboard
│
├── guardrails/                        # Guardrails
│   ├── guardrail_setup.py             # Guardrail creation
│   ├── guardrail_config.py            # Configuration definitions
│   ├── guardrail_validator.py         # Validation & testing
│   ├── guardrail_monitor.py           # Monitoring
│   └── guardrail_analyzer.py          # Analysis tool
│
├── gateway/                           # Gateway (Phase 2)
│   ├── gateway_setup.py               # Gateway creation
│   ├── smithy_target_setup.py         # Smithy integration
│   ├── openapi_target_setup.py        # OpenAPI integration
│   └── gateway_client.py              # Gateway client wrapper
│
├── infrastructure/                     # Infrastructure as Code
│   └── cloudformation_base_resources.yaml  # CloudFormation template
│
├── tests/                             # Test files
│   ├── unit/                          # Unit tests
│   │   ├── test_memory_manager.py
│   │   ├── test_jwt_validator.py
│   │   └── test_agent_runtime.py
│   ├── integration/                   # Integration tests
│   │   ├── test_cognito_integration.py
│   │   ├── test_memory_integration.py
│   │   └── test_runtime_integration.py
│   └── e2e/                           # End-to-end tests
│       ├── test_auth_flow.py
│       ├── test_agent_flow.py
│       └── test_multi_user.py
│
├── docs/                              # Documentation
│   ├── setup-guide.md                 # Detailed setup guide
│   ├── troubleshooting.md             # Troubleshooting guide
│   ├── api-reference.md              # API documentation
│   └── deployment-guide.md            # Deployment guide
│
└── cloud_engineer_agent.py           # ⚠️ DEPRECATED: Moved to agents/cloud_engineer_agent.py
```

### Modular Structure Explained ⭐ **NEW**

The project now uses a **modular structure** for easier maintenance and extensibility:

**Agents Folder (`agents/`):**
- Contains all agent implementations
- `agents/cloud_engineer_agent.py` - Main cloud engineer agent (moved from root)
- Easy to add new agents: Just create a new file in `agents/`
- Simple imports: `from agents.cloud_engineer_agent import execute_custom_task`

**Prompts Folder (`prompts/`):**
- Contains all agent prompts and predefined tasks
- `prompts/cloud_engineer/system_prompt.py` - System prompt
- `prompts/cloud_engineer/predefined_tasks.py` - Predefined tasks dictionary
- Easy to update prompts without modifying agent code
- Simple imports: `from prompts.cloud_engineer.system_prompt import get_system_prompt`

**Benefits:**
- ✅ Easy to add new agents without modifying existing code
- ✅ Clear separation: agents vs prompts vs runtime
- ✅ Simple direct imports (no complex patterns)
- ✅ Strands-friendly: Works directly with Strands Agent pattern

See **[NEWBIE_SETUP_GUIDE.md](./NEWBIE_SETUP_GUIDE.md)** for detailed step-by-step execution with AWS Console verification. See **[GETTING_STARTED.md](./GETTING_STARTED.md)** for project flow and architecture overview.

### File Organization Rules

1. **Agents**: All agent implementations go in `agents/` directory
2. **Prompts**: All prompts go in `prompts/` directory (organized by agent)
3. **Scripts**: All automation scripts go in `scripts/` directory
4. **Runtime**: Agent runtime code goes in `runtime/` directory
5. **Frontend**: Streamlit UI code goes in `frontend/` directory
6. **Configuration**: `.env` file goes at root level
7. **Tests**: All tests go in `tests/` directory organized by type
8. **Documentation**: Additional docs go in `docs/` directory or root level

### Key Files to Create First

1. **requirements.txt** - Python dependencies (see Prerequisites section)
2. **.env.example** - Configuration template (see Configuration Files section)
3. **.env** - Your configuration (create from .env.example)
4. **.gitignore** - Git ignore rules (exclude .env, .venv, etc.)

---

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

#### 1.1 Environment Preparation

**Objective**: Set up development environment and AWS resources

**Tasks:**
1. **Create/Verify Cognito User Pool**
   - **Cognito User Pool**: Create new User Pool OR verify existing one
   - **Cognito Client**: Create app client for Streamlit authentication
   - Configure password policies, MFA options, user attributes
   - Set up OAuth flows (Authorization code flow)
   - Configure callback URLs for Streamlit app

2. **Development Environment**
   - Install `bedrock-agentcore` SDK
   - Install `bedrock-agentcore-starter-toolkit` (optional)
   - Install `aws-opentelemetry-distro` for observability
   - Set up Python virtual environment
   - Configure AWS credentials for us-east-2 region

**Scripts to Create:**
- `scripts/setup_aws_resources.py` - Automated AWS resource creation
- `scripts/create_cognito_pool.py` - Create Cognito User Pool (if not exists)
- `scripts/verify_cognito.py` - Verify and configure Cognito User Pool
- `scripts/create_guardrail.py` - Create Bedrock Guardrail (standalone)
- `scripts/setup_guardrails.py` - Automated guardrail creation with defaults
- `scripts/create_agentcore_identity.py` - Create Workload Identity (standalone)
- `scripts/create_agentcore_memory.py` - Create Memory resource (standalone)
- `scripts/setup_agentcore_resources.py` - Combined Identity + Memory setup
- `scripts/list_agentcore_resources.py` - List all AgentCore resources
- `scripts/verify_agentcore_resources.py` - Verify all resources exist
- `scripts/get_resource_status.py` - Get detailed resource status
- `scripts/cleanup_resources.py` - Cleanup/destroy resources
- `scripts/deploy_all.sh` / `scripts/deploy_all.py` - One-command deployment script
- `scripts/validate_environment.py` - Environment validation script
- `scripts/rollback.py` - Rollback script for failures
- `scripts/test_deployment.py` - Deployment testing script
- `scripts/test_scalability.py` - Scalability testing script
- `scripts/deploy_streamlit_production.py` - Streamlit production deployment
- `scripts/setup_domain.py` - Domain name setup script

**Documentation Required:**
- Environment setup guide with prerequisites
- AWS resource naming conventions
- IAM role permissions matrix
- Cognito User Pool integration guide (for existing pool)

#### 1.2 Cognito User Pool Creation/Verification

**Objective**: Create Cognito User Pool or verify existing one

**Tasks:**
1. **Create Cognito User Pool (if not exists)**
   - Create user pool with email/password authentication
   - Configure password policies (min 8 chars, complexity required)
   - Set up user attributes (email, sub, groups, custom attributes)
   - Configure token expiration (1 hour access, 30 days refresh)
   - Enable MFA (optional, can be enabled later)

2. **Create Cognito User Pool Client**
   - Create app client for Streamlit authentication
   - Configure OAuth flows: Authorization code flow
   - Set callback URLs:
     - Development: `http://localhost:8501`
     - Production: `https://your-domain.com` (will be configured later)
   - Enable identity provider (Cognito)
   - Generate client secret if required
   - Note client ID and secret for integration

3. **Create Test Users**
   - Create test users via script or AWS Console
   - Verify users can authenticate
   - Test password reset flow (if enabled)

**Scripts to Create:**
- `scripts/create_cognito_pool.py` - Create Cognito User Pool if not exists
- `scripts/verify_cognito.py` - Verify existing Cognito configuration
- `auth/cognito_client.py` - Cognito client wrapper for Streamlit
- `auth/test_auth.py` - Authentication testing script

**Script Functionality (`scripts/create_cognito_pool.py`):**
```python
# Functionality:
# - Check if user pool exists by name
# - If not exists: Create new user pool with:
#   - Email/password authentication
#   - Password policies
#   - Token expiration settings
#   - User attributes
# - Create app client
# - Configure OAuth flows
# - Set callback URLs
# - Generate and return client ID and secret
# - Save configuration to .env file
```

**Documentation Required:**
- Cognito User Pool creation guide
- Client configuration guide
- JWT token structure documentation
- Authentication flow diagram
- Test user creation guide

---

### Phase 2: Agent Runtime Migration (Week 2-3)

#### 2.1 Agent Wrapper Implementation

**Objective**: Wrap existing Strands Agent with AgentCore Runtime SDK

**Tasks:**
1. **Create Agent Runtime Wrapper**
   - Wrap `cloud_engineer_agent.py` agent with `BedrockAgentCoreApp`
   - Implement `/invocations` endpoint handler
   - Implement `/ping` health check endpoint
   - Add session ID extraction from request context
   - Preserve all existing agent functionality

2. **Request/Response Handling**
   - Extract user input from payload
   - Handle agent response formatting
   - Manage errors gracefully
   - Support both sync and async operations

3. **Session Management Integration**
   - Extract session ID from AgentCore Runtime context
   - Map Cognito user ID to session ID
   - Store session metadata

**Scripts to Create:**
- `runtime/agent_runtime.py` - Main runtime wrapper
- `runtime/session_handler.py` - Session management logic
- `runtime/request_validator.py` - Input validation

**Documentation Required:**
- Agent runtime architecture document
- Session management flow diagram
- Error handling strategy

#### 2.2 AgentCore Runtime Deployment (Using AgentCore CLI)

**Objective**: Deploy agent to AgentCore Runtime using automated CLI

**Key Point**: ⭐ **NO Dockerfile Required!** AgentCore CLI uses AWS CodeBuild to build containers automatically.

**Tasks:**
1. **Configure Agent with AgentCore CLI**
   - Run `agentcore configure` command
   - Specify entrypoint file (`runtime/agent_runtime.py`)
   - Configure OAuth with Cognito
   - Configure memory (STM + LTM)
   - Accept defaults for execution role and ECR repository (auto-created)

2. **Deploy to AgentCore Runtime**
   - Run `agentcore launch` command
   - **Automatic steps performed by CLI:**
     - Container build via AWS CodeBuild (ARM64 architecture)
     - ECR repository creation (if needed)
     - Container image push to ECR
     - AgentCore Runtime creation
     - Memory resource creation
     - CloudWatch logging setup
     - Observability configuration

3. **Verify Deployment**
   - Check status with `agentcore status`
   - Test invocation with `agentcore invoke`
   - Verify logs in CloudWatch

**Scripts to Create:**
- `runtime/agent_runtime.py` - Agent wrapper (required)
- `runtime/test_runtime_local.py` - Local testing script (optional)

**Note**: Dockerfile is NOT needed unless using `--local` or `--local-build` flags. Default deployment uses CodeBuild in the cloud.

**Documentation Required:**
- AgentCore CLI usage guide
- Configuration parameters reference
- Deployment checklist
- Troubleshooting guide

---

### Phase 3: Memory Integration (Week 3-4)

#### 3.1 Memory Resource Setup

**Objective**: Create and configure AgentCore Memory resources

**Tasks:**
1. **Memory Resource Creation**
   - Create memory resource with event-based strategy
   - Configure user isolation (separate memory per user)
   - Set up retention policies
   - Configure memory access permissions

2. **Memory Manager Implementation**
   - Create wrapper class for memory operations
   - Implement write operations (store conversations)
   - Implement read operations (retrieve context)
   - Handle memory errors gracefully

3. **Session Memory Integration**
   - Store each agent interaction in memory
   - Retrieve conversation history for context
   - Implement semantic search for knowledge queries
   - Manage memory size and cleanup

**Scripts to Create:**
- `memory/memory_manager.py` - Memory operations wrapper
- `memory/memory_config.py` - Memory configuration
- `memory/session_memory_handler.py` - Session-specific memory operations
- `memory/memory_test.py` - Memory functionality testing

**Documentation Required:**
- Memory architecture document
- Memory storage schema
- Memory retrieval strategies
- Memory cleanup policies

#### 3.2 Agent Memory Integration

**Objective**: Integrate memory into agent workflow

**Tasks:**
1. **Pre-Request Memory Retrieval**
   - Retrieve user's conversation history
   - Load relevant context into agent system prompt
   - Include previous interactions in context

2. **Post-Response Memory Storage**
   - Store user query and agent response
   - Store metadata (timestamp, session ID, user ID)
   - Store relevant context for future retrieval

3. **Semantic Memory Implementation**
   - Store important knowledge from conversations
   - Enable semantic search for similar past queries
   - Implement knowledge base from user interactions

**Scripts to Create:**
- `runtime/memory_integration.py` - Memory integration in agent
- `runtime/context_builder.py` - Build context from memory
- `memory/semantic_search.py` - Semantic search implementation

**Documentation Required:**
- Memory integration flow diagram
- Context building strategy
- Semantic search usage guide

---

### Phase 4: Identity & Authentication (Week 4-5)

#### 4.1 AgentCore Identity Setup

**Objective**: Configure AgentCore Identity with Cognito

**Tasks:**
1. **Workload Identity Creation**
   - Create workload identity for agent runtime
   - Configure allowed OAuth2 return URLs
   - Set up identity metadata

2. **OAuth2 Credential Provider**
   - Create OAuth2 provider pointing to Cognito
   - Configure discovery URL from Cognito
   - Set up client ID and scopes
   - Configure callback URLs

3. **JWT Token Validation**
   - Implement JWT token validation using Cognito
   - Verify token signature and expiration
   - Extract user information from token
   - Map user to session

**Scripts to Create:**
- `identity/workload_identity_setup.py` - Workload identity creation
- `identity/oauth2_provider_setup.py` - OAuth2 provider configuration
- `identity/jwt_validator.py` - JWT validation logic
- `identity/user_mapper.py` - User ID to session mapping

**Documentation Required:**
- Identity setup guide
- JWT token validation flow
- User mapping strategy

#### 4.2 Streamlit Authentication Integration

**Objective**: Add authentication to Streamlit frontend

**Tasks:**
1. **Cognito Client Integration**
   - Create Cognito client wrapper for Streamlit
   - Implement login page
   - Implement token refresh logic
   - Handle authentication state

2. **Session Management**
   - Store authentication tokens in Streamlit session state
   - Implement token expiration handling
   - Redirect to login on authentication failure
   - Maintain user session across Streamlit reruns

3. **Protected Routes**
   - Protect main application routes
   - Show login page for unauthenticated users
   - Display user information in UI
   - Implement logout functionality

**Scripts to Create:**
- `frontend/auth_ui.py` - Authentication UI components
- `frontend/cognito_client.py` - Cognito client wrapper
- `frontend/session_manager.py` - Streamlit session management
- `frontend/protected_route.py` - Route protection decorator

**Documentation Required:**
- Authentication flow diagram
- Token management guide
- UI component documentation

---

### Phase 5: Observability Integration (Week 5-6)

#### 5.1 OpenTelemetry Setup

**Objective**: Configure OpenTelemetry instrumentation

**Tasks:**
1. **OTEL Configuration**
   - Install `aws-opentelemetry-distro`
   - Install `strands-agents[otel]` with OTEL support
   - Configure OTEL environment variables
   - Set up CloudWatch log group and stream

2. **Agent Instrumentation**
   - Enable automatic instrumentation for Strands Agent
   - Enable instrumentation for Bedrock calls
   - Enable instrumentation for MCP tools
   - Add custom spans for agent operations

3. **Session Correlation**
   - Add session ID to OTEL baggage
   - Propagate session ID across spans
   - Add user ID to span attributes
   - Enable trace correlation

**Scripts to Create:**
- `observability/otel_config.py` - OpenTelemetry configuration
- `observability/instrumentation_setup.py` - Instrumentation setup
- `observability/session_correlation.py` - Session correlation logic

**Documentation Required:**
- OpenTelemetry configuration guide
- Instrumentation setup instructions
- Trace correlation documentation

#### 5.2 CloudWatch Integration

**Objective**: Set up CloudWatch monitoring and dashboards

**Tasks:**
1. **Transaction Search Setup**
   - Enable CloudWatch Transaction Search (one-time)
   - Configure span ingestion settings
   - Set up trace indexing percentage

2. **Metrics Collection**
   - Configure automatic metrics collection
   - Set up custom metrics for agent operations
   - Configure token usage tracking
   - Set up error rate monitoring

3. **Dashboard Creation**
   - Create GenAI Observability dashboard
   - Set up agent-specific metrics dashboard
   - Create session monitoring dashboard
   - Configure alerts for critical metrics

**Scripts to Create:**
- `observability/cloudwatch_setup.py` - CloudWatch configuration
- `observability/dashboard_creator.py` - Dashboard creation script
- `observability/alarms_setup.py` - CloudWatch alarms configuration
- `observability/metrics_collector.py` - Custom metrics collection

**Documentation Required:**
- CloudWatch setup guide
- Dashboard configuration guide
- Alarms and alerting strategy

---

### Phase 6: Streamlit UI Enhancement (Week 6)

#### 6.1 UI Authentication Integration

**Objective**: Integrate authentication into Streamlit UI

**Tasks:**
1. **Login Page**
   - Create login form with Cognito integration
   - Handle login errors gracefully
   - Redirect to main app on success
   - Show loading states

2. **Main App Enhancement**
   - Add user information display
   - Add logout button
   - Show session information
   - Display user's conversation history

3. **Session Management**
   - Maintain user session across reruns
   - Handle token refresh automatically
   - Clear session on logout
   - Handle authentication errors

**Scripts to Create:**
- `frontend/login_page.py` - Login page component
- `frontend/main_app.py` - Enhanced main application
- `frontend/user_info.py` - User information display component
- `frontend/conversation_history.py` - Conversation history viewer

**Documentation Required:**
- UI component documentation
- User flow documentation
- Authentication UI guide

#### 6.2 Agent Invocation Integration

**Objective**: Connect Streamlit UI to AgentCore Runtime

**Tasks:**
1. **Agent Invocation Client**
   - Create client for invoking AgentCore Runtime using boto3
   - Handle session ID management (generate per user/conversation)
   - Implement request/response handling
   - Handle errors and retries
   - Support JWT token authentication

2. **UI Integration**
   - Update chat interface to use AgentCore Runtime
   - Maintain conversation history in UI
   - Show loading states during agent processing
   - Display agent responses with formatting
   - Map Streamlit user sessions to AgentCore Runtime sessions

3. **Session Management**
   - Generate unique session IDs per user/conversation
   - Store session IDs in Streamlit session state
   - Handle session timeout (15 minutes)

**Key Implementation:**
- Use boto3 `InvokeAgentRuntime` API
- Pass session ID generated by Streamlit (per user/conversation)
- Pass JWT token from Cognito authentication
- AgentCore Runtime creates microVM automatically per session ID

**Scripts to Create:**
- `frontend/agent_client.py` - AgentCore Runtime client (see Code Examples section)
- `frontend/chat_interface.py` - Enhanced chat interface
- `frontend/response_handler.py` - Response formatting and display
- `frontend/session_manager.py` - Session ID generation and management
- `frontend/streaming_handler.py` - Streaming response handler (if needed)

**Documentation Required:**
- Agent invocation flow diagram
- Client API documentation
- Session management guide
- Error handling guide
- Code examples (see Code Examples section)

---

## Automation Scripts Overview

All automation scripts will be created to streamline the deployment process. These scripts will handle:
- **Cognito Integration**: Verify and configure existing Cognito User Pool
- **AWS Resource Setup**: Create all required AWS resources automatically
- **Guardrails Setup**: Create and configure Bedrock Guardrails
- **AgentCore Resources**: Deploy Memory, Identity, and Runtime resources
- **Environment Validation**: Verify all prerequisites and configurations
- **Deployment Automation**: One-command deployment to production

**Script Locations:**
- `scripts/` - Main automation scripts
- `infrastructure/` - Infrastructure as Code templates
- `scripts/deploy/` - Deployment automation scripts
- `scripts/verify/` - Verification and validation scripts

### Complete Automation Scripts List

**Main Deployment Scripts:**
1. `scripts/deploy_all.sh` / `scripts/deploy_all.py` - **One-command deployment** (orchestrates all scripts)
2. `scripts/quick_start.sh` - Interactive quick start for developers
3. `scripts/setup_aws_resources.py` - Complete AWS resource setup

**Cognito Integration Scripts:**
4. `scripts/create_cognito_pool.py` - Create Cognito User Pool (if not exists)
5. `scripts/verify_cognito.py` - Verify and configure existing Cognito User Pool
6. `auth/cognito_verification.py` - Detailed Cognito verification
7. `auth/cognito_client.py` - Cognito client wrapper

**Guardrails Scripts:**
8. `scripts/create_guardrail.py` - Create Bedrock Guardrail (standalone)
9. `scripts/setup_guardrails.py` - Automated guardrail creation with defaults
10. `guardrails/guardrail_setup.py` - Guardrail configuration
11. `guardrails/guardrail_config.py` - Guardrail configuration definitions
12. `guardrails/guardrail_validator.py` - Guardrail validation

**AgentCore Resource Scripts (Individual):**
13. `scripts/create_agentcore_identity.py` - Create Workload Identity (standalone)
14. `scripts/create_agentcore_memory.py` - Create Memory resource (standalone)
15. `scripts/setup_agentcore_resources.py` - Combined Identity + Memory setup
16. `memory/memory_resource_manager.py` - Memory resource creation logic
17. `memory/memory_manager.py` - Memory operations wrapper
18. `identity/workload_identity_manager.py` - Workload identity management

**Resource Management Scripts:**
19. `scripts/list_agentcore_resources.py` - List all AgentCore resources (Memory, Identity, Runtime)
20. `scripts/verify_agentcore_resources.py` - Verify all resources exist and are configured
21. `scripts/get_resource_status.py` - Get detailed status of specific resource
22. `scripts/cleanup_resources.py` - Cleanup/destroy resources (use with caution!)

**Validation & Testing Scripts:**
23. `scripts/validate_environment.py` - Environment validation
24. `scripts/test_deployment.py` - Deployment testing
25. `scripts/test_scalability.py` - Scalability testing
26. `scripts/update_config.py` - Configuration updates

**Infrastructure Scripts:**
27. `infrastructure/cloudformation_base_resources.yaml` - CloudFormation template
28. `scripts/rollback.py` - Rollback procedures
29. `scripts/deploy_streamlit_production.py` - Streamlit production deployment
30. `scripts/setup_domain.py` - Domain name setup script

**Usage Example:**
```bash
# Quick start (interactive)
./scripts/quick_start.sh

# Or one-command deployment
python scripts/deploy_all.py --cognito-pool-id <your-pool-id> --region us-east-2 --create-memory

# Or step-by-step (recommended for newbies)
python scripts/validate_environment.py
python scripts/create_cognito_pool.py --pool-name my-pool
# OR if pool exists:
python scripts/verify_cognito.py --pool-id <your-pool-id>
python scripts/create_guardrail.py
python scripts/create_agentcore_identity.py
python scripts/create_agentcore_memory.py --enable-ltm
python scripts/setup_aws_resources.py

# Or use combined scripts (faster)
python scripts/setup_guardrails.py
python scripts/setup_agentcore_resources.py --create-memory
python scripts/setup_aws_resources.py

# Verify resources
python scripts/verify_agentcore_resources.py --all
python scripts/list_agentcore_resources.py --resource-type all
```

---

## Step-by-Step Implementation Guide ⭐ **CRITICAL**

> **📌 NEWBIE NOTE**: For **detailed step-by-step execution with AWS Console verification steps and phase achievements**, see **[NEWBIE_SETUP_GUIDE.md](./NEWBIE_SETUP_GUIDE.md)**. This section provides the high-level overview, while NEWBIE_SETUP_GUIDE.md provides the detailed walkthrough.

### Phase 1: Foundation Setup (Week 1)

#### Day 1: Environment Setup

**Already completed in Prerequisites section** ✅

#### Day 2: Verify Cognito & Create Resources

**Step 1: Create or Verify Cognito User Pool**
```bash
# Option A: Create new Cognito User Pool
python scripts/create_cognito_pool.py \
  --pool-name cloud-engineer-agent-pool \
  --region us-east-2

# Expected Output:
✅ User Pool created: <pool-id>
✅ App client created: <client-id>
✅ Configuration saved to .env

# Option B: Verify existing Cognito User Pool
python scripts/verify_cognito.py --pool-id <your-existing-pool-id>

# Expected Output:
✅ User Pool found: <pool-id>
✅ Password policy verified
✅ User attributes verified
✅ App client found/created: <client-id>
Configuration saved to: cognito_config.json

# If errors:
# - Verify pool ID: aws cognito-idp list-user-pools --region us-east-2
# - Check IAM permissions for Cognito
# - Run create script if pool doesn't exist
```

**Step 2: Validate Environment**
```bash
# Command:
python scripts/validate_environment.py

# Expected Output:
✅ AWS credentials configured
✅ Region us-east-2 accessible
✅ Bedrock access verified
✅ Cognito User Pool accessible
✅ Python dependencies installed

# If errors:
# - Fix AWS credentials: aws configure
# - Enable Bedrock access: AWS Console → Bedrock → Model access
# - Install missing dependencies: pip install <package>
```

**Step 3: Create AWS Resources**
```bash
# Command:
python scripts/setup_aws_resources.py \
  --cognito-pool-id <your-pool-id> \
  --region us-east-2

# Expected Output:
✅ IAM role created: cloud-engineer-agent-runtime-role
✅ ECR repository created: cloud-engineer-agent (for AgentCore Runtime)
✅ CloudWatch log groups created
✅ Guardrail created: <guardrail-id>
Configuration saved to: .env

# Note: Memory and Identity resources are created by `agentcore launch` command
# NOT by this script - AgentCore CLI handles them automatically

# Expected Duration: 5-10 minutes

# If errors:
# - Check IAM permissions
# - Verify region is correct
# - Check service quotas
# - Review CloudWatch logs
```

**Step 4: Verify Resources Created**
```bash
# Verify IAM role
aws iam get-role --role-name cloud-engineer-agent-runtime-role
# Expected: Returns role ARN

# Verify ECR repository
aws ecr describe-repositories --repository-names cloud-engineer-agent
# Expected: Returns repository URI

# Verify Guardrail
aws bedrock get-guardrail --guardrailIdentifier <guardrail-id>
# Expected: Returns guardrail details

# Note: Memory resource will be created by `agentcore launch` command
# No need to verify separately at this step
```

#### Day 3-4: Configure & Deploy Runtime Using AgentCore CLI

**Step 5: Wrap Agent with AgentCore Runtime SDK**

Create `runtime/agent_runtime.py` (see Code Examples section for template):
```bash
# Edit runtime/agent_runtime.py
# Import your existing agent from cloud_engineer_agent.py
# Wrap with BedrockAgentCoreApp
```

**Step 6: Configure Agent with AgentCore CLI**

```bash
# Install AgentCore starter toolkit (if not already installed)
pip install bedrock-agentcore-starter-toolkit

# Configure agent for deployment
agentcore configure -e runtime/agent_runtime.py --region us-east-2

# Interactive prompts:
# 1. Execution Role: Press Enter to auto-create
# 2. ECR Repository: Press Enter to auto-create
# 3. Requirements File: Confirm requirements.txt
# 4. OAuth Configuration: Type 'yes' (we'll configure Cognito)
#    - Discovery URL: https://cognito-idp.us-east-2.amazonaws.com/<pool-id>/.well-known/openid-configuration
#    - Client ID: <your-cognito-client-id>
# 5. Request Header Allowlist: Type 'no'
# 6. Memory Configuration: Type 'yes' (enable memory)
#    - Enable long-term memory? Type 'yes'

# Expected Output:
✅ Configuration saved to .bedrock_agentcore.yaml
✅ Memory resource will be created during launch
✅ Runtime will be configured with Cognito OAuth

# Note: This creates .bedrock_agentcore.yaml config file
# NO Dockerfile needed - AgentCore CLI handles containerization automatically!
```

**Step 7: Deploy to AgentCore Runtime**

```bash
# Deploy agent (uses CodeBuild - no Docker needed locally!)
agentcore launch

# This command automatically:
# 1. Builds container using AWS CodeBuild (ARM64 architecture)
# 2. Creates ECR repository if needed
# 3. Pushes container image to ECR
# 4. Creates AgentCore Runtime
# 5. Creates Memory resource (if configured)
# 6. Configures CloudWatch logging
# 7. Enables observability (if configured)

# Expected Output:
✅ Memory resource created: <memory-id>
✅ Memory is ACTIVE
✅ Container built and pushed to ECR
✅ AgentCore Runtime created: <runtime-arn>
✅ Transaction Search configured
✅ GenAI Observability Dashboard: <dashboard-url>

# Save the Runtime ARN - you'll need it for Streamlit integration!

# Expected Duration: 5-15 minutes (including memory provisioning)

# If errors:
# - Check IAM permissions (CodeBuild, ECR, Bedrock AgentCore)
# - Verify region is correct
# - Check CloudWatch logs: aws logs tail /aws/bedrock-agentcore/runtimes --follow
# - Verify Bedrock model access is enabled
```

**Step 8: Verify Runtime Deployment**

```bash
# Check runtime status
agentcore status

# Expected Output:
✅ Runtime: ACTIVE
✅ Memory: ACTIVE (STM+LTM)
✅ Observability: Enabled

# Test runtime invocation
agentcore invoke '{"prompt": "Hello, test message"}'

# Expected Output:
{"response": "Hello! How can I help you..."}

# If errors:
# - Wait a few minutes for memory to fully provision
# - Check runtime ARN is correct
# - Verify IAM role permissions
# - Check CloudWatch logs for detailed errors
```

**Step 9: Verify Runtime Deployment**
```bash
# Get runtime status
aws bedrock-agentcore-control get-runtime \
  --runtimeIdentifier <runtime-id>

# Expected: Returns runtime with status = ACTIVE

# Test runtime health (if endpoint available)
# Runtime endpoint will be in .env file as AGENT_RUNTIME_ENDPOINT
curl -X GET https://<runtime-endpoint>/ping
# Expected: {"status": "healthy"} or similar
```

### Phase 2: Integration & Testing (Week 2-3)

#### Day 5-7: Memory Integration

**Step 10: Test Memory Operations**
```bash
# Test memory write
python -c "
from memory.memory_manager import MemoryManager
import os
m = MemoryManager(memory_arn=os.environ['MEMORY_RESOURCE_ARN'])
m.write_event('test-user', 'test-session', 'Hello', 'Hi there')
print('✅ Memory write successful')
"

# Test memory read
python -c "
from memory.memory_manager import MemoryManager
import os
m = MemoryManager(memory_arn=os.environ['MEMORY_RESOURCE_ARN'])
events = m.read_events('test-user', 'test-session', limit=10)
print(f'✅ Memory read successful: {len(events)} events')
"
```

**Step 11: Integrate Memory into Agent**
```bash
# Update agent runtime to use memory
# Edit runtime/agent_runtime.py
# Add memory integration code (see code examples section)

# Test integration
python runtime/test_runtime_local.py
# Expected: Agent responses stored in memory
```

#### Day 8-10: Authentication Integration

**Step 12: Test Cognito Authentication**
```bash
# Test authentication flow
python auth/test_auth.py

# Expected Output:
✅ Authentication successful
✅ Token received: <token>
✅ Token validation successful

# If errors:
# - Verify Cognito User Pool ID
# - Check app client configuration
# - Verify user exists in pool
```

**Step 13: Update Streamlit with Authentication**
```bash
# Edit frontend/app.py
# Add authentication components (see code examples)

# Test locally
streamlit run frontend/app.py --server.port 8501

# Expected: Login page appears for unauthenticated users
# Expected: Main app appears after login
```

### Phase 3: Testing & Validation (Week 3-4)

**Step 14: Run Tests**
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest

# Expected: All tests pass
```

**Step 15: End-to-End Testing**
```bash
# Run E2E test suite
pytest tests/e2e/

# Test with multiple users
python tests/e2e/test_multi_user.py

# Expected: All E2E tests pass
```

### Quick Reference: Commands Summary

```bash
# Day 1: Setup
python scripts/validate_environment.py
python scripts/verify_cognito.py --pool-id <pool-id>

# Day 2: Create Resources
python scripts/setup_aws_resources.py --cognito-pool-id <pool-id>

# Day 3: Build & Deploy
cd runtime
docker build -t cloud-engineer-agent .
docker tag cloud-engineer-agent:latest <ecr-uri>
docker push <ecr-uri>
cd ..
python runtime/deploy_runtime.py

# Day 4: Verify
aws bedrock-agentcore-control get-runtime --runtimeIdentifier <id>
python runtime/test_runtime_local.py

# Day 5+: Integration
python auth/test_auth.py
streamlit run frontend/app.py
pytest
```

---

## Detailed Script & Component Documentation

### Script 1: `runtime/agent_runtime.py`

**Purpose**: Main agent runtime wrapper that integrates existing Strands Agent with AgentCore Runtime SDK

**Functionality:**
- Initialize `BedrockAgentCoreApp` instance
- Create entrypoint handler decorated with `@app.entrypoint`
- Extract user input from payload
- Invoke existing Strands Agent (from `cloud_engineer_agent.py`)
- Handle agent response and format for return
- Extract session ID from `RequestContext`
- Handle errors and exceptions gracefully
- Support both sync and async operations

**Key Components:**
- Agent initialization (preserve existing agent setup)
- Request payload parsing
- Session ID extraction
- Response formatting
- Error handling

**Input/Output:**
- Input: JSON payload with `prompt` or `message` field
- Output: JSON response with agent message and metadata

**Dependencies:**
- `bedrock_agentcore.runtime.BedrockAgentCoreApp`
- `bedrock_agentcore.runtime.context.RequestContext`
- Existing `cloud_engineer_agent.py` agent

**Documentation Requirements:**
- Detailed code comments explaining each section
- Error handling strategy documentation
- Response format specification
- Session management explanation

---

### Script 2: `memory/memory_manager.py`

**Purpose**: Wrapper class for AgentCore Memory operations

**Functionality:**
- Initialize memory client with memory resource ARN
- Write events to memory (store conversations)
- Read events from memory (retrieve conversation history)
- Implement semantic search for knowledge queries
- Handle memory errors and retries
- Manage memory resource lifecycle

**Key Methods:**
- `write_event(user_id, session_id, message, response)` - Store conversation
- `read_events(user_id, session_id, limit)` - Retrieve conversation history
- `semantic_search(user_id, query, limit)` - Semantic search in memory
- `clear_session(user_id, session_id)` - Clear session memory

**Configuration:**
- Memory resource ARN
- Event retention policy
- Search parameters

**Documentation Requirements:**
- API reference for all methods
- Memory schema documentation
- Usage examples
- Error handling guide

---

### Script 3: `identity/cognito_integration.py`

**Purpose**: Cognito User Pool setup and integration

**Functionality:**
- Create Cognito User Pool (if not exists)
- Create Cognito User Pool Client
- Configure password policies
- Set up user attributes
- Create test users
- Handle Cognito API calls

**Key Methods:**
- `create_user_pool(pool_name, config)` - Create user pool
- `create_user_pool_client(pool_id, client_name, config)` - Create client
- `create_user(email, password, attributes)` - Create user
- `authenticate_user(email, password)` - Authenticate and get tokens
- `validate_token(token)` - Validate JWT token

**Configuration:**
- User pool name and configuration
- Client configuration
- Attribute schema

**Documentation Requirements:**
- Cognito setup guide
- Token structure documentation
- Authentication flow diagram
- User management guide

---

### Script 4: `identity/jwt_validator.py`

**Purpose**: JWT token validation for Cognito tokens

**Functionality:**
- Validate JWT token signature using Cognito public keys
- Verify token expiration
- Verify token issuer and audience
- Extract user information from token
- Handle token refresh

**Key Methods:**
- `validate_token(token)` - Validate JWT token
- `extract_user_info(token)` - Extract user information
- `get_cognito_public_keys()` - Fetch Cognito public keys
- `is_token_expired(token)` - Check token expiration

**Security Considerations:**
- Cache Cognito public keys
- Verify token signature
- Check token expiration
- Validate audience and issuer

**Documentation Requirements:**
- Token validation flow
- Security best practices
- Error handling guide

---

### Script 5: `identity/workload_identity_manager.py`

**Purpose**: Manage AgentCore Identity workload identities

**Functionality:**
- Create workload identity for agent runtime
- Configure OAuth2 return URLs
- Get workload access token
- Integrate with Cognito for user authentication

**Key Methods:**
- `create_workload_identity(name, callback_urls)` - Create workload identity
- `get_workload_access_token(workload_name, user_token)` - Get access token
- `update_workload_identity(name, callback_urls)` - Update workload identity

**Configuration:**
- Workload identity name
- Allowed OAuth2 return URLs

**Documentation Requirements:**
- Workload identity setup guide
- Token flow documentation
- Integration with Cognito guide

---

### Script 6: `observability/otel_config.py`

**Purpose**: OpenTelemetry configuration and setup

**Functionality:**
- Configure OpenTelemetry environment variables
- Set up AWS Distro for OpenTelemetry
- Configure CloudWatch exporters
- Set up service name and resource attributes
- Enable automatic instrumentation

**Configuration:**
- Service name
- CloudWatch log group and stream
- Trace sampling percentage
- Resource attributes

**Documentation Requirements:**
- OTEL configuration guide
- Environment variables reference
- Instrumentation setup instructions

---

### Script 7: `observability/dashboard_creator.py`

**Purpose**: Create CloudWatch dashboards for monitoring

**Functionality:**
- Create GenAI Observability dashboard
- Create agent-specific metrics dashboard
- Create session monitoring dashboard
- Configure custom widgets
- Set up dashboard refresh intervals

**Key Dashboards:**
- Agent performance dashboard
- Session monitoring dashboard
- Error tracking dashboard
- Token usage dashboard

**Documentation Requirements:**
- Dashboard configuration guide
- Metrics reference
- Customization guide

---

### Script 8: `frontend/auth_ui.py`

**Purpose**: Authentication UI components for Streamlit

**Functionality:**
- Create login form component
- Handle login submission
- Display authentication errors
- Show loading states
- Handle token storage

**Key Components:**
- `login_form()` - Login form component
- `authenticate_user(email, password)` - Authentication handler
- `handle_login_success()` - Success handler
- `handle_login_error()` - Error handler

**Documentation Requirements:**
- UI component documentation
- User flow documentation
- Styling guide

---

### Script 9: `frontend/agent_client.py`

**Purpose**: Client for invoking AgentCore Runtime from Streamlit

**Functionality:**
- Create client for AgentCore Runtime API
- Handle session ID management
- Send requests to agent runtime
- Handle responses and errors
- Implement retry logic

**Key Methods:**
- `invoke_agent(prompt, session_id, user_id)` - Invoke agent
- `create_session(user_id)` - Create new session
- `get_session_status(session_id)` - Get session status
- `handle_response(response)` - Process agent response

**Configuration:**
- Agent runtime ARN
- Region
- Timeout settings

**Documentation Requirements:**
- Client API reference
- Error handling guide
- Session management guide

---

### Script 10: `runtime/agent_runtime.py` (Agent Wrapper)

**Purpose**: Wrap existing agent with AgentCore Runtime SDK

**Functionality:**
- Import existing `cloud_engineer_agent.py` agent
- Wrap with `BedrockAgentCoreApp` decorator
- Create entrypoint handler using `@app.entrypoint`
- Extract user input from payload
- Invoke existing agent
- Return formatted response
- Handle errors gracefully

**Key Components:**
- Agent initialization (preserve existing agent setup)
- Request payload parsing
- Session ID extraction from context
- Response formatting
- Error handling

**Note**: NO Dockerfile needed! AgentCore CLI uses CodeBuild to build containers automatically. Dockerfile only needed if using `--local` or `--local-build` flags.

**Documentation Requirements:**
- Agent wrapper implementation guide
- Code examples (see Code Examples section)
- Error handling strategy
- Session management explanation

---

### Script 11: `scripts/create_cognito_pool.py`

**Purpose**: Create Cognito User Pool if it doesn't exist

**Functionality:**
- Check if user pool exists by name
- Create user pool if not exists with:
  - Email/password authentication
  - Password policies
  - Token expiration settings
  - User attributes (email, sub, groups)
- Create app client for Streamlit
- Configure OAuth flows (Authorization code)
- Set callback URLs (development and production)
- Generate client secret
- Save configuration to .env file

**Input Parameters:**
- `--pool-name`: User pool name (default: cloud-engineer-agent-pool)
- `--region`: AWS region (default: us-east-2)
- `--create-client`: Create app client (default: true)
- `--client-name`: App client name (default: streamlit-client)

**Output:**
- User Pool ID
- Client ID
- Client Secret (if generated)
- Configuration saved to .env file

**Key Methods:**
- `create_user_pool(name, config)` - Create user pool
- `create_app_client(pool_id, client_name, config)` - Create app client
- `configure_oauth_flows(pool_id, client_id, config)` - Configure OAuth
- `save_config(pool_id, client_id, client_secret)` - Save to .env

**Documentation Requirements:**
- Cognito User Pool creation guide
- OAuth configuration guide
- Client setup instructions

---

### Script 12: `scripts/setup_aws_resources.py`

**Purpose**: Automated setup of all AWS resources (one-command setup)

**Functionality:**
- **Cognito User Pool**: Verify existing User Pool OR create new one if not exists
- **Cognito Client**: Verify or create app client automatically
- **IAM Roles**: Create IAM roles for AgentCore Runtime with least-privilege permissions
- **ECR Repository**: Create ECR repository for agent container images (used by AgentCore CLI)
- **CloudWatch Log Groups**: Create log groups for observability
- **Bedrock Guardrail**: Create guardrail with cloud engineering policies
- **Environment Variables**: Generate `.env` file with all resource ARNs and IDs
- **Validation**: Verify all resources created successfully

**Note**: AgentCore Memory and Identity resources are created automatically by `agentcore launch` command. This script does NOT create them - it only creates base AWS resources.

**Input Parameters:**
- `--cognito-pool-id`: Cognito User Pool ID (optional - will create if not provided)
- `--region`: AWS region (default: us-east-2)
- `--prefix`: Resource naming prefix (default: cloud-engineer-agent)
- `--create-cognito`: Create Cognito User Pool if not exists (default: false)
- `--skip-guardrail`: Skip guardrail creation (default: false)

**Output:**
- `.env` file with all configuration
- JSON file with all resource ARNs and IDs
- Status report of created resources

**Error Handling:**
- Rollback on failure
- Idempotent operations (can run multiple times safely)
- Detailed error messages with remediation steps

**Documentation Requirements:**
- Complete automation script documentation
- Parameter reference guide
- Troubleshooting guide
- Rollback procedures

---

### Script 15: `scripts/verify_cognito.py`

**Purpose**: Verify and configure existing Cognito User Pool

**Functionality:**
- **Verify User Pool**: Check if User Pool exists and is accessible
- **Verify Configuration**: Validate authentication settings, password policies
- **Verify User Attributes**: Check required attributes (email, sub, groups)
- **Client Verification**: Check if app client exists or create one
- **Client Configuration**: Configure callback URLs, OAuth flows, token settings
- **Test Authentication**: Test authentication flow with sample credentials
- **Generate Config**: Output Cognito configuration for integration

**Key Methods:**
- `verify_user_pool(pool_id)` - Verify User Pool exists and get details
- `verify_password_policy(pool_id)` - Validate password policy
- `verify_user_attributes(pool_id)` - Check required attributes
- `get_or_create_client(pool_id, client_name, config)` - Get or create app client
- `configure_client(pool_id, client_id, config)` - Configure client settings
- `test_authentication(pool_id, client_id, username, password)` - Test auth flow

**Configuration:**
- Cognito User Pool ID
- App client name
- Callback URLs
- OAuth flows
- Token expiration settings

**Output:**
- Verification report (JSON)
- Configuration file for integration
- Test results

**Documentation Requirements:**
- Cognito verification checklist
- Configuration guide
- Integration examples

---

### Script 16: `scripts/setup_guardrails.py`

**Purpose**: Automated Bedrock Guardrail creation and configuration

**Functionality:**
- **Create Guardrail**: Create Bedrock Guardrail with all policies
- **Content Filters**: Configure profanity, hate speech, violence, sexual content, misinformation filters
- **Topic Policies**: Set up cloud engineering topic policies (allowed/blocked topics)
- **PII Detection**: Configure PII detection and redaction rules
- **Thresholds**: Set confidence thresholds for blocking
- **Version Management**: Create and manage guardrail versions
- **Export Configuration**: Export guardrail config for reuse

**Key Methods:**
- `create_guardrail(name, description, config)` - Create guardrail resource
- `configure_content_filters(guardrail_id, filters)` - Configure content filters
- `configure_topic_policies(guardrail_id, allowed_topics, blocked_topics)` - Set topic policies
- `configure_pii_detection(guardrail_id, pii_types, action)` - Configure PII detection
- `get_guardrail_version(guardrail_id)` - Get guardrail version

**Configuration:**
- Guardrail name and description
- Content filter thresholds (MEDIUM/HIGH)
- Allowed topics (cloud engineering domain)
- Blocked topics (general knowledge, entertainment, etc.)
- PII types to detect
- Redaction behavior (block vs. redact)

**Output:**
- Guardrail ID and version
- Guardrail ARN
- Configuration JSON file

**Documentation Requirements:**
- Guardrail configuration guide
- Policy definitions
- Integration instructions

---

### Script 17: `scripts/setup_agentcore_resources.py`

**Purpose**: Automated setup of AgentCore Memory and Identity resources

**Functionality:**
- **Memory Resource**: Create AgentCore Memory resource with event-based strategy
- **Memory Configuration**: Configure user isolation, retention policies
- **Workload Identity**: Create AgentCore Identity workload
- **OAuth2 Provider**: Configure OAuth2 provider for Cognito integration
- **Return URLs**: Configure allowed OAuth2 return URLs
- **Permissions**: Set up IAM permissions for resources
- **Validation**: Verify all resources are accessible

**Key Methods:**
- `create_memory_resource(name, config)` - Create Memory resource
- `create_workload_identity(name, callback_urls)` - Create workload identity
- `configure_oauth2_provider(provider_name, cognito_config)` - Configure OAuth2
- `verify_resources()` - Verify all resources created

**Configuration:**
- Memory resource name and strategy
- User isolation settings
- Workload identity name
- Cognito OAuth2 configuration
- Callback URLs

**Output:**
- Memory resource ARN
- Workload identity details
- OAuth2 provider configuration

**Documentation Requirements:**
- Resource setup guide
- Configuration reference
- Integration guide

---

### Script 18: `scripts/deploy_all.sh` (or `scripts/deploy_all.py`)

**Purpose**: One-command deployment of entire infrastructure

**Functionality:**
- **Orchestration**: Run all setup scripts in correct order
- **Dependency Management**: Ensure resources are created in proper order
- **Error Handling**: Stop on errors and provide rollback options
- **Status Reporting**: Show progress and status of each step
- **Environment Setup**: Generate final `.env` file with all values
- **Validation**: Verify complete deployment

**Execution Flow:**
1. Verify prerequisites (AWS credentials, region, Cognito Pool ID)
2. Run `verify_cognito.py` - Verify and configure Cognito
3. Run `setup_guardrails.py` - Create guardrails
4. Run `setup_agentcore_resources.py` - Create Memory and Identity
5. Run `setup_aws_resources.py` - Create IAM roles, ECR, CloudWatch
6. Build and push container image
7. Deploy AgentCore Runtime
8. Verify deployment
9. Generate final configuration

**Input Parameters:**
- `--cognito-pool-id`: Existing Cognito User Pool ID (required)
- `--region`: AWS region (default: us-east-2)
- `--skip-build`: Skip container build (default: false)
- `--skip-runtime`: Skip runtime deployment (default: false)
- `--dry-run`: Show what would be created without executing (default: false)

**Output:**
- Complete deployment status report
- Final `.env` file
- Resource ARNs and IDs JSON file
- CloudWatch dashboard links

**Documentation Requirements:**
- Deployment guide
- Troubleshooting guide
- Rollback procedures

---

### Script 19: `scripts/validate_environment.py`

**Purpose**: Comprehensive environment validation before deployment

**Functionality:**
- **AWS Credentials**: Verify AWS credentials are configured
- **Region Access**: Verify access to us-east-2 region
- **Bedrock Access**: Verify Bedrock model access
- **Cognito Access**: Verify access to existing Cognito User Pool
- **Permissions**: Check required IAM permissions
- **Dependencies**: Verify Python packages are installed
- **Configuration**: Validate configuration files

**Checks Performed:**
- AWS credentials validation
- Region availability
- Bedrock model access (check for Claude models)
- Cognito User Pool accessibility
- IAM permissions check
- Python dependencies check
- Environment variables validation

**Output:**
- Validation report (JSON and human-readable)
- Missing permissions list
- Remediation steps for failures

**Documentation Requirements:**
- Validation checklist
- Permission requirements
- Troubleshooting guide

---

### Script 20: `scripts/rollback.py`

**Purpose**: Rollback deployment in case of failures

**Functionality:**
- **Resource Tracking**: Track created resources from deployment
- **Selective Rollback**: Rollback specific resources or all
- **Dependency Handling**: Rollback in reverse dependency order
- **State Preservation**: Preserve state for debugging
- **Cleanup**: Remove created resources safely

**Key Methods:**
- `rollback_all()` - Rollback all created resources
- `rollback_resource(resource_type, resource_id)` - Rollback specific resource
- `list_resources()` - List all created resources
- `preserve_state()` - Save state before rollback

**Safety Features:**
- Confirmation prompts for destructive operations
- Dry-run mode to preview rollback
- State preservation for debugging
- Detailed rollback log

**Documentation Requirements:**
- Rollback procedures
- State preservation guide
- Recovery procedures

---

### Script 21: `scripts/update_config.py`

**Purpose**: Update configuration files after resource creation

**Functionality:**
- **Environment Variables**: Update `.env` file with resource ARNs
- **Configuration Files**: Update runtime configuration files
- **Secrets Management**: Store sensitive values in AWS Secrets Manager (optional)
- **Validation**: Validate all configuration values
- **Documentation**: Generate configuration documentation

**Key Methods:**
- `update_env_file(resources)` - Update .env file
- `update_runtime_config(runtime_arn, config)` - Update runtime config
- `store_secrets(secrets)` - Store in Secrets Manager
- `validate_config()` - Validate all configurations

**Configuration:**
- Resource ARNs and IDs
- Environment variables
- Runtime settings
- Guardrail configuration

**Output:**
- Updated `.env` file
- Updated configuration files
- Configuration documentation

**Documentation Requirements:**
- Configuration update guide
- Secrets management guide

---

### Script 22: `scripts/test_deployment.py`

**Purpose**: Comprehensive testing of deployed infrastructure

**Functionality:**
- **Cognito Testing**: Test authentication flow
- **Guardrail Testing**: Test guardrail enforcement
- **Memory Testing**: Test memory operations
- **Runtime Testing**: Test agent runtime invocation
- **Integration Testing**: Test end-to-end flows
- **Performance Testing**: Basic performance checks

**Test Suites:**
- Authentication tests
- Guardrail enforcement tests
- Memory read/write tests
- Agent invocation tests
- Session management tests
- Error handling tests

**Output:**
- Test report (JSON and HTML)
- Pass/fail status
- Performance metrics

**Documentation Requirements:**
- Test execution guide
- Test case documentation
- Performance benchmarks

---

### Script 23: `scripts/test_scalability.py`

**Purpose**: Test application scalability with concurrent users

**Functionality:**
- **Concurrent User Simulation**: Simulate N concurrent users
- **Load Testing**: Generate load from multiple users simultaneously
- **Session Isolation Verification**: Verify sessions are isolated
- **Response Time Measurement**: Measure response times under load
- **Resource Monitoring**: Monitor AgentCore Runtime metrics
- **Data Leakage Testing**: Verify no data leakage between sessions

**Input Parameters:**
- `--concurrent-users`: Number of concurrent users (default: 100)
- `--requests-per-user`: Requests per user (default: 10)
- `--runtime-arn`: AgentCore Runtime ARN (required)
- `--test-isolation`: Test session isolation
- `--burst-load`: Test burst load scenario
- `--duration`: Test duration in seconds

**Key Methods:**
- `simulate_concurrent_users(user_count, requests_per_user)` - Simulate concurrent users
- `test_session_isolation(session_count)` - Test session isolation
- `measure_response_times()` - Measure response times
- `verify_no_data_leakage()` - Verify data isolation
- `monitor_runtime_metrics()` - Monitor AgentCore metrics
- `generate_report()` - Generate scalability report

**Output:**
- Scalability test report (JSON and HTML)
- Response time statistics
- Success rate
- Number of microVMs created
- Session isolation verification results
- Resource utilization metrics

**Documentation Requirements:**
- Scalability testing guide
- Load testing procedures
- Performance benchmarks
- Acceptance criteria

---

### Script 24: `scripts/deploy_streamlit_production.py`

**Purpose**: Deploy Streamlit UI to production (ECS Fargate + ALB)

**Functionality:**
- **ECS Cluster Creation**: Create Fargate cluster
- **Task Definition**: Create task definition with Streamlit container
- **ECS Service**: Create service with ALB integration
- **Application Load Balancer**: Create ALB with HTTPS listener
- **Target Group**: Create target group for ECS tasks
- **Security Groups**: Configure security groups
- **Auto-Scaling**: Configure auto-scaling policies
- **CloudWatch Logging**: Set up CloudWatch log groups

**Input Parameters:**
- `--cluster-name`: ECS cluster name
- `--service-name`: ECS service name
- `--image-uri`: ECR image URI
- `--desired-count`: Initial task count (default: 2)
- `--region`: AWS region (default: us-east-2)
- `--cpu`: CPU units per task (default: 512)
- `--memory`: Memory per task (default: 1024)

**Output:**
- ALB DNS name
- Service ARN
- Cluster ARN
- Configuration saved to .env

**Documentation Requirements:**
- ECS deployment guide
- ALB configuration guide
- Auto-scaling setup
- Troubleshooting guide

---

### Script 25: `scripts/setup_domain.py`

**Purpose**: Setup domain name and SSL certificate for Streamlit UI

**Functionality:**
- **Route 53 Hosted Zone**: Create hosted zone (if domain not in Route 53)
- **ACM Certificate**: Request SSL certificate
- **Certificate Validation**: Validate certificate (DNS or email)
- **ALB Listener**: Configure HTTPS listener on ALB
- **Route 53 Record**: Create A record pointing to ALB
- **Cognito Update**: Update Cognito callback URLs

**Input Parameters:**
- `--domain-name`: Your domain name (e.g., yourdomain.com)
- `--subdomain`: Subdomain (e.g., agent -> agent.yourdomain.com)
- `--region`: AWS region (default: us-east-2)
- `--validation-method`: DNS or email (default: DNS)
- `--alb-arn`: ALB ARN (required)

**Output:**
- Certificate ARN
- Route 53 record
- Final URL (https://agent.yourdomain.com)
- Configuration saved to .env

**Documentation Requirements:**
- Domain setup guide
- SSL certificate setup
- Route 53 configuration
- DNS validation guide

---

### Script 23: `infrastructure/cloudformation_base_resources.yaml`

**Purpose**: CloudFormation template for base infrastructure

**Functionality:**
- **IAM Roles**: Define IAM roles for AgentCore Runtime
- **ECR Repository**: Define ECR repository for container images
- **CloudWatch Log Groups**: Define log groups for observability
- **S3 Buckets**: Define S3 buckets for temporary storage (if needed)
- **Outputs**: Export resource ARNs and IDs for use in other scripts

**Resources Defined:**
- AgentCoreRuntimeRole (IAM Role)
- AgentContainerRepository (ECR)
- AgentRuntimeLogGroup (CloudWatch)
- AgentMemoryLogGroup (CloudWatch)
- GuardrailLogGroup (CloudWatch)

**Parameters:**
- ProjectPrefix
- CognitoUserPoolId (existing)
- Region

**Outputs:**
- RuntimeRoleArn
- ECRRepositoryUri
- LogGroupArns

**Documentation Requirements:**
- CloudFormation template guide
- Parameter reference
- Deployment instructions

---

### Script 26: `scripts/create_agentcore_identity.py`

**Purpose**: Create AgentCore Workload Identity resource (standalone script)

**Functionality:**
- **Identity Creation**: Create Workload Identity using AgentCore Control Plane API
- **Configuration**: Configure identity name and description
- **Environment Update**: Update .env file with Identity ARN and name
- **Validation**: Validates AWS credentials before creation

**Input Parameters:**
- `--name`: Identity name (default: cloud-engineer-agent-workload-identity)
- `--description`: Identity description (optional)

**Output:**
- Workload Identity ARN
- Workload Identity Name
- Updates .env with WORKLOAD_IDENTITY_NAME and WORKLOAD_IDENTITY_ARN

**Usage:**
```bash
# Create with default name
python scripts/create_agentcore_identity.py

# Create with custom name
python scripts/create_agentcore_identity.py --name my-custom-identity --description "Custom identity"
```

**Documentation Requirements:**
- Identity creation guide
- Configuration reference
- Troubleshooting guide

---

### Script 27: `scripts/create_agentcore_memory.py`

**Purpose**: Create AgentCore Memory resource (standalone script)

**Functionality:**
- **Memory Creation**: Create Memory resource using Bedrock AgentCore SDK
- **Memory Configuration**: Configure STM (Short-Term Memory) and optionally LTM (Long-Term Memory)
- **Strategy Setup**: Configure event-based and semantic strategies
- **Environment Update**: Update .env file with Memory ARN and ID

**Input Parameters:**
- `--name`: Memory resource name (default: cloud-engineer-agent-memory)
- `--enable-ltm`: Enable Long-Term Memory (default: True)
- `--disable-ltm`: Disable Long-Term Memory

**Output:**
- Memory resource ARN
- Memory resource ID
- Memory status
- Updates .env with MEMORY_RESOURCE_ARN and MEMORY_RESOURCE_ID

**Usage:**
```bash
# Create with LTM enabled (default)
python scripts/create_agentcore_memory.py

# Create with custom name and LTM enabled
python scripts/create_agentcore_memory.py --name my-memory --enable-ltm

# Create with LTM disabled (STM only)
python scripts/create_agentcore_memory.py --disable-ltm
```

**Prerequisites:**
- `bedrock-agentcore-starter-toolkit` must be installed

**Documentation Requirements:**
- Memory creation guide
- STM vs LTM explanation
- Configuration reference

---

### Script 28: `scripts/create_guardrail.py`

**Purpose**: Create Bedrock Guardrail resource (standalone script)

**Functionality:**
- **Guardrail Creation**: Create Bedrock Guardrail with default configuration
- **Content Filters**: Configure profanity, hate speech, violence filters
- **Topic Blocking**: Set up cloud engineering topic policies
- **Environment Update**: Update .env file with Guardrail ID and version

**Input Parameters:**
- `--name`: Guardrail name (default: cloud-engineer-agent-guardrail)
- `--description`: Guardrail description (optional)

**Output:**
- Guardrail ID
- Guardrail Version
- Guardrail ARN
- Updates .env with BEDROCK_GUARDRAIL_ID and BEDROCK_GUARDRAIL_VERSION

**Usage:**
```bash
# Create with default name
python scripts/create_guardrail.py

# Create with custom name
python scripts/create_guardrail.py --name my-guardrail --description "Custom guardrail"
```

**Documentation Requirements:**
- Guardrail creation guide
- Configuration reference
- Filter setup guide

---

### Script 29: `scripts/list_agentcore_resources.py`

**Purpose**: List all AgentCore resources (Memory, Identity, Runtime)

**Functionality:**
- **Resource Discovery**: Lists all Memory resources
- **Identity Discovery**: Lists all Workload Identity resources
- **Runtime Discovery**: Lists all Runtime resources
- **Resource Details**: Displays ARN, ID, status, creation date for each resource

**Input Parameters:**
- `--resource-type`: Filter by type (memory|identity|runtime|all, default: all)
- `--region`: AWS region (default: from env or us-east-2)

**Output:**
- Table of all resources with details
- Summary count by resource type

**Usage:**
```bash
# List all resources
python scripts/list_agentcore_resources.py --resource-type all

# List only Memory resources
python scripts/list_agentcore_resources.py --resource-type memory

# List only Identity resources
python scripts/list_agentcore_resources.py --resource-type identity
```

**Documentation Requirements:**
- Resource listing guide
- Output format reference

---

### Script 30: `scripts/verify_agentcore_resources.py`

**Purpose**: Verify that all required AgentCore resources exist and are configured

**Functionality:**
- **.env Validation**: Checks .env file for resource ARNs/IDs
- **AWS Verification**: Verifies resources exist in AWS
- **Status Validation**: Validates resource status (ACTIVE, CREATING, etc.)
- **Issue Reporting**: Reports missing or misconfigured resources

**Input Parameters:**
- `--check-memory`: Verify Memory resource exists
- `--check-identity`: Verify Identity resource exists
- `--check-runtime`: Verify Runtime resource exists
- `--all`: Check all resources (default)

**Output:**
- Status report for each resource
- List of missing resources
- Recommendations for fixing issues

**Usage:**
```bash
# Verify all resources
python scripts/verify_agentcore_resources.py --all

# Verify specific resource type
python scripts/verify_agentcore_resources.py --check-memory
```

**Documentation Requirements:**
- Verification guide
- Troubleshooting guide

---

### Script 31: `scripts/get_resource_status.py`

**Purpose**: Get detailed status of a specific AgentCore resource

**Functionality:**
- **Resource Retrieval**: Retrieves detailed information about specific resource
- **Status Display**: Displays status, configuration, and metadata
- **Health Metrics**: Shows resource health and availability
- **JSON Output**: Optional JSON output for automation

**Input Parameters:**
- `--resource-type`: Resource type (memory|identity|runtime|guardrail) (required)
- `--resource-id`: Resource ID or ARN (required)
- `--region`: AWS region (default: from env or us-east-2)
- `--json`: Output as JSON

**Output:**
- Detailed resource information
- Status and health metrics
- Configuration details

**Usage:**
```bash
# Get Memory status
python scripts/get_resource_status.py --resource-type memory --resource-id <memory-id>

# Get Identity status
python scripts/get_resource_status.py --resource-type identity --resource-id <identity-name>

# Get status as JSON
python scripts/get_resource_status.py --resource-type memory --resource-id <id> --json
```

**Documentation Requirements:**
- Status check guide
- Output format reference

---

### Script 32: `scripts/cleanup_resources.py`

**Purpose**: Clean up/destroy AgentCore resources and related AWS resources

**Functionality:**
- **Resource Listing**: Lists resources to be deleted
- **Confirmation**: Prompts for confirmation (unless --force)
- **Safe Deletion**: Deletes resources in safe order (Runtime → Memory → Identity → Guardrail)
- **Environment Update**: Updates .env file to remove deleted resource IDs

**Input Parameters:**
- `--resource-type`: Resource type to cleanup (memory|identity|runtime|guardrail|all, default: all)
- `--dry-run`: Show what would be deleted without actually deleting
- `--force`: Skip confirmation prompts
- `--region`: AWS region (default: from env or us-east-2)

**Output:**
- List of resources to be deleted
- Confirmation prompt (unless --force)
- Deletion progress
- Updated .env file

**Usage:**
```bash
# Preview deletions (safe)
python scripts/cleanup_resources.py --dry-run

# Delete specific resource type
python scripts/cleanup_resources.py --resource-type memory --force

# Delete all resources (use with extreme caution!)
python scripts/cleanup_resources.py --resource-type all --force
```

**WARNING:**
- This script permanently deletes resources
- Always use --dry-run first to preview
- Check dependencies before deleting (e.g., don't delete Memory if Runtime uses it)

**Documentation Requirements:**
- Cleanup guide
- Safety warnings
- Dependency guide

---

### Script 24: `scripts/quick_start.sh`

**Purpose**: Quick start script for developers

**Functionality:**
- **Interactive Setup**: Guide user through setup process
- **Cognito Pool ID**: Prompt for existing Cognito Pool ID
- **Configuration**: Interactive configuration prompts
- **Deployment**: Run full deployment
- **Verification**: Verify deployment

**User Experience:**
- Step-by-step prompts
- Clear instructions
- Progress indicators
- Error handling with helpful messages

**Documentation Requirements:**
- Quick start guide
- Interactive setup guide

---

### Script 13: `guardrails/guardrail_setup.py`

**Purpose**: Create and configure Amazon Bedrock Guardrail

**Functionality:**
- Create Bedrock Guardrail resource
- Configure content filters (profanity, hate speech, violence, sexual content, misinformation)
- Set up topic policies (blocked/allowed topics)
- Configure PII detection and redaction
- Set blocking thresholds and confidence levels
- Enable guardrail trace for debugging

**Key Components:**
- Content policy configuration
- Topic policy configuration
- PII detection configuration
- Guardrail versioning

**Configuration:**
- Guardrail name and description
- Content filter thresholds
- Topic policy definitions
- PII detection rules

**Output:**
- Guardrail ID and version
- Guardrail ARN

**Documentation Requirements:**
- Guardrail configuration guide
- Content policy definitions
- Topic policy matrix
- PII detection configuration

---

### Script 14: `runtime/guardrail_integration.py`

**Purpose**: Integrate Bedrock Guardrails into Strands Agent

**Functionality:**
- Update BedrockModel initialization with guardrail parameters
- Configure guardrail ID and version from environment variables
- Enable guardrail trace for debugging
- Set input/output redaction preferences
- Handle guardrail intervention responses
- Log guardrail interventions for monitoring

**Key Methods:**
- `configure_guardrails()` - Set up guardrail configuration
- `handle_guardrail_intervention()` - Handle blocked content
- `log_guardrail_metrics()` - Track intervention metrics

**Configuration:**
- Guardrail ID and version
- Input redaction enabled/disabled
- Output redaction enabled/disabled
- Redaction messages

**Documentation Requirements:**
- Guardrail integration guide
- Response handling strategy
- User messaging guidelines
- Monitoring integration

---

## Security & Compliance

### Security Architecture Overview

Security is implemented in **6 layers** to ensure enterprise-grade protection:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Authentication & Identity                          │
│ Cognito User Pool → JWT Tokens → AgentCore Identity         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Authorization & Access Control                     │
│ JWT Validation → User Mapping → Session Authorization       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Runtime Isolation                                  │
│ Dedicated microVM per User → Complete Isolation             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Data Security                                      │
│ Encryption (TLS/HTTPS) → Memory Encryption → PII Guard     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Content Safety & Guardrails                       │
│ Content Filtering → Topic Blocking → PII Detection          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 6: Audit & Compliance                                │
│ CloudWatch Logs → Audit Trail → Compliance Reports          │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Authentication & Identity

#### 1.1 Cognito User Pool Integration

**What It Does:**
- Manages user authentication credentials
- Issues JWT tokens for authenticated sessions
- Enforces password policies
- Supports MFA (Multi-Factor Authentication)

**Security Features:**
- ✅ **Email/Password Authentication**: Secure credential management
- ✅ **Password Policies**: Complexity requirements, expiration, history
- ✅ **MFA Support**: Optional multi-factor authentication (can be enabled)
- ✅ **Token Management**: 1-hour access tokens, 30-day refresh tokens
- ✅ **Account Lockout**: Protection against brute force attacks
- ✅ **User Attributes**: Secure attribute management (email, groups, custom)

**Implementation:**
- User Pool ID: `<existing-pool-id>` (already exists)
- App Client ID: `<client-id>` (will be configured)
- OAuth Flows: Authorization code flow
- Token Expiration: Access (1 hour), Refresh (30 days)
- Password Policy: Minimum 8 characters, complexity required

**Security Benefits:**
- Centralized user management
- Industry-standard authentication (OAuth 2.0)
- Token-based security (no password storage in app)
- SSO-ready architecture

#### 1.2 JWT Token Validation

**What It Does:**
- Validates JWT tokens from Streamlit frontend
- Verifies token signature and expiration
- Extracts user identity from token claims
- Maps user to agent session

**Security Features:**
- ✅ **Token Signature Verification**: Validates tokens are from Cognito
- ✅ **Expiration Checking**: Rejects expired tokens
- ✅ **Claim Validation**: Verifies user ID, groups, permissions
- ✅ **Token Refresh**: Automatic refresh before expiration

**Implementation Flow:**
```
1. User logs in → Cognito issues JWT token
2. Streamlit sends token to AgentCore Runtime
3. AgentCore Identity validates token
4. Extract user ID from token claims
5. Map user ID to agent session
6. Reject if token invalid/expired
```

**Security Benefits:**
- Stateless authentication (no server-side sessions)
- Tamper-proof tokens (cryptographically signed)
- Automatic expiration
- Secure token validation

#### 1.3 AgentCore Identity Service

**What It Does:**
- Creates workload identity for agent runtime
- Manages OAuth2 credential providers
- Maps Cognito users to agent sessions
- Provides identity context for all operations

**Security Features:**
- ✅ **Workload Identity**: Secure identity for runtime
- ✅ **User-Session Mapping**: Ensures user can only access their session
- ✅ **OAuth2 Integration**: Ready for SSO (Phase 2)
- ✅ **Identity Context**: All operations tagged with user identity

**Security Benefits:**
- Secure runtime identity
- User isolation enforcement
- SSO-ready architecture
- Complete identity traceability

### Layer 2: Authorization & Access Control

#### 2.1 User-Level Authorization

**What It Does:**
- Ensures users can only access their own data
- Prevents cross-user data access
- Enforces session-based access control

**Security Features:**
- ✅ **Session Isolation**: Each user gets dedicated session
- ✅ **Memory Isolation**: Users can only access their own memory
- ✅ **Data Segregation**: Complete separation between users
- ✅ **Access Control**: IAM roles enforce permissions

**Implementation Flow:**
```
1. User authenticates → JWT token issued
2. Token validated → User ID extracted
3. User ID mapped to session ID
4. All operations scoped to user session
5. Memory access filtered by user ID
6. Cross-user access blocked
```

**Security Benefits:**
- Zero data leakage between users
- GDPR compliance (data isolation)
- Granular access control
- Audit trail for all access

#### 2.2 IAM Role-Based Access Control

**What It Does:**
- Controls what AWS services the agent can access
- Enforces least-privilege principle
- Manages permissions for runtime

**Security Features:**
- ✅ **Least Privilege**: Runtime only has required permissions
- ✅ **Service-Specific Access**: Limited to EC2, S3, RDS, Lambda, etc.
- ✅ **No Cross-Account Access**: Confined to single AWS account
- ✅ **Read/Write Separation**: Separate permissions for read vs write

**IAM Permissions Example:**
- Read operations: `ec2:Describe*`, `s3:List*`, `rds:Describe*`
- Write operations: `cloudformation:*` (via CloudFormation MCP)
- Bedrock access: `bedrock:InvokeModel`, `bedrock-agentcore:*`

**Security Benefits:**
- Restricted AWS access
- Principle of least privilege
- Audit trail via CloudTrail
- Easy permission management

### Layer 3: Runtime Isolation

#### 3.1 Dedicated MicroVM Per User Session

**What It Does:**
- Each user gets completely isolated runtime environment
- No shared resources between users
- Complete process isolation

**Security Features:**
- ✅ **MicroVM Isolation**: Dedicated virtual machine per user
- ✅ **No Shared Memory**: Complete memory separation
- ✅ **No Shared Processes**: Process isolation
- ✅ **Network Isolation**: Separate network stack per session

**How It Works:**
```
User 1 → Session 1 → MicroVM 1 (isolated)
User 2 → Session 2 → MicroVM 2 (isolated)
User 3 → Session 3 → MicroVM 3 (isolated)
```

**Security Benefits:**
- **Complete Isolation**: Zero possibility of data leakage
- **Side-Channel Attack Prevention**: No shared resources
- **Failure Isolation**: One user's errors don't affect others
- **Compliance**: Meets strict isolation requirements

#### 3.2 Session Management

**What It Does:**
- Manages user sessions with automatic timeout
- Tracks session state and lifecycle
- Cleans up isolated resources after session ends

**Security Features:**
- ✅ **Automatic Timeout**: Sessions expire after 15 minutes of inactivity
- ✅ **Session Cleanup**: Resources cleaned up after session ends
- ✅ **Session State**: Tracks active/inactive sessions
- ✅ **Session Security**: Sessions tied to authenticated user

**Security Benefits:**
- Prevents unauthorized access via stale sessions
- Automatic resource cleanup
- Reduces attack surface
- Prevents resource exhaustion

### Layer 4: Data Security

#### 4.1 Encryption in Transit

**What It Does:**
- Encrypts all data during transmission
- Uses TLS/HTTPS for all communications

**Security Features:**
- ✅ **TLS/HTTPS**: All API calls encrypted
- ✅ **Certificate Validation**: Validates server certificates
- ✅ **Perfect Forward Secrecy**: Uses modern cipher suites
- ✅ **No Plaintext**: No unencrypted data transmission

**Implementation:**
```
Streamlit → HTTPS → API Gateway → HTTPS → AgentCore Runtime
AgentCore Runtime → HTTPS → AWS Services
AgentCore Runtime → HTTPS → AgentCore Memory
```

**Security Benefits:**
- Prevents man-in-the-middle attacks
- Protects data during transmission
- Industry-standard encryption
- Compliance requirement met

#### 4.2 Encryption at Rest

**What It Does:**
- Encrypts data stored in AgentCore Memory
- Encrypts CloudWatch logs
- Encrypts ECR container images

**Security Features:**
- ✅ **Memory Encryption**: AgentCore Memory encrypted at rest
- ✅ **Log Encryption**: CloudWatch logs encrypted
- ✅ **Container Encryption**: ECR images encrypted
- ✅ **KMS Integration**: AWS KMS key management

**Security Benefits:**
- Protects stored data from unauthorized access
- Compliance requirement (GDPR, SOC 2)
- Defense in depth
- Secure storage

#### 4.3 PII Protection

**What It Does:**
- Detects and protects Personally Identifiable Information
- Redacts PII from logs and traces
- Complies with data protection regulations

**Security Features:**
- ✅ **Automatic PII Detection**: Bedrock Guardrails detect PII
- ✅ **PII Redaction**: Automatically redacts PII from responses
- ✅ **Log Masking**: PII masked in observability traces
- ✅ **Compliance**: GDPR, SOC 2, HIPAA compliance

**PII Types Protected:**
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses
- Names (configurable)
- Addresses (configurable)

**Security Benefits:**
- Regulatory compliance
- Privacy protection
- Reduced legal risk
- Customer trust

#### 4.4 Secrets Management

**What It Does:**
- Securely stores and retrieves sensitive credentials
- Rotates secrets automatically
- Encrypts secrets at rest

**Security Features:**
- ✅ **AWS Secrets Manager**: Secure secret storage
- ✅ **Encryption**: Secrets encrypted with KMS
- ✅ **Access Control**: IAM-based access to secrets
- ✅ **Audit Trail**: All secret access logged

**Security Benefits:**
- No hardcoded secrets
- Centralized secret management
- Automatic rotation support
- Audit compliance

### Layer 5: Content Safety & Guardrails

#### 5.1 Bedrock Guardrails

**What It Does:**
- Filters harmful, inappropriate, or toxic content
- Blocks responses on disallowed topics
- Detects and redacts PII automatically

**Security Features:**
- ✅ **Content Filtering**: Profanity, hate speech, violence, sexual content
- ✅ **Topic Blocking**: Blocks non-cloud-engineering topics
- ✅ **PII Detection**: Automatic PII detection and redaction
- ✅ **Compliance**: Meets regulatory requirements

**Guardrail Configuration:**
- Content Filters: Profanity (MEDIUM), Hate Speech (MEDIUM), Violence (MEDIUM), Sexual Content (MEDIUM), Misinformation (HIGH)
- Topic Policies: Allowed (Cloud engineering, AWS services, DevOps), Blocked (General knowledge, entertainment, politics)
- PII Detection: Email, Phone, SSN, Credit Cards → Redact; AWS Account IDs, ARNs → Allow

**Security Benefits:**
- Content safety
- Regulatory compliance
- Reduced legal risk
- Brand protection

#### 5.2 Input/Output Validation

**What It Does:**
- Validates user input before processing
- Sanitizes agent output before sending
- Prevents injection attacks

**Security Features:**
- ✅ **Input Validation**: Validates user input format
- ✅ **Output Sanitization**: Cleans agent responses
- ✅ **Injection Prevention**: Blocks code injection attempts
- ✅ **Size Limits**: Prevents resource exhaustion

**Security Benefits:**
- Prevents injection attacks
- Data integrity
- Resource protection
- System stability

### Layer 6: Audit & Compliance

#### 6.1 Comprehensive Logging

**What It Does:**
- Logs all authentication events
- Logs all agent invocations
- Logs all errors with context
- Creates audit trail for compliance

**Security Features:**
- ✅ **Authentication Logs**: All login attempts logged
- ✅ **Operation Logs**: All agent operations logged
- ✅ **Error Logs**: Detailed error context
- ✅ **Audit Trail**: Complete activity history

**Logging Includes:**
- User ID, session ID, timestamp
- Request/response details
- Error messages and stack traces
- Guardrail interventions
- Performance metrics

**Security Benefits:**
- Forensic analysis capability
- Compliance audit trail
- Debugging and troubleshooting
- Security incident investigation

#### 6.2 Monitoring & Alerting

**What It Does:**
- Monitors security events
- Alerts on suspicious activities
- Tracks performance anomalies

**Security Features:**
- ✅ **Failed Authentication Alerts**: Alerts on repeated failures
- ✅ **Unusual Access Patterns**: Detects anomalies
- ✅ **Error Rate Monitoring**: Tracks error spikes
- ✅ **Performance Monitoring**: Tracks response times

**Monitoring Metrics:**
- Failed authentication attempts
- Unusual access patterns
- High error rates
- Guardrail intervention rates
- Session anomalies

**Security Benefits:**
- Early threat detection
- Proactive security response
- Performance optimization
- Compliance reporting

#### 6.3 Compliance Features

**What It Does:**
- Ensures compliance with regulations
- Provides audit reports
- Supports data protection requirements

**Compliance Standards:**
- ✅ **GDPR**: Data isolation, right to deletion, PII protection
- ✅ **SOC 2**: Audit logs, access controls, encryption
- ✅ **HIPAA**: Enhanced PII protection (if handling healthcare data)

**GDPR Compliance:**
- User data isolation
- Right to deletion (can delete user data)
- PII protection
- Data portability support

**SOC 2 Compliance:**
- Complete audit logs
- Access controls
- Encryption at rest and in transit
- Monitoring and alerting

**Security Benefits:**
- Regulatory compliance
- Customer trust
- Reduced legal risk
- Business continuity

### Security Best Practices Implemented

1. **Defense in Depth**: Multiple security layers, no single point of failure
2. **Least Privilege**: Minimal required permissions, user-level access control
3. **Zero Trust Architecture**: Verify every request, no implicit trust
4. **Encryption Everywhere**: TLS/HTTPS + encryption at rest
5. **Isolation**: User session isolation, memory isolation, process isolation
6. **Monitoring & Auditing**: Complete audit trail, real-time monitoring

### Security Controls Summary

| Security Control | Implementation | Status |
|-----------------|----------------|--------|
| **Authentication** | Cognito User Pool + JWT | ✅ Required |
| **Authorization** | AgentCore Identity + IAM | ✅ Required |
| **Session Isolation** | Dedicated microVM per user | ✅ Required |
| **Memory Isolation** | User-specific memory spaces | ✅ Required |
| **Encryption in Transit** | TLS/HTTPS | ✅ Required |
| **Encryption at Rest** | KMS + AgentCore Memory encryption | ✅ Required |
| **PII Protection** | Bedrock Guardrails | ✅ Required |
| **Content Filtering** | Bedrock Guardrails | ✅ Required |
| **Audit Logging** | CloudWatch + OpenTelemetry | ✅ Required |
| **Monitoring** | CloudWatch + Alarms | ✅ Required |
| **MFA** | Cognito MFA (optional) | ⏸️ Optional |
| **SSO** | OAuth2 (Phase 2) | 🔄 Phase 2 |

### Security Testing

**Authentication Testing:**
- Test valid/invalid credentials
- Test token expiration
- Test token refresh
- Test session timeout

**Authorization Testing:**
- Test user isolation
- Test memory isolation
- Test cross-user access prevention
- Test IAM permissions

**Isolation Testing:**
- Verify microVM isolation
- Verify memory isolation
- Verify process isolation
- Verify network isolation

**Guardrails Testing:**
- Test content filtering
- Test topic blocking
- Test PII detection
- Test redaction behavior

---

## Scalability & Performance

### Auto-Scaling

**AgentCore Runtime:**
- Automatic scaling based on concurrent requests
- Dedicated microVM per user session
- No cold start delays (sessions persist)
- Handles thousands of concurrent users

**Performance Metrics:**
- Target: < 2 seconds response time for simple queries
- Target: < 10 seconds for complex operations
- Concurrent user support: 100+ users (scalable to 1000+)
- Throughput: 100+ requests per second

### Caching Strategy

**Memory Caching:**
- Cache conversation history per session
- Cache user context
- Cache frequently accessed memory

**Response Caching:**
- Cache common queries (optional)
- Cache documentation responses
- Cache diagram generation results

### Load Balancing

**Streamlit Frontend:**
- Deploy Streamlit on ECS/Fargate with ALB
- Multiple instances for high availability
- Session stickiness (if needed)

**Agent Runtime:**
- Managed by AgentCore Runtime automatically
- No manual load balancing required

---

## Guardrails & Content Safety

### Overview

Guardrails are safety mechanisms that control AI system behavior by defining boundaries for content generation and interaction. For enterprise compliance, we will implement **Amazon Bedrock Guardrails** integrated with Strands Agents SDK to provide:

1. **Content Filtering**: Block harmful, inappropriate, or toxic content
2. **Topic Blocking**: Prevent responses on disallowed topics outside the cloud engineering domain
3. **PII Protection**: Detect and redact Personally Identifiable Information
4. **Compliance**: Meet regulatory requirements for AI systems
5. **Risk Management**: Reduce legal and reputational risks

### Implementation Strategy

**Primary Approach**: Amazon Bedrock Native Guardrails
- Integrated directly with Bedrock models
- Automatic content filtering before and after model responses
- Configurable blocking and redaction policies
- Native support in Strands Agents SDK

**Secondary Approach**: Custom Guardrails Hook (Optional)
- Shadow mode for monitoring guardrail triggers
- Custom filtering logic for specific requirements
- Can be used for soft-launching before full enforcement

### Phase 1: Bedrock Guardrails Setup (Week 4-5)

#### 1.1 Guardrail Creation

**Objective**: Create Amazon Bedrock Guardrail with appropriate policies

**Tasks:**
1. **Create Guardrail Resource**
   - Define content filters (profanity, hate speech, violence, etc.)
   - Set up topic blocking policies (block non-cloud-engineering topics)
   - Configure PII detection and redaction
   - Set blocking thresholds (MEDIUM or HIGH confidence)

2. **Content Policy Configuration**
   - **Profanity Filter**: Block or redact profane content
   - **Hate Speech Filter**: Block hate speech and discriminatory content
   - **Violence Filter**: Block violent content
   - **Sexual Content Filter**: Block sexual content
   - **Misinformation Filter**: Block known misinformation patterns

3. **Topic Policy Configuration**
   - **Blocked Topics**: Topics outside cloud engineering domain
   - **Custom Topics**: Define cloud engineering-specific allowed topics
   - **Allowed Topics**: Ensure cloud engineering topics are explicitly allowed

4. **PII Detection Configuration**
   - Enable PII detection for:
     - Email addresses
     - Phone numbers
     - Social Security Numbers
     - Credit card numbers
     - IP addresses
     - AWS account IDs (optional - may need to allow)
     - AWS resource ARNs (optional - may need to allow)
   - Configure redaction behavior (block vs. redact)

**Scripts to Create:**
- `guardrails/guardrail_setup.py` - Guardrail creation script
- `guardrails/guardrail_config.py` - Guardrail configuration definition
- `guardrails/guardrail_validator.py` - Guardrail validation and testing

**Documentation Required:**
- Guardrail configuration guide
- Content policy definitions
- Topic policy matrix
- PII detection configuration

#### 1.2 Agent Integration

**Objective**: Integrate Bedrock Guardrails into Strands Agent

**Tasks:**
1. **Model Configuration**
   - Update BedrockModel initialization with guardrail parameters
   - Configure guardrail ID and version
   - Enable guardrail trace for debugging
   - Set input/output redaction preferences

2. **Guardrail Response Handling**
   - Handle `guardrail_intervened` stop reason
   - Log guardrail interventions for monitoring
   - Provide user-friendly messages when content is blocked
   - Track guardrail intervention metrics

3. **Input Redaction Configuration**
   - Enable `guardrail_redact_input` to overwrite blocked user input
   - Set custom redaction message
   - Ensure follow-up questions don't trigger same guardrails

4. **Output Redaction Configuration** (Optional)
   - Enable `guardrail_redact_output` for model output filtering
   - Set custom output redaction message
   - Handle blocked responses gracefully

**Scripts to Create:**
- `runtime/guardrail_integration.py` - Guardrail integration in agent
- `runtime/guardrail_handler.py` - Guardrail response handling
- `runtime/guardrail_metrics.py` - Guardrail intervention tracking

**Documentation Required:**
- Guardrail integration guide
- Response handling strategy
- User messaging guidelines

#### 1.3 Monitoring & Tuning

**Objective**: Monitor guardrail effectiveness and tune policies

**Tasks:**
1. **Metrics Collection**
   - Track guardrail intervention rates
   - Monitor false positive/negative rates
   - Track content filter triggers by type
   - Monitor PII detection rates

2. **Dashboard Creation**
   - Create CloudWatch dashboard for guardrail metrics
   - Visualize intervention trends
   - Alert on high intervention rates

3. **Tuning Process**
   - Review intervention logs regularly
   - Adjust confidence thresholds as needed
   - Update topic policies based on usage patterns
   - Refine PII detection rules

**Scripts to Create:**
- `guardrails/guardrail_monitor.py` - Guardrail monitoring script
- `guardrails/guardrail_analyzer.py` - Intervention analysis tool
- `observability/guardrail_dashboard.py` - Dashboard creation script

**Documentation Required:**
- Guardrail monitoring guide
- Tuning best practices
- Intervention analysis process

### Phase 2: Advanced Guardrails (Optional - Week 6)

#### 2.1 Custom Guardrails Hook (Shadow Mode)

**Objective**: Implement custom guardrails hook for monitoring

**Tasks:**
1. **Hook Implementation**
   - Create `NotifyOnlyGuardrailsHook` class
   - Implement `MessageAddedEvent` callback for input checking
   - Implement `AfterInvocationEvent` callback for output checking
   - Use Bedrock `ApplyGuardrail` API in shadow mode

2. **Monitoring Integration**
   - Log guardrail violations without blocking
   - Track violation patterns
   - Analyze before full enforcement

**Scripts to Create:**
- `guardrails/custom_guardrails_hook.py` - Custom hook implementation
- `guardrails/shadow_mode_monitor.py` - Shadow mode monitoring

**Documentation Required:**
- Custom hook implementation guide
- Shadow mode monitoring process

#### 2.2 PII Redaction Enhancement

**Objective**: Enhance PII redaction using third-party libraries

**Tasks:**
1. **Library Integration** (Optional)
   - Integrate LLM Guard or Presidio for advanced PII detection
   - Implement recursive PII redaction for nested data
   - Configure custom PII patterns

2. **OpenTelemetry Integration**
   - Configure OTEL collector for PII masking
   - Mask PII in traces and logs
   - Ensure compliance in observability data

**Scripts to Create:**
- `guardrails/pii_redaction.py` - Enhanced PII redaction
- `observability/otel_pii_config.py` - OTEL PII masking configuration

**Documentation Required:**
- PII redaction enhancement guide
- OTEL masking configuration

### Guardrails Configuration Details

#### Content Filters

**Profanity Filter:**
- Block threshold: MEDIUM confidence
- Action: Block or redact
- Scope: User input and model output

**Hate Speech Filter:**
- Block threshold: MEDIUM confidence
- Action: Block
- Scope: User input and model output

**Violence Filter:**
- Block threshold: MEDIUM confidence
- Action: Block
- Scope: User input and model output

**Sexual Content Filter:**
- Block threshold: MEDIUM confidence
- Action: Block
- Scope: User input and model output

**Misinformation Filter:**
- Block threshold: HIGH confidence
- Action: Block
- Scope: Model output only

#### Topic Policies

**Allowed Topics:**
- Cloud engineering
- AWS services
- Infrastructure as Code
- Security best practices
- Cost optimization
- DevOps practices
- Cloud architecture

**Blocked Topics:**
- General knowledge (outside cloud engineering)
- Entertainment
- Politics
- Personal advice
- Medical advice
- Legal advice
- Financial advice (outside cloud cost optimization)

#### PII Detection

**Detected PII Types:**
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses
- Names (configurable)
- Addresses (configurable)

**Redaction Behavior:**
- AWS Account IDs: Allow (required for cloud engineering)
- AWS Resource ARNs: Allow (required for cloud engineering)
- Personal information: Redact or block
- User credentials: Always block

### Guardrails Monitoring

**Key Metrics:**
- Total guardrail interventions
- Interventions by type (content filter, topic policy, PII)
- False positive rate
- False negative rate
- User impact (blocked requests)

**Alerting:**
- Alert on high intervention rate (> 10% of requests)
- Alert on new violation patterns
- Alert on PII detection events

**Dashboards:**
- Guardrail intervention dashboard
- Content filter breakdown
- Topic policy violations
- PII detection trends

### Compliance Considerations

**Regulatory Compliance:**
- GDPR: PII protection and right to deletion
- SOC 2: Content filtering and audit logging
- HIPAA: Enhanced PII protection (if handling healthcare data)

**Audit Requirements:**
- Log all guardrail interventions
- Maintain audit trail of blocked content
- Document guardrail policy changes
- Regular compliance reviews

---

## SSO Preparation (Phase 2)

### Architecture for SSO

**Current Setup (Phase 1):**
- Cognito User Pool (native authentication)
- AgentCore Identity with Cognito integration
- JWT token validation

**SSO Integration (Phase 2):**
- Add Cognito Identity Provider (SAML/OIDC)
- Configure federated identity providers
- Update AgentCore Identity OAuth2 provider
- Enhance Streamlit UI for SSO login

### Prerequisites

**Required Setup:**
- Identity provider (e.g., Azure AD, Okta, Google Workspace)
- SAML/OIDC metadata
- Cognito Identity Provider configuration
- OAuth2 scopes and claims mapping

**Integration Points:**
- Cognito Identity Provider setup
- AgentCore Identity OAuth2 provider update
- Streamlit UI SSO login button
- Token mapping and user attribute mapping

### Implementation Steps (Future)

1. Configure Cognito Identity Provider
2. Update AgentCore Identity OAuth2 provider
3. Add SSO login option to Streamlit UI
4. Handle SSO token validation
5. Map SSO user attributes to application users
6. Test SSO flow end-to-end

---

## Testing Strategy

### Unit Testing

**Scope:**
- Individual script functions
- Memory operations
- Token validation
- Request/response handling

**Tools:**
- pytest
- unittest
- Mocking for AWS services

**Coverage Target:**
- 80% code coverage minimum

### Integration Testing

**Scope:**
- Agent runtime integration
- Memory integration
- Cognito authentication flow
- End-to-end agent invocation

**Tools:**
- pytest with AWS SDK mocks
- LocalStack for local AWS testing
- Integration test environment

### End-to-End Testing

**Scope:**
- Complete user flow from login to agent response
- Multi-user concurrent testing
- Session persistence testing
- Error handling testing

**Tools:**
- Automated E2E test suite
- Load testing tools
- Session testing scripts

### Security Testing

**Scope:**
- Authentication bypass testing
- Token manipulation testing
- Session isolation testing
- Authorization testing

**Tools:**
- Security scanning tools
- Penetration testing (manual)
- Token validation testing

### Scalability Testing ⭐ **CRITICAL**

**Objective**: Verify the application can handle 100+ concurrent users

**Scope:**
- Concurrent user simulation
- Runtime session creation under load
- Memory operations under load
- Response time measurement
- Resource utilization monitoring

**Test Scenarios:**

**Scenario 1: Concurrent User Load Test**
```bash
# Run scalability test script
python scripts/test_scalability.py \
  --concurrent-users 100 \
  --requests-per-user 10 \
  --runtime-arn <your-runtime-arn>

# Expected Behavior:
# - 100 concurrent users sending requests
# - AgentCore Runtime creates up to 100 microVMs
# - Each request completes successfully
# - Response times remain acceptable (< 10 seconds)
# - No data leakage between sessions
```

**Scenario 2: Session Isolation Test**
```bash
# Test that sessions are isolated
python scripts/test_scalability.py \
  --test-isolation \
  --sessions 50

# Expected Behavior:
# - 50 different sessions created
# - Each session gets separate microVM
# - Data from one session not accessible to another
# - Memory isolation verified
```

**Scenario 3: Burst Load Test**
```bash
# Simulate sudden traffic spike
python scripts/test_scalability.py \
  --burst-load \
  --initial-users 10 \
  --peak-users 200 \
  --ramp-up-time 60

# Expected Behavior:
# - AgentCore Runtime auto-scales to handle burst
# - All requests processed successfully
# - No service degradation
# - MicroVMs created as needed
```

**Metrics to Monitor:**

1. **AgentCore Runtime Metrics:**
   - Number of active runtime sessions
   - Number of microVMs created
   - Average response time per session
   - Error rate
   - Concurrent invocation count

2. **Memory Metrics:**
   - Memory write operations per second
   - Memory read operations per second
   - Memory latency
   - Memory errors

3. **Streamlit UI Metrics:**
   - Response time from UI to Runtime
   - UI rendering time
   - Concurrent active users
   - API call success rate

**Scripts to Create:**
- `scripts/test_scalability.py` - Scalability testing script
- `scripts/test_concurrent_users.py` - Concurrent user simulation
- `scripts/test_session_isolation.py` - Session isolation verification
- `scripts/monitor_scalability.py` - Real-time monitoring during tests

**Load Testing Tools:**
- **Locust** (recommended): Python-based load testing
- **Apache JMeter**: For more complex scenarios
- **Custom script**: Using asyncio for concurrent requests

**Scalability Test Script Example (`scripts/test_scalability.py`):**
```python
# Functionality:
# - Simulate N concurrent users
# - Each user sends M requests
# - Measure response times
# - Verify session isolation
# - Monitor AgentCore Runtime metrics
# - Generate scalability report

# Key Methods:
# - simulate_concurrent_users(user_count, requests_per_user)
# - test_session_isolation(session_count)
# - measure_response_times()
# - verify_no_data_leakage()
# - generate_report()
```

**Acceptance Criteria:**
- ✅ 100 concurrent users supported without errors
- ✅ Response time < 10 seconds for 95% of requests
- ✅ No data leakage between sessions
- ✅ Auto-scaling works correctly
- ✅ Memory operations scale linearly
- ✅ No service degradation under load

**How to Run Scalability Tests:**

```bash
# 1. Prepare test environment
# Ensure AgentCore Runtime is deployed and active
agentcore status

# 2. Run baseline test (10 users)
python scripts/test_scalability.py --concurrent-users 10

# 3. Run target test (100 users)
python scripts/test_scalability.py --concurrent-users 100

# 4. Run stress test (200 users)
python scripts/test_scalability.py --concurrent-users 200

# 5. Analyze results
# Review generated scalability report
# Check CloudWatch metrics
# Verify session isolation logs
```

**Expected Results:**

| Concurrent Users | Avg Response Time | Success Rate | MicroVMs Created |
|-----------------|-------------------|--------------|------------------|
| 10 | < 2 seconds | 100% | 10 |
| 50 | < 5 seconds | 100% | 50 |
| 100 | < 10 seconds | > 99% | 100 |
| 200 | < 15 seconds | > 98% | 200 |

**Monitoring During Tests:**

```bash
# Watch CloudWatch metrics in real-time
aws cloudwatch get-metric-statistics \
  --namespace AWS/BedrockAgentCore \
  --metric-name ConcurrentInvocations \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum

# Monitor runtime logs
aws logs tail /aws/bedrock-agentcore/runtimes/<runtime-id> --follow
```

---

## Deployment & Rollout

### Deployment Strategy

**Phases:**
1. **Development Environment**: Initial deployment for testing
2. **Staging Environment**: Production-like testing
3. **Production Environment**: Gradual rollout

**Rollout Plan:**
- Week 1: Deploy to development, test with small user group
- Week 2: Deploy to staging, comprehensive testing
- Week 3: Deploy to production, gradual user migration
- Week 4: Monitor and optimize

### AgentCore Runtime Deployment Process

**Steps:**
1. Wrap agent with AgentCore Runtime SDK (see Step-by-Step Guide)
2. Configure with `agentcore configure`
3. Deploy with `agentcore launch` (uses CodeBuild - no Docker needed)
4. Verify deployment with `agentcore status`
5. Test invocation with `agentcore invoke`

**Rollback Plan:**
- Keep previous container version in ECR
- Use `agentcore destroy` to remove current runtime
- Redeploy previous version using `agentcore launch` with previous config

### Streamlit Production Deployment ⭐ **CRITICAL**

**Objective**: Deploy Streamlit UI to production with domain name and HTTPS

**Architecture:**
```
Users → Domain Name (HTTPS) → Application Load Balancer → ECS Fargate Tasks → Streamlit App
```

**Deployment Steps:**

**Step 1: Create ECR Repository for Streamlit**
```bash
# Create ECR repository
aws ecr create-repository \
  --repository-name streamlit-cloud-engineer-agent \
  --region us-east-2

# Get repository URI
ECR_URI=$(aws ecr describe-repositories \
  --repository-names streamlit-cloud-engineer-agent \
  --query 'repositories[0].repositoryUri' \
  --output text \
  --region us-east-2)
```

**Step 2: Create Streamlit Dockerfile**
```dockerfile
# frontend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY frontend/ ./frontend/
COPY cloud_engineer_agent.py .
COPY .env.example .env

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

**Step 3: Build and Push Streamlit Container**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-2.amazonaws.com

# Build image
docker build -t streamlit-app:latest -f frontend/Dockerfile .

# Tag image
docker tag streamlit-app:latest \
  <account-id>.dkr.ecr.us-east-2.amazonaws.com/streamlit-cloud-engineer-agent:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-2.amazonaws.com/streamlit-cloud-engineer-agent:latest
```

**Step 4: Create ECS Cluster and Service**
```bash
# Use deployment script
python scripts/deploy_streamlit_production.py \
  --cluster-name cloud-engineer-agent-cluster \
  --service-name streamlit-service \
  --image-uri <ecr-uri>:latest \
  --desired-count 2 \
  --region us-east-2

# This script creates:
# - ECS Fargate cluster
# - Task definition
# - ECS service
# - Application Load Balancer (ALB)
# - Target group
# - Security groups
# - IAM roles
```

**Step 5: Setup Domain Name and SSL Certificate**

```bash
# Run domain setup script
python scripts/setup_domain.py \
  --domain-name your-domain.com \
  --subdomain agent \
  --region us-east-2

# This script:
# 1. Creates Route 53 hosted zone (if domain not in Route 53)
# 2. Requests ACM SSL certificate
# 3. Validates certificate (DNS or email)
# 4. Creates ALB listener with HTTPS
# 5. Configures Route 53 record pointing to ALB
# 6. Updates Cognito callback URLs with new domain
```

**Step 6: Update Cognito Callback URLs**
```bash
# Update Cognito app client with production callback URL
aws cognito-idp update-user-pool-client \
  --user-pool-id <pool-id> \
  --client-id <client-id> \
  --callback-urls https://agent.your-domain.com \
  --logout-urls https://agent.your-domain.com \
  --region us-east-2
```

**Scripts to Create:**

**Script: `scripts/deploy_streamlit_production.py`**
```python
# Functionality:
# - Create ECS Fargate cluster
# - Create task definition with Streamlit container
# - Create ECS service with auto-scaling
# - Create Application Load Balancer (ALB)
# - Create target group
# - Configure security groups
# - Set up CloudWatch logging
# - Configure auto-scaling policies

# Input Parameters:
# - --cluster-name: ECS cluster name
# - --service-name: ECS service name
# - --image-uri: ECR image URI
# - --desired-count: Initial task count
# - --region: AWS region

# Output:
# - ALB DNS name
# - Service ARN
# - Cluster ARN
# - Configuration saved to .env
```

**Script: `scripts/setup_domain.py`**
```python
# Functionality:
# - Create Route 53 hosted zone (if needed)
# - Request ACM SSL certificate
# - Validate certificate (DNS or email)
# - Configure ALB listener with HTTPS
# - Create Route 53 A record pointing to ALB
# - Update Cognito callback URLs

# Input Parameters:
# - --domain-name: Your domain name (e.g., yourdomain.com)
# - --subdomain: Subdomain (e.g., agent -> agent.yourdomain.com)
# - --region: AWS region

# Output:
# - Certificate ARN
# - Route 53 record
# - Final URL (https://agent.yourdomain.com)
```

**Step 7: Verify Production Deployment**

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster cloud-engineer-agent-cluster \
  --services streamlit-service \
  --region us-east-2

# Expected: Service running with desired count tasks

# Check ALB status
aws elbv2 describe-load-balancers \
  --region us-east-2 \
  --query 'LoadBalancers[?contains(LoadBalancerName, `streamlit`)].DNSName' \
  --output text

# Test production URL
curl https://agent.your-domain.com/_stcore/health
# Expected: {"status": "ok"}

# Test in browser
# Navigate to: https://agent.your-domain.com
# Expected: Login page appears
```

**Auto-Scaling Configuration:**

```bash
# Configure auto-scaling for ECS service
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/cloud-engineer-agent-cluster/streamlit-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10 \
  --region us-east-2

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/cloud-engineer-agent-cluster/streamlit-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name streamlit-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }' \
  --region us-east-2
```

**Production Deployment Checklist:**

- [ ] ECR repository created
- [ ] Streamlit container built and pushed
- [ ] ECS cluster created
- [ ] Task definition created with environment variables
- [ ] ECS service created with ALB
- [ ] Security groups configured
- [ ] IAM roles created
- [ ] Auto-scaling configured
- [ ] Domain name configured
- [ ] SSL certificate issued and attached
- [ ] Route 53 record created
- [ ] Cognito callback URLs updated
- [ ] Health checks passing
- [ ] CloudWatch logging configured
- [ ] Alarms configured

### Monitoring During Rollout

**Key Metrics:**
- Error rates
- Response times
- User authentication success rates
- Memory usage
- Session creation rates
- ECS task health
- ALB request rates

**Alerts:**
- Error rate > 5%
- Response time > 10 seconds
- Authentication failures > 10%
- Memory errors
- ECS task failures
- ALB 5xx errors

---

## Monitoring & Maintenance

### Key Metrics to Monitor

**Performance Metrics:**
- Agent response time (p50, p95, p99)
- Token usage per request
- Concurrent sessions
- Request throughput

**Reliability Metrics:**
- Error rate
- Session failure rate
- Memory errors
- Authentication failures

**Business Metrics:**
- Active users
- Total requests
- User engagement
- Feature usage

### Dashboards

**GenAI Observability Dashboard:**
- Agent performance overview
- Session tracking
- Trace analysis
- Error tracking

**Custom Dashboards:**
- User activity dashboard
- Memory usage dashboard
- Authentication dashboard
- Cost tracking dashboard

### Alerting

**Critical Alerts:**
- Agent runtime down
- High error rate (> 5%)
- Authentication system failure
- Memory service unavailable

**Warning Alerts:**
- Response time degradation
- High token usage
- Memory quota approaching
- Unusual user activity patterns

### Maintenance Tasks

**Daily:**
- Review error logs
- Check dashboard metrics
- Monitor authentication logs

**Weekly:**
- Review performance metrics
- Analyze user feedback
- Check memory usage trends

**Monthly:**
- Review and optimize costs
- Update dependencies
- Security audit
- Performance optimization

---

## Appendix

### A. Glossary

- **AgentCore Runtime**: Serverless runtime environment for agent deployment
- **AgentCore Memory**: Persistent storage for conversation context
- **AgentCore Identity**: Authentication and authorization service
- **AgentCore Observability**: Monitoring and tracing capabilities
- **MicroVM**: Lightweight virtual machine providing session isolation
- **Session ID**: Unique identifier for user conversation session
- **Workload Identity**: Identity for agent runtime workload

### B. AWS Resources Checklist

- [ ] Cognito User Pool
- [ ] Cognito User Pool Client
- [ ] IAM Role for AgentCore Runtime
- [ ] ECR Repository
- [ ] CloudWatch Log Groups
- [ ] AgentCore Memory Resource
- [ ] AgentCore Identity Workload
- [ ] AgentCore Runtime
- [ ] CloudWatch Dashboards
- [ ] CloudWatch Alarms

### C. Dependencies Checklist

**Python Packages:**
- [ ] `bedrock-agentcore>=0.1.0` ⭐ **REQUIRED**
- [ ] `bedrock-agentcore-starter-toolkit>=0.1.21` ⭐ **REQUIRED** (for deployment CLI)
- [ ] `strands-agents>=0.1.0` (with OTEL support: `strands-agents[otel]`)
- [ ] `aws-opentelemetry-distro>=0.1.0`
- [ ] `boto3>=1.34.0`
- [ ] `botocore>=1.34.0`
- [ ] `streamlit>=1.28.0`
- [ ] `streamlit-authenticator>=0.2.3`
- [ ] `python-dotenv>=1.0.0`
- [ ] `pydantic>=2.5.0`
- [ ] `requests>=2.31.0`
- [ ] All existing MCP tool dependencies (from your current setup)

**Note**: `bedrock-agentcore-starter-toolkit` provides the `agentcore` CLI command used for:
- `agentcore configure` - Configure agent for deployment
- `agentcore launch` - Deploy agent to AgentCore Runtime (uses CodeBuild - no Docker needed!)
- `agentcore status` - Check deployment status
- `agentcore invoke` - Test agent invocation
- `agentcore destroy` - Clean up resources

**AWS Resources:**
- [ ] Bedrock Guardrails (created via AWS Console or CLI)
- [ ] Cognito User Pool (existing)
- [ ] IAM roles (created by scripts)
- [ ] ECR repository (created by scripts)
- [ ] CloudWatch log groups (created by scripts)

**Installation Command:**
```bash
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python -c "import bedrock_agentcore; print('✅ AgentCore installed')"
python -c "import strands; print('✅ Strands installed')"
python -c "import boto3; print('✅ Boto3 installed')"
python -c "import streamlit; print('✅ Streamlit installed')"

# Verify AgentCore CLI (from starter toolkit)
agentcore --help
# Expected: Shows agentcore CLI help menu
agentcore --version
# Expected: Shows version (must be >= 0.1.21 for memory support)
```

### E. IAM Permissions Required

**Complete IAM Policy Template:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AgentCoreRuntimePermissions",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:*",
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AWSReadPermissions",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:List*",
        "s3:List*",
        "s3:Get*",
        "s3:HeadBucket",
        "rds:Describe*",
        "lambda:List*",
        "lambda:Get*",
        "iam:List*",
        "iam:Get*",
        "cloudformation:Describe*",
        "cloudformation:List*",
        "cloudformation:Get*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudFormationWritePermissions",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:CreateChangeSet",
        "cloudformation:ExecuteChangeSet"
      ],
      "Resource": "*"
    },
    {
      "Sid": "MemoryPermissions",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:WriteMemoryEvent",
        "bedrock-agentcore:ReadMemoryEvent",
        "bedrock-agentcore:SearchMemory"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CognitoPermissions",
      "Effect": "Allow",
      "Action": [
        "cognito-idp:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMPermissions",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:GetRole",
        "iam:ListRoles",
        "iam:PutRolePolicy",
        "iam:GetRolePolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ECRPermissions",
      "Effect": "Allow",
      "Action": [
        "ecr:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    },
    {
      "Sid": "GuardrailPermissions",
      "Effect": "Allow",
      "Action": [
        "bedrock:CreateGuardrail",
        "bedrock:GetGuardrail",
        "bedrock:ListGuardrails",
        "bedrock:UpdateGuardrail"
      ],
      "Resource": "*"
    }
  ]
}
```

**How to Apply Permissions:**

1. **Create IAM Policy:**
   ```bash
   # Save policy JSON to file: agentcore-policy.json
   aws iam create-policy \
     --policy-name AgentCoreFullAccess \
     --policy-document file://agentcore-policy.json
   ```

2. **Attach Policy to User:**
   ```bash
   aws iam attach-user-policy \
     --user-name <your-username> \
     --policy-arn arn:aws:iam::<account-id>:policy/AgentCoreFullAccess
   ```

3. **Or Use AWS Console:**
   - Go to: IAM → Users → Your User → Permissions
   - Click: "Add permissions" → "Attach policies directly"
   - Search: "AgentCoreFullAccess" (or create custom policy)
   - Attach and save

### F. Runtime IAM Role Trust Policy

**Trust Policy for AgentCore Runtime Role:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock-agentcore.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "<your-account-id>"
        }
      }
    }
  ]
}
```

**Note:** This trust policy is automatically created by `setup_aws_resources.py` script

## Configuration Files

### .env.example Template

Create `.env.example` file in project root:

```bash
# AWS Configuration
AWS_REGION=us-east-2
AWS_ACCOUNT_ID=<your-account-id>
AWS_PROFILE=default

# Cognito Configuration (Existing User Pool)
COGNITO_USER_POOL_ID=<your-existing-pool-id>
COGNITO_CLIENT_ID=<your-client-id>
COGNITO_REGION=us-east-2

# Guardrails Configuration (Will be populated by setup scripts)
BEDROCK_GUARDRAIL_ID=<will-be-generated>
BEDROCK_GUARDRAIL_VERSION=<will-be-generated>
GUARDRAIL_TRACE=enabled
GUARDRAIL_REDACT_INPUT=true
GUARDRAIL_REDACT_OUTPUT=false

# AgentCore Configuration (Will be populated by setup scripts)
AGENT_RUNTIME_ARN=<will-be-generated>
AGENT_RUNTIME_ENDPOINT=<will-be-generated>
MEMORY_RESOURCE_ARN=<will-be-generated>
WORKLOAD_IDENTITY_NAME=<will-be-generated>

# Observability Configuration
OTEL_SERVICE_NAME=cloud-engineer-agent
OTEL_LOG_GROUP=/aws/bedrock-agentcore/runtimes
OTEL_LOG_STREAM=<will-be-generated>

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# API Gateway Configuration (Phase 2)
API_GATEWAY_URL=<will-be-generated>
API_GATEWAY_API_ID=<will-be-generated>
```

### How to Create .env File

1. **Copy example file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your AWS Account ID:**
   ```bash
   aws sts get-caller-identity --query Account --output text
   # Copy this value
   ```

3. **Get Cognito User Pool ID:**
   ```bash
   # From AWS Console: Cognito → User Pools → Select pool → Copy Pool ID
   # Or via CLI:
   aws cognito-idp list-user-pools --max-results 10 --region us-east-2
   # Copy the Id value
   ```

4. **Edit .env file:**
   ```bash
   # Windows: notepad .env
   # Mac/Linux: nano .env
   
   # Replace these values:
   AWS_REGION=us-east-2
   AWS_ACCOUNT_ID=<paste-your-account-id>
   COGNITO_USER_POOL_ID=<paste-your-pool-id>
   
   # Leave other values as-is (will be populated by scripts)
   ```

5. **Verify .env file:**
   ```bash
   # Load environment variables
   source .env  # Linux/Mac
   # Or manually check values are set
   ```

### Configuration Variable Reference

| Variable | Source | Required | Description | Example |
|----------|--------|----------|-------------|---------|
| `AWS_REGION` | Manual | Yes | AWS region | `us-east-2` |
| `AWS_ACCOUNT_ID` | Manual | Yes | Your AWS account ID | `123456789012` |
| `COGNITO_USER_POOL_ID` | Manual | Yes | Existing Cognito User Pool ID | `us-east-2_AbCdEfGhI` |
| `COGNITO_CLIENT_ID` | Manual/Generated | Yes | Cognito App Client ID | `1a2b3c4d5e6f7g8h9i0j` |
| `AGENT_RUNTIME_ARN` | Generated | Yes | Created by setup script | `arn:aws:bedrock-agentcore:...` |
| `MEMORY_RESOURCE_ARN` | Generated | Yes | Created by setup script | `arn:aws:bedrock-agentcore:...` |
| `BEDROCK_GUARDRAIL_ID` | Generated | Yes | Created by guardrail script | `guardrail-1234567890` |
| `BEDROCK_GUARDRAIL_VERSION` | Generated | Yes | Guardrail version | `DRAFT` or version number |

### Configuration File Locations

- **`.env`**: Root directory (DO NOT commit to git)
- **`.env.example`**: Root directory (commit to git as template)
- **`cognito_config.json`**: Generated by verify_cognito.py
- **`resources.json`**: Generated by setup_aws_resources.py (contains all ARNs)

---

## Troubleshooting Guide ⭐ **CRITICAL**

### Common Errors & Solutions

#### Error: "AccessDeniedException: User is not authorized"

**Cause:** Missing IAM permissions

**Solution:**
```bash
# Check current permissions
aws sts get-caller-identity

# Verify you have these permissions:
# - bedrock-agentcore:*
# - cognito-idp:*
# - iam:CreateRole
# - iam:AttachRolePolicy
# - ecr:*
# - logs:CreateLogGroup
# - logs:PutLogEvents

# Fix: Add required permissions to your IAM user/role
# Go to: AWS Console → IAM → Users → Your User → Permissions
# Add policies or create custom policy with required permissions
```

**Prevention:** Run `python scripts/validate_environment.py` first to check permissions

---

#### Error: "Model not found" or "Model access denied"

**Cause:** Bedrock model access not enabled

**Solution:**
```bash
# Check current model access
aws bedrock list-foundation-models --region us-east-2 | grep claude

# If empty or access denied:
# 1. Go to: AWS Console → Bedrock → Model access
# 2. Click: "Edit" button
# 3. Enable: "Anthropic Claude Sonnet 3.7" (or your preferred model)
# 4. Click: "Save changes"
# 5. Wait 2-5 minutes for propagation
# 6. Verify again:
aws bedrock list-foundation-models --region us-east-2 | grep claude
```

**Prevention:** Enable model access before starting setup

---

#### Error: "Cognito User Pool not found"

**Cause:** Wrong User Pool ID or region mismatch

**Solution:**
```bash
# List all user pools
aws cognito-idp list-user-pools --max-results 10 --region us-east-2

# Verify pool exists
aws cognito-idp describe-user-pool \
  --user-pool-id <pool-id> \
  --region us-east-2

# Check .env file has correct region
cat .env | grep COGNITO_REGION
# Should show: COGNITO_REGION=us-east-2

# Verify pool ID format: us-east-2_XXXXXXXXX
```

**Prevention:** Double-check pool ID before running scripts

---

#### Error: "Docker build failed" or "Image push failed"

**Cause:** Docker not running or ECR authentication issue

**Solution:**
```bash
# Check Docker is running
docker ps
# Expected: Returns container list (or empty list, but no error)

# If Docker not running:
# - Start Docker Desktop
# - Wait for Docker to fully start
# - Verify: docker ps works

# Login to ECR
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-2.amazonaws.com

# Expected Output: Login Succeeded

# Verify ECR repository exists
aws ecr describe-repositories --repository-names cloud-engineer-agent

# If repository doesn't exist, create it:
aws ecr create-repository --repository-name cloud-engineer-agent --region us-east-2
```

**Prevention:** Always verify Docker is running before builds

---

#### Error: "Runtime creation failed"

**Cause:** IAM role permissions or network configuration

**Solution:**
```bash
# Check IAM role exists
aws iam get-role --role-name cloud-engineer-agent-runtime-role

# Verify role trust policy allows bedrock-agentcore.amazonaws.com
aws iam get-role --role-name cloud-engineer-agent-runtime-role \
  --query 'Role.AssumeRolePolicyDocument'

# Expected: Should include "bedrock-agentcore.amazonaws.com" in Principal

# Check CloudWatch logs for detailed error
aws logs tail /aws/bedrock-agentcore/runtimes --follow

# Common issues:
# - Wrong IAM role ARN in .env
# - IAM role trust policy incorrect
# - Missing permissions in IAM role
# - Network configuration issues
```

**Prevention:** Verify IAM role before runtime deployment

---

#### Error: "Token validation failed"

**Cause:** Wrong Cognito configuration or expired token

**Solution:**
```bash
# Verify Cognito client configuration
aws cognito-idp describe-user-pool-client \
  --user-pool-id <pool-id> \
  --client-id <client-id>

# Check token expiration settings
# Verify discovery URL is correct
# Format: https://cognito-idp.<region>.amazonaws.com/<pool-id>/.well-known/openid-configuration

# Test token manually
python auth/test_auth.py
# Should return valid tokens

# If token expired:
# - Refresh token: Use refresh token to get new access token
# - Re-authenticate: Login again to get new tokens
```

**Prevention:** Implement token refresh logic before expiration

---

#### Error: "Memory write failed" or "Memory read failed"

**Cause:** Memory resource not accessible or wrong ARN

**Solution:**
```bash
# Verify memory resource exists
aws bedrock-agentcore-control get-memory-resource \
  --memoryResourceIdentifier <memory-id>

# Check memory ARN in .env
cat .env | grep MEMORY_RESOURCE_ARN

# Verify IAM permissions for memory
# Runtime role needs: bedrock-agentcore:WriteMemoryEvent, bedrock-agentcore:ReadMemoryEvent

# Test memory access
python memory/memory_test.py
```

**Prevention:** Verify memory resource creation before use

---

### Debugging Steps

**Step 1: Check Logs**
```bash
# Runtime logs
aws logs tail /aws/bedrock-agentcore/runtimes --follow

# CloudWatch logs
aws logs tail /aws/bedrock-agentcore/memory --follow

# Application logs (if running locally)
# Check terminal output where Streamlit is running
```

**Step 2: Verify Configuration**
```bash
# Check .env file exists and has values
cat .env

# Verify all required variables are set
python scripts/validate_environment.py

# Expected: All checks pass
```

**Step 3: Test Individual Components**
```bash
# Test Cognito
python auth/test_auth.py

# Test Memory
python memory/memory_test.py

# Test Runtime locally
python runtime/test_runtime_local.py

# Each test should pass independently
```

**Step 4: Check AWS Service Status**
```bash
# Check AWS service health
# Go to: https://status.aws.amazon.com/
# Verify all services are operational

# Check service quotas
aws service-quotas get-service-quota \
  --service-code bedrock-agentcore \
  --quota-code <quota-code>
```

### Getting Help

**Check Logs:**
- CloudWatch Logs: `/aws/bedrock-agentcore/runtimes`
- Application logs: Terminal output
- Docker logs: `docker logs <container-id>`

**Common Issues:**
- See errors above for solutions
- Check AWS Service Health Dashboard
- Verify service quotas not exceeded
- Review CloudWatch metrics for anomalies

**Support Resources:**
- AWS Support: https://support.aws.amazon.com/
- AgentCore Documentation: https://aws.github.io/bedrock-agentcore-starter-toolkit/
- Strands Agents Docs: https://strandsagents.com/latest/
- CloudWatch Logs Insights: For advanced log queries

---

## Cost Estimation

### Estimated Monthly Costs

**AgentCore Runtime:**
- Per invocation: $0.0001 per request
- Monthly (100 users, 1000 requests/user): ~$10/month
- Scales linearly with usage

**AgentCore Memory:**
- Storage: $0.01 per GB-month
- Monthly (100 users, 100MB/user): ~$10/month
- Additional requests: $0.001 per 1K requests

**AgentCore Identity:**
- Free tier: Included
- No additional cost

**Bedrock Model Usage:**
- Claude Sonnet 3.7: ~$0.003 per 1K input tokens, $0.015 per 1K output tokens
- Monthly (1000 requests, avg 2K tokens): ~$50-100/month
- **Cost varies significantly based on usage**

**CloudWatch Logs:**
- First 5GB: Free
- Additional: $0.50 per GB
- Estimated: ~$10-20/month

**CloudWatch Metrics:**
- First 10 metrics: Free
- Additional: $0.30 per metric per month
- Estimated: ~$5-10/month

**ECR Storage:**
- $0.10 per GB-month
- Estimated: ~$1/month

**API Gateway** (if used):
- First 1M requests: Free
- Additional: $3.50 per 1M requests
- Estimated: ~$5-10/month

**Total Estimated Monthly Cost:**

| Usage Level | Monthly Cost | Annual Cost |
|-------------|--------------|-------------|
| **Light** (10 users, 100 requests/user) | $80-120 | $960-1440 |
| **Typical** (100 users, 1000 requests/user) | $150-300 | $1800-3600 |
| **Heavy** (1000 users, 5000 requests/user) | $1000-2500 | $12000-30000 |

### Cost Optimization Tips

1. **Memory Retention:** Set retention policies to delete old conversations (reduce storage)
2. **Log Retention:** Set CloudWatch log retention to 7-14 days (reduce log storage)
3. **Model Selection:** Use smaller models for simple queries (reduce token costs)
4. **Caching:** Cache common responses to reduce model calls (reduce invocation costs)
5. **Auto-scaling:** Use AgentCore Runtime auto-scaling (no idle costs)
6. **Request Optimization:** Batch requests when possible (reduce API calls)

### Budget Planning Worksheet

| Component | Monthly Cost (Light) | Monthly Cost (Typical) | Monthly Cost (Heavy) |
|-----------|---------------------|----------------------|---------------------|
| AgentCore Runtime | $1-2 | $10-20 | $100-200 |
| Memory | $1-2 | $10-20 | $100-200 |
| Bedrock Models | $50-80 | $100-200 | $500-1500 |
| CloudWatch | $10-20 | $20-40 | $100-200 |
| ECR | $1 | $1-2 | $5-10 |
| API Gateway | $0-5 | $5-10 | $50-100 |
| **Total** | **$63-129** | **$146-292** | **$855-2210** |

### Setting Up Cost Alerts

```bash
# Create CloudWatch billing alarm
aws cloudwatch put-metric-alarm \
  --alarm-name agentcore-monthly-budget \
  --alarm-description "Alert when monthly cost exceeds $200" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 200 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD
```

---

### D. Environment Variables Reference

```
# AWS Configuration
AWS_REGION=us-east-2
AWS_ACCOUNT_ID=<your-account-id>

# Cognito Configuration (Existing User Pool)
COGNITO_USER_POOL_ID=<existing-pool-id>
COGNITO_CLIENT_ID=<existing-client-id>
COGNITO_REGION=us-east-2

# Guardrails Configuration
BEDROCK_GUARDRAIL_ID=<guardrail-id>
BEDROCK_GUARDRAIL_VERSION=<guardrail-version>
GUARDRAIL_TRACE=enabled
GUARDRAIL_REDACT_INPUT=true
GUARDRAIL_REDACT_OUTPUT=false

# AgentCore Configuration
AGENT_RUNTIME_ARN=<runtime-arn>
MEMORY_RESOURCE_ARN=<memory-arn>
WORKLOAD_IDENTITY_NAME=<workload-name>

# Observability Configuration
OTEL_SERVICE_NAME=cloud-engineer-agent
OTEL_LOG_GROUP=/aws/bedrock-agentcore/runtimes
OTEL_LOG_STREAM=<log-stream>
```

### G. Code Examples & Templates

#### Example 1: Basic Runtime Wrapper

```python
# runtime/agent_runtime.py
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.runtime.context import RequestContext
from cloud_engineer_agent import agent  # Import existing agent
import os
import logging

logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()

@app.entrypoint
def handle_invocation(context: RequestContext, request: dict) -> dict:
    """
    Handle agent invocation request.
    
    Args:
        context: Request context with session ID and user info
        request: Request payload with user input
        
    Returns:
        Agent response with message and metadata
    """
    try:
        # Extract user input
        user_input = request.get('prompt') or request.get('message', '')
        
        if not user_input:
            return {
                'error': 'No prompt or message provided',
                'session_id': context.session_id
            }
        
        # Extract session ID
        session_id = context.session_id
        
        # Extract user ID from context
        user_id = context.user_id or 'anonymous'
        
        logger.info(f"Processing request for user {user_id}, session {session_id}")
        
        # Invoke existing agent
        response = agent(user_input)
        
        # Format response
        if hasattr(response, 'message'):
            content = response.message.get('content', str(response))
        else:
            content = str(response)
        
        return {
            'message': content,
            'session_id': session_id,
            'user_id': user_id
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            'error': str(e),
            'session_id': context.session_id if context else 'unknown'
        }

if __name__ == '__main__':
    # For local testing
    app.run()
```

#### Example 2: Memory Integration

```python
# runtime/memory_integration.py
from memory.memory_manager import MemoryManager
import os
import logging

logger = logging.getLogger(__name__)

# Initialize memory manager
memory_manager = MemoryManager(
    memory_arn=os.environ.get('MEMORY_RESOURCE_ARN')
)

def store_conversation(user_id: str, session_id: str, 
                      user_input: str, agent_response: str):
    """Store conversation in memory."""
    try:
        memory_manager.write_event(
            user_id=user_id,
            session_id=session_id,
            message=user_input,
            response=agent_response
        )
        logger.info(f"Stored conversation for user {user_id}, session {session_id}")
    except Exception as e:
        logger.error(f"Error storing conversation: {e}", exc_info=True)

def retrieve_context(user_id: str, session_id: str, limit: int = 10):
    """Retrieve conversation context."""
    try:
        events = memory_manager.read_events(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
        return events
    except Exception as e:
        logger.error(f"Error retrieving context: {e}", exc_info=True)
        return []
```

#### Example 3: Cognito Authentication

```python
# auth/cognito_client.py
import boto3
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

cognito_client = boto3.client(
    'cognito-idp', 
    region_name=os.environ.get('COGNITO_REGION', 'us-east-2')
)

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user and return tokens."""
    try:
        response = cognito_client.initiate_auth(
            ClientId=os.environ['COGNITO_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        auth_result = response['AuthenticationResult']
        return {
            'access_token': auth_result['AccessToken'],
            'id_token': auth_result['IdToken'],
            'refresh_token': auth_result['RefreshToken'],
            'expires_in': auth_result['ExpiresIn']
        }
    except cognito_client.exceptions.NotAuthorizedException:
        logger.error("Invalid credentials")
        return None
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        return None

def validate_token(token: str) -> Optional[Dict]:
    """Validate JWT token and return user info."""
    try:
        # Get user pool ID
        pool_id = os.environ['COGNITO_USER_POOL_ID']
        
        # Get user info from token
        response = cognito_client.get_user(AccessToken=token)
        
        return {
            'username': response['Username'],
            'user_attributes': {attr['Name']: attr['Value'] 
                              for attr in response['UserAttributes']}
        }
    except Exception as e:
        logger.error(f"Token validation error: {e}", exc_info=True)
        return None
```

#### Example 4: Streamlit Authentication UI

```python
# frontend/auth_ui.py
import streamlit as st
from auth.cognito_client import authenticate_user, validate_token
import os

def show_login_page():
    """Display login page."""
    st.title("Cloud Engineer Agent - Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            tokens = authenticate_user(email, password)
            if tokens:
                # Store tokens in session state
                st.session_state['access_token'] = tokens['access_token']
                st.session_state['id_token'] = tokens['id_token']
                st.session_state['refresh_token'] = tokens['refresh_token']
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email
                st.rerun()
            else:
                st.error("Invalid email or password")

def check_authentication():
    """Check if user is authenticated."""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if not st.session_state['authenticated']:
        show_login_page()
        return False
    
    # Validate token
    token = st.session_state.get('access_token')
    if token:
        user_info = validate_token(token)
        if not user_info:
            # Token invalid, clear session
            st.session_state['authenticated'] = False
            st.rerun()
            return False
    
    return True
```

### H. Testing Examples

#### Unit Test Example

```python
# tests/unit/test_memory_manager.py
import pytest
from unittest.mock import Mock, patch
from memory.memory_manager import MemoryManager

@pytest.fixture
def memory_manager():
    """Create memory manager with mocked client."""
    with patch('memory.memory_manager.MemoryClient') as mock_client:
        manager = MemoryManager(memory_arn='arn:test:memory:123')
        manager.client = mock_client
        return manager

def test_write_event(memory_manager):
    """Test writing event to memory."""
    memory_manager.write_event(
        user_id='user123',
        session_id='session456',
        message='Hello',
        response='Hi there'
    )
    memory_manager.client.write_event.assert_called_once()

def test_read_events(memory_manager):
    """Test reading events from memory."""
    memory_manager.client.read_events.return_value = [
        {'message': 'Hello', 'response': 'Hi'}
    ]
    events = memory_manager.read_events('user123', 'session456', limit=10)
    assert len(events) == 1
    assert events[0]['message'] == 'Hello'
```

#### Integration Test Example

```python
# tests/integration/test_agent_runtime.py
import pytest
import os
from runtime.agent_runtime import handle_invocation
from bedrock_agentcore.runtime.context import RequestContext

@pytest.fixture
def mock_context():
    """Create mock request context."""
    return RequestContext(
        session_id='test-session-123',
        user_id='test-user-456'
    )

def test_agent_invocation(mock_context):
    """Test agent invocation with sample request."""
    request = {'prompt': 'List EC2 instances'}
    
    response = handle_invocation(mock_context, request)
    
    assert 'message' in response or 'error' in response
    assert response['session_id'] == 'test-session-123'

def test_agent_invocation_empty_request(mock_context):
    """Test agent invocation with empty request."""
    request = {}
    
    response = handle_invocation(mock_context, request)
    
    assert 'error' in response
```

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_memory_manager.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests
pytest tests/integration/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_memory_manager.py::test_write_event
```

#### Example 5: Streamlit Agent Client (Invoking AgentCore Runtime)

```python
# frontend/agent_client.py
import boto3
import json
import uuid
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class AgentCoreClient:
    """Client for invoking AgentCore Runtime from Streamlit."""
    
    def __init__(self):
        self.runtime_arn = os.environ.get('AGENT_RUNTIME_ARN')
        self.region = os.environ.get('AWS_REGION', 'us-east-2')
        self.client = boto3.client('bedrock-agentcore', region_name=self.region)
    
    def invoke_agent(
        self, 
        prompt: str, 
        session_id: str, 
        access_token: Optional[str] = None
    ) -> Dict:
        """
        Invoke AgentCore Runtime with user prompt.
        
        Args:
            prompt: User's message/prompt
            session_id: Runtime session ID (generated by Streamlit)
            access_token: JWT token from Cognito (optional if OAuth configured)
            
        Returns:
            Agent response with message content
        """
        try:
            # Prepare payload
            payload = json.dumps({"prompt": prompt}).encode()
            
            # Invoke runtime
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=payload,
                qualifier="DEFAULT"
            )
            
            # Process streaming response
            content = []
            for chunk in response.get("response", []):
                content.append(chunk.decode('utf-8'))
            
            # Parse response
            result = json.loads(''.join(content))
            
            logger.info(f"Agent response received for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error invoking agent: {e}", exc_info=True)
            return {
                'error': str(e),
                'session_id': session_id
            }

# Usage in Streamlit
def main():
    import streamlit as st
    from frontend.session_manager import generate_session_id
    
    # Initialize client
    agent_client = AgentCoreClient()
    
    # Get user ID from session state (after login)
    user_id = st.session_state.get('user_id')
    access_token = st.session_state.get('access_token')
    
    # Generate session ID (per user/conversation)
    if 'runtime_session_id' not in st.session_state:
        st.session_state['runtime_session_id'] = generate_session_id(user_id)
    
    # Chat interface
    user_input = st.chat_input("Enter your message")
    
    if user_input:
        # Call AgentCore Runtime
        response = agent_client.invoke_agent(
            prompt=user_input,
            session_id=st.session_state['runtime_session_id'],
            access_token=access_token
        )
        
        # Display response
        st.write(response.get('message', response.get('response', 'Error')))
```

**How This Works:**
1. User sends message in Streamlit
2. Streamlit generates session ID (if new conversation)
3. Streamlit calls `invoke_agent_runtime` API
4. AgentCore Runtime receives request → Creates microVM for session ID
5. Agent runs in isolated microVM
6. Response returned to Streamlit
7. Streamlit displays response to user

**Session Isolation:**
- Each unique session ID gets its own microVM
- Streamlit generates unique session IDs per user/conversation
- Multiple users → Multiple session IDs → Multiple microVMs
- Complete isolation guaranteed by AgentCore Runtime

#### ⚠️ Common Mistakes to Avoid

1. **Wrong Region**
   - ❌ DON'T: Use different regions for different services
   - ✅ DO: Use us-east-2 for ALL services consistently

2. **IAM Permissions**
   - ❌ DON'T: Use overly permissive policies
   - ✅ DO: Use least-privilege principle

3. **Environment Variables**
   - ❌ DON'T: Hardcode values in code
   - ✅ DO: Use .env file and environment variables

4. **Container Builds**
   - ❌ DON'T: Build on wrong architecture (x86_64 instead of ARM64)
   - ✅ DO: Use ARM64 base images for AgentCore Runtime

5. **Memory Isolation**
   - ❌ DON'T: Share memory between users
   - ✅ DO: Always filter by user_id and session_id

6. **Token Handling**
   - ❌ DON'T: Store tokens in plaintext or commit to git
   - ✅ DO: Use secure storage (Secrets Manager or environment variables)

7. **Error Handling**
   - ❌ DON'T: Swallow exceptions silently
   - ✅ DO: Log errors with context and return user-friendly messages

#### ✅ Best Practices

1. **Always Validate Input**
   - Validate user input before processing
   - Sanitize inputs to prevent injection attacks
   - Check input size limits

2. **Error Handling**
   - Always handle exceptions gracefully
   - Log errors with context (user_id, session_id, request details)
   - Return user-friendly error messages

3. **Testing**
   - Write tests before deploying
   - Test error scenarios
   - Test with multiple users
   - Test token expiration

4. **Monitoring**
   - Set up alerts for critical errors
   - Monitor cost and usage
   - Review logs regularly
   - Track guardrail interventions

5. **Documentation**
   - Document all environment variables
   - Document API changes
   - Keep deployment logs
   - Document configuration changes

6. **Security**
   - Never commit .env file to git
   - Use secrets manager for sensitive data
   - Rotate credentials regularly
   - Review IAM permissions regularly

### J. Key Contacts & Resources

**Documentation:**
- AgentCore Documentation: https://aws.github.io/bedrock-agentcore-starter-toolkit/
- Strands Agents Documentation: https://strandsagents.com/latest/
- Cognito Documentation: https://docs.aws.amazon.com/cognito/

**Support:**
- AWS Support
- AgentCore GitHub Issues
- Strands Agents Community

---

## Questions & Next Steps

### Confirmed Requirements ✓

1. **Cognito User Pool**: ✅ Can create new OR use existing (scripts handle both)
2. **Deployment Region**: ✅ us-east-2
3. **User Scale**: ✅ 100+ concurrent users
4. **Compliance Requirements**: ✅ Guardrails implementation required
5. **Runtime Deployment**: ✅ Using AgentCore CLI (agentcore launch) - no Dockerfile needed
6. **Scalability Testing**: ✅ Scripts provided for testing 100+ concurrent users
7. **Production Deployment**: ✅ Streamlit deployment via ECS Fargate + ALB + Domain setup

### Implementation Status

**Ready for Implementation:**
- ✅ AgentCore CLI deployment process documented
- ✅ Cognito User Pool creation script documented
- ✅ Scalability testing procedures documented
- ✅ Streamlit production deployment documented
- ✅ Domain name setup documented
- ✅ Architecture flow clarified (Streamlit → AgentCore Runtime)

**Remaining Questions for Clarification:**

1. **User Management**: Will users be created manually, or do you need automated user provisioning?
2. **Memory Strategy**: Prefer event-based or semantic memory, or both? (Both recommended - configured via AgentCore CLI)
3. **Network Configuration**: Public or VPC network mode for AgentCore Runtime? (Public recommended for Phase 1)
4. **Cost Considerations**: Any specific cost targets or constraints?
5. **Guardrail Policies**: Any specific content filtering requirements beyond standard cloud engineering topics?
6. **PII Handling**: Should AWS Account IDs and ARNs be allowed (required for cloud engineering) or redacted?
7. **Domain Name**: Do you have a domain name ready for production deployment?

### Next Steps

1. **Review this plan** with stakeholders
2. **Answer clarification questions** above
3. **Prioritize phases** based on business needs
4. **Set up development environment** (Week 1)
5. **Begin Phase 1 implementation** (Week 1)

---

**End of Implementation Plan**

