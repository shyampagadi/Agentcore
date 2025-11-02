# Getting Started Guide - Enterprise Cloud Engineer Agent

**Welcome!** This guide will help you understand, set up, and deploy the Enterprise Cloud Engineer Agent built with AWS Bedrock AgentCore.

> **⭐ NEWBIE ALERT**: If you're new to this project and want a **detailed step-by-step execution guide with AWS Console verification steps**, see **[NEWBIE_SETUP_GUIDE.md](./NEWBIE_SETUP_GUIDE.md)** - This is your detailed implementation guide!

---

## Table of Contents

1. [Welcome & Project Overview](#welcome--project-overview)
2. [Architecture Overview](#architecture-overview)
3. [System Flow (How Everything Works Together)](#system-flow-how-everything-works-together)
4. [Project Structure Explained](#project-structure-explained)
5. [Script Execution Guide](#script-execution-guide) ⭐ **CRITICAL - START HERE**
6. [Common Workflows](#common-workflows)
7. [Quick Reference](#quick-reference)
8. [FAQ](#faq)
9. [Where to Get Help](#where-to-get-help)

---

## Welcome & Project Overview

### What This Project Does

This is an **Enterprise Cloud Engineer Agent** that helps cloud engineers manage AWS infrastructure using natural language. Built with:
- **AWS Bedrock AgentCore**: Serverless runtime with auto-scaling and session isolation
- **Strands Agents**: Agent framework for AWS operations
- **Streamlit**: Web UI for user interaction
- **Cognito**: Authentication and user management
- **Bedrock Guardrails**: Content safety and compliance

### Key Features

- ✅ **Multi-user support**: 100+ concurrent users with isolated sessions
- ✅ **Secure**: Cognito authentication + JWT validation
- ✅ **Scalable**: Auto-scaling microVMs per session
- ✅ **Compliant**: Guardrails for content filtering and PII protection
- ✅ **Memory**: Conversation history and knowledge persistence
- ✅ **AWS Integration**: Full AWS service operations via MCP tools

### Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.10+** (`python --version`)
- ✅ **AWS CLI 2.x** installed and configured (`aws --version`)
- ✅ **AWS Account** with admin access
- ✅ **Bedrock Model Access** enabled (Claude Sonnet 3.7)
- ✅ **Cognito User Pool** (or we'll create one)
- ✅ **Docker Desktop** (for local testing, optional)

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed prerequisites.

---

## Architecture Overview

### Visual Architecture Diagram

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────┐
│     Streamlit UI (Frontend)     │
│  - Authentication (Cognito)     │
│  - Chat Interface               │
│  - Session Management           │
│  - Running on: ECS Fargate/EC2 │
└────────┬────────────────────────┘
         │ API Call (HTTPS)
         │ Session ID + JWT Token
         ▼
┌─────────────────────────────────┐
│   AgentCore Runtime (Backend)    │
│  - MicroVM per Session          │
│  - Auto-scaling                 │
│  - Session Isolation            │
│  - Serverless                   │
└────────┬────────────────────────┘
         │ Agent Execution
         ▼
┌─────────────────────────────────┐
│   Cloud Engineer Agent          │
│  - Strands Agent                │
│  - MCP Tools (AWS CLI, Docs)   │
│  - Bedrock Model (Claude)      │
└────────┬────────────────────────┘
         │ Memory Operations
         │ Guardrail Checks
         ▼
┌─────────────────────────────────┐
│   AgentCore Memory              │
│  - Conversation History (STM)   │
│  - Knowledge Base (LTM)         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   Bedrock Guardrails             │
│  - Content Filtering             │
│  - PII Protection                │
│  - Topic Blocking                │
└─────────────────────────────────┘
```

### Components Explained

- **Streamlit UI**: Frontend web interface where users interact
- **AgentCore Runtime**: Serverless runtime that creates isolated microVMs for each user session
- **Cloud Engineer Agent**: The core Strands agent that processes requests and calls AWS services
- **AgentCore Memory**: Persistent storage for conversation history and knowledge
- **Bedrock Guardrails**: Content safety and compliance filtering
- **Cognito**: User authentication and identity management

### How Scalability Works

**Key Concept**: Each user session gets its own isolated microVM!

- When **User A** logs in → Streamlit generates `session_id_A`
- When **User A** sends a message → AgentCore Runtime creates/uses `microVM_A` for `session_id_A`
- When **User B** logs in → Streamlit generates `session_id_B`
- When **User B** sends a message → AgentCore Runtime creates/uses `microVM_B` for `session_id_B`
- **Result**: Users A and B operate in completely isolated environments

This means:
- ✅ No data leakage between users
- ✅ Auto-scaling: AgentCore creates microVMs as needed
- ✅ No shared state: Each session is independent
- ✅ Handles 100+ concurrent users automatically

---

## System Flow (How Everything Works Together)

### Complete User Journey

**Step 1: User Opens Streamlit UI**
- URL: `http://localhost:8501` (dev) or `https://your-domain.com` (prod)
- What happens: Streamlit server starts, shows login page
- Files involved: `frontend/app.py`, `frontend/auth_ui.py`

**Step 2: User Authenticates**
- User enters username/password
- What happens:
  - `frontend/auth_ui.py` calls `auth/cognito_client.py`
  - Cognito validates credentials
  - Returns JWT tokens (access, ID, refresh)
  - Streamlit stores tokens in session state
- Files involved: `auth/cognito_client.py`, `identity/jwt_validator.py`

**Step 3: User Sends Message**
- User types message in chat interface
- What happens:
  - `frontend/app.py` calls `frontend/session_manager.py`
  - Generates/retrieves session ID
  - `frontend/agent_client.py` prepares request
  - Calls AgentCore Runtime API with session ID + JWT token
- Files involved: `frontend/agent_client.py`, `frontend/session_manager.py`

**Step 4: Request Reaches AgentCore Runtime**
- Runtime receives request with `session_id` and JWT token
- What happens:
  - Runtime validates JWT token (`identity/jwt_validator.py`)
  - Creates/retrieves microVM for `session_id`
  - Calls `runtime/agent_runtime.py` → `handle_invocation()`
  - Extracts prompt from payload
- Files involved: `runtime/agent_runtime.py`, `runtime/session_handler.py`

**Step 5: Agent Processes Request**
- Runtime calls agent execution
- What happens:
  - `runtime/memory_integration.py` loads conversation history
  - `runtime/context_builder.py` builds context
  - `runtime/guardrail_integration.py` checks input
  - `agents/cloud_engineer_agent.py` executes with tools
  - Agent calls AWS services via MCP tools
  - Agent generates response
  - `runtime/guardrail_integration.py` checks output
  - `runtime/memory_integration.py` saves conversation
- Files involved: `runtime/agent_runtime.py`, `agents/cloud_engineer_agent.py`

**Step 6: Response Returned**
- Agent returns response
- What happens:
  - Runtime formats response
  - Returns to Streamlit via API
  - Streamlit displays response
- Files involved: `frontend/app.py`, `frontend/response_handler.py`

**Step 7: User Sees Response**
- Response displayed in chat interface
- What happens:
  - `frontend/app.py` displays message
  - Updates chat history
- Files involved: `frontend/app.py`

### Session Management Flow

```
User Login → Cognito User ID
    ↓
Session ID Generated (frontend/session_manager.py)
    ↓
Session ID Used in Runtime Calls
    ↓
AgentCore Runtime Creates MicroVM (if new session)
    ↓
MicroVM Isolated from Other Sessions
    ↓
Conversation History Saved to Memory
    ↓
Next Request: Same Session ID → Same MicroVM
```

### Memory Integration Flow

```
Agent Execution Request
    ↓
Load Context from Memory (memory/session_memory_handler.py)
    ↓
Build Context with History (runtime/context_builder.py)
    ↓
Agent Executes with Context
    ↓
Save Conversation to Memory (memory/memory_manager.py)
```

### Guardrail Integration Flow

```
User Input
    ↓
Check Input Guardrail (runtime/guardrail_integration.py)
    ├── If Violation: Block Request
    └── If Safe: Continue
    ↓
Agent Processing
    ↓
Agent Output
    ↓
Check Output Guardrail (runtime/guardrail_integration.py)
    ├── If Violation: Redact/Block
    └── If Safe: Return Response
```

---

## Project Structure Explained

### Directory Structure

```
maygum-agentcore/
├── agents/                          # ⭐ NEW: Modular agents
│   ├── __init__.py                  # Package marker
│   └── cloud_engineer_agent.py      # Main agent (moved from root)
│
├── prompts/                         # ⭐ NEW: Modular prompts
│   ├── __init__.py                  # Package marker
│   └── cloud_engineer/              # Cloud engineer agent prompts
│       ├── __init__.py
│       ├── system_prompt.py         # System prompt
│       └── predefined_tasks.py      # Predefined tasks
│
├── runtime/                         # AgentCore Runtime code
│   ├── agent_runtime.py            # ⭐ ENTRYPOINT: Runtime wrapper
│   ├── session_handler.py          # Session management
│   ├── memory_integration.py       # Memory operations
│   └── guardrail_integration.py    # Guardrail checks
│
├── frontend/                        # Streamlit UI
│   ├── app.py                      # ⭐ MAIN APP: Streamlit entrypoint
│   ├── agent_client.py             # AgentCore client
│   ├── auth_ui.py                  # Authentication UI
│   └── session_manager.py          # Session management
│
├── scripts/                         # Automation scripts
│   ├── validate_environment.py    # ⭐ START HERE: Environment check
│   ├── create_cognito_pool.py      # Cognito setup
│   ├── setup_guardrails.py         # Guardrail setup
│   └── deploy_all.py               # One-command deployment
│
├── memory/                          # Memory module
├── identity/                        # Identity module
├── guardrails/                      # Guardrails module
├── auth/                            # Authentication
├── utils/                           # Shared utilities
├── tests/                           # Test files
├── infrastructure/                  # Infrastructure as Code
│
├── .env.example                     # Environment variables template
├── requirements.txt                 # Python dependencies
├── IMPLEMENTATION_PLAN.md          # Detailed implementation plan
└── GETTING_STARTED.md              # This file
```

### Key Files Explained

**Entry Points:**
- `runtime/agent_runtime.py` - Runtime entrypoint (called by AgentCore)
- `frontend/app.py` - Streamlit entrypoint (run with `streamlit run`)

**Agent Files:**
- `agents/cloud_engineer_agent.py` - Main agent implementation
- `prompts/cloud_engineer/system_prompt.py` - System prompt
- `prompts/cloud_engineer/predefined_tasks.py` - Task definitions

**Configuration:**
- `.env` - Environment variables (create from `.env.example`)
- `requirements.txt` - Python dependencies

### File Relationships

```
frontend/app.py
    ↓ imports
frontend/agent_client.py
    ↓ calls
AgentCore Runtime API
    ↓ invokes
runtime/agent_runtime.py
    ↓ imports
agents/cloud_engineer_agent.py
    ↓ imports
prompts/cloud_engineer/system_prompt.py
    ↓ uses
MCP Tools (AWS CLI, Docs, etc.)
```

---

## Script Execution Guide ⭐ **CRITICAL**

### Pre-Deployment Checklist

Before running any scripts, verify:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **AWS CLI** installed and configured (`aws --version`, `aws configure`)
- [ ] **AWS Credentials** working (`aws sts get-caller-identity`)
- [ ] **Bedrock Model Access** enabled (check in AWS Console)
- [ ] **Cognito User Pool ID** available (or plan to create one)
- [ ] **Virtual Environment** created and activated
- [ ] **Dependencies** installed (`pip install -r requirements.txt`)
- [ ] **.env file** created from `.env.example`

### Script Execution Sequence

#### PHASE 1: ENVIRONMENT SETUP (Day 1)

**Step 1: Validate Environment**
```bash
python scripts/validate_environment.py
```
- **Purpose**: Check all prerequisites before starting
- **What it checks**: Python version, AWS credentials, Bedrock access, Cognito, dependencies, .env file
- **Expected Output**: All checks pass ✅
- **Time**: ~30 seconds
- **Next**: Step 2 (if all pass)

**Step 2: Create/Verify Cognito User Pool**
```bash
# Create new pool
python scripts/create_cognito_pool.py --pool-name cloud-engineer-agent-pool

# OR verify existing pool
python scripts/verify_cognito.py --pool-id <your-pool-id>
```
- **Purpose**: Set up authentication infrastructure
- **What it does**: Creates Cognito User Pool, App Client, configures OAuth, updates .env
- **Expected Output**: Pool created, .env updated with credentials
- **Updates .env**: `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID`
- **Time**: ~2-3 minutes
- **Next**: Step 3

**Step 3: Setup Base AWS Resources**
```bash
python scripts/setup_aws_resources.py
```
- **Purpose**: Create CloudWatch logs, ECR repository
- **What it does**: Creates log groups, ECR repository (optional), log retention policies
- **Expected Output**: Log groups and ECR repository created
- **Time**: ~1-2 minutes
- **Next**: Step 4

**Step 4: Setup Guardrails**
```bash
python scripts/setup_guardrails.py
```
- **Purpose**: Create Bedrock Guardrails for content safety
- **What it does**: Creates guardrail, configures filters, sets topic blocking, updates .env
- **Expected Output**: Guardrail created, .env updated
- **Updates .env**: `BEDROCK_GUARDRAIL_ID`, `BEDROCK_GUARDRAIL_VERSION`
- **Time**: ~1-2 minutes
- **Next**: Step 5

**Step 5: Setup AgentCore Resources**

You have two options:

**Option A: Individual Scripts (More Control)**
```bash
# Create Identity separately
python scripts/create_agentcore_identity.py

# Create Memory separately (optional)
python scripts/create_agentcore_memory.py --enable-ltm
```

**Option B: Combined Script (Faster)**
```bash
# Create Identity + optionally Memory
python scripts/setup_agentcore_resources.py --create-memory
```

- **Purpose**: Create Memory and Identity resources
- **What it does**: 
  - Creates Workload Identity (always)
  - Optionally creates Memory resource (if --create-memory flag used)
  - Updates .env file
- **Expected Output**: Identity created, optionally Memory created, .env updated
- **Updates .env**: `WORKLOAD_IDENTITY_NAME`, `WORKLOAD_IDENTITY_ARN`, optionally `MEMORY_RESOURCE_ARN`, `MEMORY_RESOURCE_ID`
- **Time**: ~1-2 minutes
- **Next**: Step 6

#### PHASE 2: RUNTIME DEPLOYMENT (Day 2-3)

**Step 6: Configure Agent Runtime**
```bash
agentcore configure
```
- **Purpose**: Configure AgentCore Runtime settings
- **What it does**: Prompts for entrypoint, configures OAuth, Memory, execution role, ECR
- **Interactive Prompts**:
  - Entrypoint file: `runtime/agent_runtime.py`
  - OAuth provider: Cognito
  - Cognito User Pool ID: (from .env)
  - Memory strategy: Both (STM + LTM)
  - Network mode: Public (default)
- **Expected Output**: Configuration saved ✅
- **Time**: ~2-3 minutes (interactive)
- **Next**: Step 7

**Step 7: Deploy Agent Runtime**
```bash
agentcore launch
```
- **Purpose**: Deploy agent to AgentCore Runtime
- **What it does**: Builds container image (via CodeBuild), pushes to ECR, creates Memory resource, deploys Runtime, configures Identity, sets up CloudWatch logging
- **Expected Output**: Runtime deployed, endpoint URL provided
- **Updates .env**: `AGENT_RUNTIME_ARN`, `MEMORY_RESOURCE_ARN`
- **Time**: ~10-15 minutes
- **Next**: Step 8

#### PHASE 3: TESTING & VERIFICATION (Day 4)

**Step 8: Test Deployment**
```bash
python scripts/test_deployment.py
```
- **Purpose**: Verify all resources are working
- **What it does**: Validates AWS credentials, Cognito, Guardrails, Runtime access
- **Expected Output**: All tests passed ✅
- **Time**: ~1 minute
- **Next**: Step 9

**Step 9: Test Scalability (Optional)**
```bash
python scripts/test_scalability.py --concurrent-users 100
```
- **Purpose**: Test concurrent user handling
- **What it does**: Sends concurrent requests, measures response times, tracks success rates
- **Expected Output**: Test complete, metrics reported
- **Time**: ~5-10 minutes
- **Next**: Step 10

**Step 10: Run Streamlit UI Locally**
```bash
streamlit run frontend/app.py
```
- **Purpose**: Test UI locally before production deployment
- **What it does**: Starts Streamlit server on `http://localhost:8501`
- **Expected Output**: Streamlit UI accessible in browser
- **Time**: ~10 seconds
- **Next**: Step 11

#### PHASE 4: PRODUCTION DEPLOYMENT (Day 5)

**Step 11: Deploy Streamlit UI to Production**
```bash
python scripts/deploy_streamlit_production.py
```
- **Purpose**: Deploy Streamlit UI to ECS Fargate with ALB
- **What it does**: Creates ECS cluster, Task Definition, ALB, Route 53 record, SSL certificate
- **Expected Output**: Production URL provided
- **Time**: ~15-20 minutes
- **Next**: You're done! 🎉

### What Each Script Does (Detailed)

| Script | Purpose | What It Does | Output | Updates .env |
|--------|---------|--------------|--------|--------------|
| `validate_environment.py` | Check prerequisites | Validates Python, AWS, Bedrock, Cognito, dependencies | Status report | No |
| `create_cognito_pool.py` | Create Cognito pool | Creates User Pool, App Client, configures OAuth | Pool ID, Client ID | Yes |
| `verify_cognito.py` | Verify Cognito pool | Verifies existing Cognito pool configuration | Verification report | Yes |
| `setup_aws_resources.py` | Create AWS resources | Creates CloudWatch logs, ECR repository | Resource ARNs | No |
| `create_guardrail.py` | Create guardrail | Creates Bedrock Guardrail, configures filters | Guardrail ID | Yes |
| `setup_guardrails.py` | Setup guardrails | Creates guardrail with default config | Guardrail ID | Yes |
| `create_agentcore_identity.py` | Create Identity | Creates Workload Identity resource | Identity ARN | Yes |
| `create_agentcore_memory.py` | Create Memory | Creates Memory resource (STM + optional LTM) | Memory ARN, ID | Yes |
| `setup_agentcore_resources.py` | Setup AgentCore resources | Creates Identity + optionally Memory | Resource ARNs | Yes |
| `list_agentcore_resources.py` | List resources | Lists all Memory, Identity, Runtime resources | Resource list | No |
| `verify_agentcore_resources.py` | Verify resources | Verifies all resources exist and are configured | Verification report | No |
| `get_resource_status.py` | Get resource status | Gets detailed status of specific resource | Resource details | No |
| `cleanup_resources.py` | Cleanup resources | Deletes resources (use with caution!) | Deletion report | Yes |
| `destroy_all.py` | Destroy all resources | Destroys ALL resources (complete teardown) | Destruction summary | Yes |
| `test_deployment.py` | Test deployment | Validates all resources | Test results | No |
| `test_scalability.py` | Test scalability | Load tests Runtime | Metrics report | No |
| `deploy_streamlit_production.py` | Deploy UI to production | Creates ECS, ALB, Route 53 | Production URL | Yes |
| `deploy_all.py` | One-command deployment | Orchestrates all setup steps | Deployment summary | Yes |

### Expected Outputs

After completing all steps, you should have:

- ✅ Cognito User Pool ID in `.env`
- ✅ Guardrail ID in `.env`
- ✅ AgentCore Runtime ARN in `.env`
- ✅ Memory Resource ARN in `.env`
- ✅ Production URL for Streamlit UI

### Troubleshooting Each Step

**Step 1 fails**: Check Python version, AWS credentials, Bedrock access

**Step 2 fails**: Verify AWS permissions, check region (`us-east-2`)

**Step 7 fails**: Check `agentcore` CLI is installed, verify .env has all required variables

**Step 10 fails**: Check Streamlit is installed (`pip install streamlit`), verify port 8501 is available

See [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) for detailed troubleshooting.

---

## Common Workflows

### First-Time Setup

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`: `cp .env.example .env`
6. Edit `.env` with your AWS credentials
7. Run Step 1-11 from Script Execution Guide

### Adding a New Agent

1. Create new agent file: `agents/my_new_agent.py`
2. Create prompt folder: `prompts/my_new_agent/`
3. Add system prompt: `prompts/my_new_agent/system_prompt.py`
4. Update `agents/__init__.py` to export new agent
5. Update `runtime/agent_runtime.py` to support new agent (if needed)

### Updating Prompts

1. Edit `prompts/cloud_engineer/system_prompt.py` or `predefined_tasks.py`
2. Restart Streamlit UI (if running locally)
3. Redeploy Runtime (if changes require runtime update): `agentcore launch`

### Testing Changes

1. Test locally: `streamlit run frontend/app.py`
2. Test Runtime: Use `test_deployment.py`
3. Test scalability: Use `test_scalability.py`

### Deployment

1. Run all setup scripts (Steps 1-5)
2. Configure Runtime: `agentcore configure`
3. Deploy Runtime: `agentcore launch`
4. Deploy UI: `python scripts/deploy_streamlit_production.py`

### Daily Development

1. Activate virtual environment
2. Run Streamlit locally: `streamlit run frontend/app.py`
3. Make changes to agents or prompts
4. Test changes in local UI
5. Deploy when ready: `agentcore launch` (for Runtime changes)

---

## Quick Reference

### Command Cheat Sheet

```bash
# Environment Setup
python scripts/validate_environment.py
python scripts/create_cognito_pool.py --pool-name my-pool
python scripts/verify_cognito.py --pool-id <your-pool-id>

# Infrastructure Setup
python scripts/setup_aws_resources.py
python scripts/create_guardrail.py
# OR
python scripts/setup_guardrails.py

# AgentCore Resources (Individual)
python scripts/create_agentcore_identity.py
python scripts/create_agentcore_memory.py --enable-ltm
# OR (Combined)
python scripts/setup_agentcore_resources.py --create-memory

# Resource Management
python scripts/list_agentcore_resources.py --resource-type all
python scripts/verify_agentcore_resources.py --all
python scripts/get_resource_status.py --resource-type memory --resource-id <id>

# Testing
python scripts/test_deployment.py
python scripts/test_scalability.py --concurrent-users 100

# Production Deployment
python scripts/deploy_streamlit_production.py
python scripts/setup_domain.py --domain your-domain.com

# One-Command Deployment
python scripts/deploy_all.py --create-memory

# Cleanup (Use with caution!)
python scripts/cleanup_resources.py --dry-run  # Preview
python scripts/cleanup_resources.py --resource-type all --force

# Destroy ALL resources (Complete teardown)
python scripts/destroy_all.py --dry-run  # Preview first!
python scripts/destroy_all.py --force  # ⚠️ IRREVERSIBLE!

### File Locations

- **Agent**: `agents/cloud_engineer_agent.py`
- **Prompts**: `prompts/cloud_engineer/`
- **Runtime Entrypoint**: `runtime/agent_runtime.py`
- **UI Entrypoint**: `frontend/app.py`
- **Configuration**: `.env`

### Resource Management Scripts

**New!** Individual scripts for managing resources:

```bash
# List all resources
python scripts/list_agentcore_resources.py --resource-type all

# Verify resources exist
python scripts/verify_agentcore_resources.py --all

# Get detailed status of specific resource
python scripts/get_resource_status.py --resource-type memory --resource-id <id>

# Cleanup resources (use with caution!)
python scripts/cleanup_resources.py --dry-run  # Preview first
python scripts/cleanup_resources.py --resource-type memory --force
```

### Common Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-2

# Check Cognito pools
aws cognito-idp list-user-pools --max-results 10 --region us-east-2

# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtimes --follow --region us-east-2

# List AgentCore resources
python scripts/list_agentcore_resources.py --resource-type all
```

### Environment Variables

Key variables in `.env`:

- `AWS_REGION` - AWS region (us-east-2)
- `COGNITO_USER_POOL_ID` - Cognito User Pool ID
- `COGNITO_CLIENT_ID` - Cognito App Client ID
- `BEDROCK_GUARDRAIL_ID` - Guardrail ID
- `AGENT_RUNTIME_ARN` - Runtime ARN (after deployment)
- `MEMORY_RESOURCE_ARN` - Memory ARN (after deployment)

See `.env.example` for complete list.

---

## FAQ

### Q: How do I check if my resources exist?

A: Use `python scripts/list_agentcore_resources.py --resource-type all` or `python scripts/verify_agentcore_resources.py --all`

### Q: How do I create Memory separately?

A: Run `python scripts/create_agentcore_memory.py --enable-ltm`. See [Script Execution Guide](#script-execution-guide) for details.

### Q: How do I verify all resources are configured correctly?

A: Run `python scripts/verify_agentcore_resources.py --all`

### Q: How do I get detailed status of a resource?

A: Use `python scripts/get_resource_status.py --resource-type memory --resource-id <id>`

### Q: How do I clean up resources?

A: First preview with `python scripts/cleanup_resources.py --dry-run`, then run `python scripts/cleanup_resources.py --resource-type all --force` (use with caution!)

### Q: How do I know if my environment is ready?

A: Run `python scripts/validate_environment.py`. It checks everything!

### Q: Do I need Docker for local development?

A: No, Docker is only needed for production deployment. You can run Streamlit locally without Docker.

### Q: How do I add more users?

A: Create users in Cognito User Pool via AWS Console or CLI:
```bash
aws cognito-idp admin-create-user \
  --user-pool-id <your-pool-id> \
  --username newuser \
  --region us-east-2
```

### Q: How do I view logs?

A: Use CloudWatch Console or CLI:
```bash
aws logs tail /aws/bedrock-agentcore/runtimes --follow --region us-east-2
```

### Q: How do I update the agent?

A: Edit `agents/cloud_engineer_agent.py` or prompts, then redeploy: `agentcore launch`

### Q: How do I test locally without deploying Runtime?

A: You can't test AgentCore Runtime locally - it's serverless. But you can test the agent logic by importing it directly in a Python script.

### Q: What if deployment fails?

A: Check CloudWatch logs, verify .env has all required variables, ensure AWS permissions are correct. See troubleshooting section in IMPLEMENTATION_PLAN.md.

---

## Where to Get Help

1. **Documentation**: Read `IMPLEMENTATION_PLAN.md` for detailed information
2. **Scripts**: Check script docstrings for usage: `python scripts/<script>.py --help`
3. **AWS Documentation**: 
   - [AgentCore Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)
   - [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
   - [Cognito Documentation](https://docs.aws.amazon.com/cognito/)
4. **Strands Agents**: [Strands Agents Documentation](https://docs.strands.ai/)
5. **CloudWatch Logs**: Check logs for runtime errors
6. **AWS Support**: Use AWS Support if needed

---

## Next Steps After Setup

1. ✅ Complete all script execution steps (Steps 1-11)
2. ✅ Test the application end-to-end
3. ✅ Review `IMPLEMENTATION_PLAN.md` for advanced features
4. ✅ Set up monitoring and alerting
5. ✅ Plan for SSO integration (Phase 2)

---

**Ready to start?** Begin with Step 1: `python scripts/validate_environment.py`

Good luck! 🚀

