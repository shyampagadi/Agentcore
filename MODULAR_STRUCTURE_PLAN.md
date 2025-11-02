# Modular Structure & Newbie Guide - Implementation Plan

## 📋 Overview

This plan outlines:
1. **Modular Agent Structure** - `agents/` folder for multiple agents
2. **Modular Prompt Structure** - `prompts/` folder for prompt management
3. **Comprehensive Newbie Guide** - `GETTING_STARTED.md` explaining flow, scripts, and execution sequence

---

## 1. Agents Folder Structure (`agents/`) - SIMPLIFIED

### Purpose
- **Modularity**: Add new agents without modifying existing code
- **Separation of Concerns**: Each agent is self-contained
- **Simple Structure**: Direct imports, no complex patterns

### Proposed Structure (SIMPLIFIED)

```
agents/
├── __init__.py                          # Package marker (simple exports)
├── cloud_engineer_agent.py              # Main cloud engineer agent (moved from root)
│
└── tools/                               # Agent-specific tools (optional)
    ├── __init__.py
    └── mcp_setup.py                    # MCP client setup utilities (if needed)
```

### File Responsibilities

#### `agents/cloud_engineer_agent.py`
- **Purpose**: Main cloud engineer agent (moved from root)
- **What it does**:
  - Current agent implementation (all existing functionality preserved)
  - Imports prompts from `prompts/cloud_engineer/` folder
  - Direct Strands Agent creation (no factory needed)
- **Changes needed**:
  - Move from root to `agents/`
  - Import system prompt from `prompts/cloud_engineer/system_prompt.py`
  - Import PREDEFINED_TASKS from `prompts/cloud_engineer/predefined_tasks.py`
- **Functionality preserved**:
  - All existing functionality
  - MCP tools integration
  - System prompt
  - Predefined tasks
- **Usage**:
  ```python
  from agents.cloud_engineer_agent import execute_custom_task, execute_predefined_task
  # Direct import, simple usage
  ```

#### `agents/tools/mcp_setup.py` (Optional)
- **Purpose**: Shared MCP client setup utilities (if needed)
- **What it does**:
  - Centralized MCP client initialization
  - Handles platform-specific setup (Windows vs Linux)
- **Note**: Only create if MCP setup logic needs to be shared

### Benefits of This Simple Structure

1. **Easy to Add New Agents**:
   - Create new agent file (e.g., `agents/cost_optimizer_agent.py`)
   - Import it directly where needed
   - No factory, no registry needed

2. **Clear Separation**:
   - Each agent is self-contained
   - Prompts are separate (in `prompts/` folder)
   - Simple direct imports

3. **Strands-Friendly**:
   - Works directly with Strands Agent pattern
   - No abstraction layers
   - Easy to understand and maintain

---

## 2. Prompts Folder Structure (`prompts/`)

### Purpose
- **Centralized Prompt Management**: All prompts in one place
- **Version Control**: Track prompt changes
- **Reusability**: Share prompts across agents
- **Easy Updates**: Modify prompts without code changes

### Proposed Structure

```
prompts/
├── __init__.py                          # Package marker (simple exports)
│
├── cloud_engineer/                      # Cloud engineer agent prompts
│   ├── __init__.py
│   ├── system_prompt.py                # Main system prompt (moved from cloud_engineer_agent.py)
│   └── predefined_tasks.py              # Predefined tasks dictionary (moved from cloud_engineer_agent.py)
│
└── common/                              # Shared prompts (optional)
    ├── __init__.py
    └── error_handling.py               # Error message prompts (if needed)
```

### File Responsibilities

#### `prompts/cloud_engineer/system_prompt.py`
- **Purpose**: Main system prompt for cloud engineer agent
- **What it contains**:
  - Complete system prompt string (moved from `cloud_engineer_agent.py`)
  - Formatting placeholders (e.g., `{RESOLVED_AWS_REGION}`)
  - Simple function to get formatted prompt
- **Usage**:
  ```python
  from prompts.cloud_engineer.system_prompt import get_system_prompt
  
  system_prompt = get_system_prompt(region="us-east-2")
  ```
- **Benefits**: Easy to modify prompt without touching agent code
- **Structure**:
  ```python
  SYSTEM_PROMPT_TEMPLATE = """
  ... (prompt content here) ...
  """
  
  def get_system_prompt(region: str) -> str:
      return SYSTEM_PROMPT_TEMPLATE.format(RESOLVED_AWS_REGION=region)
  ```

#### `prompts/cloud_engineer/predefined_tasks.py`
- **Purpose**: Predefined tasks dictionary
- **What it contains**:
  - PREDEFINED_TASKS dictionary (moved from `cloud_engineer_agent.py`)
  - Task descriptions
- **Usage**:
  ```python
  from prompts.cloud_engineer.predefined_tasks import PREDEFINED_TASKS
  
  task_description = PREDEFINED_TASKS.get("ec2_status")
  ```
- **Benefits**: Easy to add/modify tasks without code changes
- **Structure**: Simple dictionary (keep existing format)

#### `prompts/common/error_handling.py` (Optional)
- **Purpose**: Shared error handling prompts (only if needed)
- **What it contains**:
  - Error message templates
  - User-friendly error messages
- **Note**: Only create if error messages need to be shared across agents

### Benefits of This Simple Structure

1. **Easy Prompt Updates**:
   - Modify prompts without code changes
   - Simple file-based organization
   - Direct imports

2. **Simple Organization**:
   - Clear structure by agent
   - Easy to find prompts
   - No complex managers needed

3. **Direct Usage**:
   - Simple imports: `from prompts.cloud_engineer.system_prompt import get_system_prompt`
   - No abstraction layers
   - Easy to understand

---

## 3. Comprehensive Newbie Guide (`GETTING_STARTED.md`)

### Purpose
- **Onboarding**: Help newbies understand the project
- **Flow Explanation**: Explain how everything works together
- **Script Guide**: What each script does and when to use it
- **Execution Sequence**: Step-by-step execution order
- **Troubleshooting**: Quick reference for common issues

### Proposed Structure

```
GETTING_STARTED.md

Table of Contents:
1. Welcome & Project Overview
2. Architecture Overview (with diagrams)
3. System Flow (How Everything Works Together)
4. Project Structure Explained
5. Script Execution Guide (CRITICAL SECTION)
   - Pre-deployment Checklist
   - Script Execution Sequence (Step-by-Step)
   - What Each Script Does (Detailed)
   - Expected Outputs
   - Troubleshooting Each Step
6. Common Workflows
   - First-Time Setup
   - Adding a New Agent
   - Updating Prompts
   - Testing Changes
   - Deployment
   - Daily Development
7. Quick Reference
   - Command Cheat Sheet
   - File Locations
   - Common Commands
   - Environment Variables
8. Next Steps After Setup
9. FAQ
10. Where to Get Help
```

### Detailed Content Plan

#### Section 1: Welcome & Project Overview
- **What this project does**: Enterprise cloud engineer agent using AWS Bedrock AgentCore
- **Key technologies**: AgentCore Runtime, Streamlit, Cognito, Bedrock, Memory, Guardrails
- **Target users**: Cloud engineers, DevOps teams, AWS administrators
- **Prerequisites**: Listed clearly with links to setup guides
- **Project goals**: Multi-user, scalable, secure cloud engineering assistant

#### Section 2: Architecture Overview

**2.1 Visual Architecture Diagram (ASCII)**
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
└────────┬────────────────────────┘
         │ API Call (HTTPS)
         │ Session ID + JWT Token
         ▼
┌─────────────────────────────────┐
│   AgentCore Runtime (Backend)    │
│  - MicroVM per Session           │
│  - Auto-scaling                 │
│  - Session Isolation            │
└────────┬────────────────────────┘
         │ Agent Execution
         ▼
┌─────────────────────────────────┐
│   Cloud Engineer Agent          │
│  - Strands Agent                │
│  - MCP Tools                    │
│  - Bedrock Model               │
└────────┬────────────────────────┘
         │ Memory Operations
         │ Guardrail Checks
         ▼
┌─────────────────────────────────┐
│   AgentCore Memory              │
│  - Conversation History         │
│  - Knowledge Base               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│   Bedrock Guardrails             │
│  - Content Filtering             │
│  - PII Protection                │
└─────────────────────────────────┘
```

**2.2 Components Explained**
- **Streamlit UI**: Frontend web interface
- **AgentCore Runtime**: Serverless runtime environment
- **Agent**: Core Strands agent with AWS tools
- **Memory**: Conversation persistence
- **Guardrails**: Content safety and compliance
- **Identity**: Cognito authentication

**2.3 Data Flow**
- Request flow: User → Streamlit → Runtime → Agent → AWS
- Response flow: AWS → Agent → Runtime → Streamlit → User
- Memory flow: Agent → Memory (save) → Memory → Agent (load)

#### Section 3: System Flow (Detailed Step-by-Step)

**3.1 Complete User Journey**

```
Step 1: User Opens Streamlit UI
├── URL: http://localhost:8501 (dev) or https://your-domain.com (prod)
├── What happens: Streamlit server starts, shows login page
└── Files involved: frontend/app.py, frontend/auth_ui.py

Step 2: User Authenticates
├── User enters username/password
├── What happens: 
│   ├── frontend/auth_ui.py calls auth/cognito_client.py
│   ├── Cognito validates credentials
│   ├── Returns JWT tokens (access, ID, refresh)
│   └── Streamlit stores tokens in session state
└── Files involved: auth/cognito_client.py, identity/jwt_validator.py

Step 3: User Sends Message
├── User types message in chat interface
├── What happens:
│   ├── frontend/app.py calls frontend/session_manager.py
│   ├── Generates/retrieves session ID
│   ├── frontend/agent_client.py prepares request
│   └── Calls AgentCore Runtime API
└── Files involved: frontend/agent_client.py, frontend/session_manager.py

Step 4: Request Reaches AgentCore Runtime
├── Runtime receives request with session_id and JWT token
├── What happens:
│   ├── Runtime validates JWT token (identity/jwt_validator.py)
│   ├── Creates/retrieves microVM for session_id
│   ├── Calls runtime/agent_runtime.py → handle_invocation()
│   └── Extracts prompt from payload
└── Files involved: runtime/agent_runtime.py, runtime/session_handler.py

Step 5: Agent Processes Request
├── Runtime calls agent execution
├── What happens:
│   ├── runtime/memory_integration.py loads conversation history
│   ├── runtime/context_builder.py builds context
│   ├── runtime/guardrail_integration.py checks input
│   ├── agents/cloud_engineer_agent.py executes with tools
│   ├── Agent calls AWS services via MCP tools
│   ├── Agent generates response
│   ├── runtime/guardrail_integration.py checks output
│   └── runtime/memory_integration.py saves conversation
└── Files involved: runtime/agent_runtime.py, agents/cloud_engineer_agent.py

Step 6: Response Returned
├── Agent returns response
├── What happens:
│   ├── Runtime formats response
│   ├── Returns to Streamlit via API
│   └── Streamlit displays response
└── Files involved: frontend/app.py, frontend/response_handler.py

Step 7: User Sees Response
├── Response displayed in chat interface
├── What happens:
│   ├── frontend/app.py displays message
│   ├── frontend/chat_interface.py formats message
│   └── Updates chat history
└── Files involved: frontend/app.py, frontend/chat_interface.py
```

**3.2 Session Management Flow**
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

**3.3 Memory Integration Flow**
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

**3.4 Guardrail Integration Flow**
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

#### Section 4: Project Structure Explained

**4.1 Directory Structure (Detailed)**

```
maygum-agentcore/
├── agents/                          # ⭐ NEW: Modular agents
│   ├── cloud_engineer_agent.py     # Main agent (moved from root)
│   ├── base_agent.py               # Base agent class
│   ├── agent_factory.py            # Agent factory
│   └── config/                     # Agent configurations
│
├── prompts/                         # ⭐ NEW: Modular prompts
│   ├── cloud_engineer/
│   │   ├── system_prompt.py        # System prompt
│   │   └── predefined_tasks.py     # Predefined tasks
│   └── common/                     # Shared prompts
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
└── infrastructure/                  # Infrastructure as Code
```

**4.2 Key Files Explained**

- **Entry Points**:
  - `runtime/agent_runtime.py` - Runtime entrypoint (called by AgentCore)
  - `frontend/app.py` - Streamlit entrypoint (run with `streamlit run`)
  
- **Agent Files**:
  - `agents/cloud_engineer_agent.py` - Main agent implementation
  - `agents/base_agent.py` - Base agent class
  
- **Prompt Files**:
  - `prompts/cloud_engineer/system_prompt.py` - System prompt
  - `prompts/cloud_engineer/predefined_tasks.py` - Task definitions
  
- **Configuration**:
  - `.env` - Environment variables (create from .env.example)
  - `requirements.txt` - Python dependencies

**4.3 File Relationships**

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
agents/tools/mcp_setup.py
```

#### Section 5: Script Execution Guide (CRITICAL SECTION)

**5.1 Pre-Deployment Checklist**

Before running any scripts, verify:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **AWS CLI** installed and configured (`aws --version`, `aws configure`)
- [ ] **AWS Credentials** working (`aws sts get-caller-identity`)
- [ ] **Bedrock Model Access** enabled (check in AWS Console)
- [ ] **Cognito User Pool ID** available (or plan to create one)
- [ ] **Virtual Environment** created and activated
- [ ] **Dependencies** installed (`pip install -r requirements.txt`)
- [ ] **.env file** created from `.env.example`

**5.2 Script Execution Sequence**

```
═══════════════════════════════════════════════════════════════
PHASE 1: ENVIRONMENT SETUP (Day 1)
═══════════════════════════════════════════════════════════════

Step 1: Validate Environment
├── Script: scripts/validate_environment.py
├── Command: python scripts/validate_environment.py
├── Purpose: Check all prerequisites before starting
├── What it checks:
│   ├── Python version (3.10+)
│   ├── AWS credentials
│   ├── AWS region accessibility
│   ├── Bedrock model access
│   ├── Cognito User Pool accessibility
│   ├── Python dependencies
│   └── .env file exists
├── Expected Output:
│   ✅ Python 3.11.0 (meets requirement: 3.10+)
│   ✅ AWS credentials valid
│   ✅ Region us-east-2 accessible
│   ✅ Bedrock model access enabled
│   ✅ Cognito User Pool accessible
│   ✅ All required packages installed
│   ✅ .env file exists and has required variables
├── If fails: Fix issues, rerun
├── Time: ~30 seconds
└── Next Step: Step 2 (if all pass)

═══════════════════════════════════════════════════════════════
PHASE 2: INFRASTRUCTURE SETUP (Day 2)
═══════════════════════════════════════════════════════════════

Step 2: Create/Verify Cognito User Pool
├── Script: scripts/create_cognito_pool.py OR scripts/verify_cognito.py
├── Command Options:
│   ├── Create new: python scripts/create_cognito_pool.py --pool-name cloud-engineer-agent-pool
│   └── Verify existing: python scripts/verify_cognito.py --pool-id <your-pool-id>
├── Purpose: Set up authentication infrastructure
├── What it does:
│   ├── Creates Cognito User Pool (if creating new)
│   ├── Creates App Client for Streamlit
│   ├── Configures OAuth flows
│   ├── Sets callback URLs
│   └── Updates .env file with credentials
├── Expected Output:
│   ✅ Cognito User Pool created: us-east-2_abc123def
│   ✅ App client created: 1a2b3c4d5e6f7g8h9i0j
│   ✅ Updated .env file with Cognito credentials
├── Updates .env: COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID
├── Time: ~2-3 minutes
└── Next Step: Step 3

Step 3: Setup Base AWS Resources
├── Script: scripts/setup_aws_resources.py
├── Command: python scripts/setup_aws_resources.py
├── Purpose: Create CloudWatch logs, ECR repository (if needed)
├── What it does:
│   ├── Creates CloudWatch log groups
│   ├── Creates ECR repository (optional)
│   └── Sets up log retention policies
├── Expected Output:
│   ✅ Created log group: /aws/bedrock-agentcore/runtimes
│   ✅ Created log group: /aws/bedrock-agentcore/memory
│   ✅ Created ECR repository: cloud-engineer-agent-runtime
├── Time: ~1-2 minutes
└── Next Step: Step 4

Step 4: Setup Guardrails
├── Script: scripts/setup_guardrails.py
├── Command: python scripts/setup_guardrails.py
├── Purpose: Create Bedrock Guardrails for content safety
├── What it does:
│   ├── Creates Bedrock Guardrail
│   ├── Configures content filters
│   ├── Sets up topic blocking
│   └── Updates .env file with guardrail ID
├── Expected Output:
│   ✅ Guardrail created: guardrail-1234567890abcdef
│   ✅ Updated .env file with guardrail ID
├── Updates .env: BEDROCK_GUARDRAIL_ID, BEDROCK_GUARDRAIL_VERSION
├── Time: ~1-2 minutes
└── Next Step: Step 5

Step 5: Setup AgentCore Resources
├── Script: scripts/setup_agentcore_resources.py
├── Command: python scripts/setup_agentcore_resources.py
├── Purpose: Create Memory and Identity resources
├── What it does:
│   ├── Creates Workload Identity
│   └── Updates .env file with identity ARN
├── Expected Output:
│   ✅ Workload Identity created: arn:aws:bedrock-agentcore:...
│   ✅ Updated .env file
├── Note: Memory resource will be created by agentcore launch
├── Updates .env: WORKLOAD_IDENTITY_NAME
├── Time: ~1 minute
└── Next Step: Step 6

═══════════════════════════════════════════════════════════════
PHASE 3: RUNTIME DEPLOYMENT (Day 3-4)
═══════════════════════════════════════════════════════════════

Step 6: Configure Agent Runtime
├── Commands: agentcore configure
├── Purpose: Configure AgentCore Runtime settings
├── What it does:
│   ├── Prompts for entrypoint file (runtime/agent_runtime.py)
│   ├── Configures OAuth with Cognito
│   ├── Configures Memory (STM + LTM)
│   ├── Sets execution role (auto-created)
│   └── Sets ECR repository (auto-created)
├── Interactive Prompts:
│   ├── Entrypoint file: runtime/agent_runtime.py
│   ├── OAuth provider: Cognito
│   ├── Cognito User Pool ID: (from .env)
│   ├── Memory strategy: Both (STM + LTM)
│   └── Network mode: Public (default)
├── Expected Output:
│   ✅ Configuration saved
│   ✅ Ready to launch
├── Time: ~2-3 minutes (interactive)
└── Next Step: Step 7

Step 7: Deploy Agent Runtime
├── Commands: agentcore launch
├── Purpose: Deploy agent to AgentCore Runtime
├── What it does:
│   ├── Builds container image (via CodeBuild)
│   ├── Pushes to ECR
│   ├── Creates Memory resource
│   ├── Deploys Runtime
│   ├── Configures Identity
│   └── Sets up CloudWatch logging
├── Expected Output:
│   ✅ Container image built and pushed
│   ✅ Memory resource created: arn:aws:bedrock-agentcore:...
│   ✅ Runtime deployed: arn:aws:bedrock-agentcore:...
│   ✅ Runtime endpoint: https://runtime-id.bedrock-agentcore...
├── Updates .env: AGENT_RUNTIME_ARN, MEMORY_RESOURCE_ARN
├── Time: ~10-15 minutes
└── Next Step: Step 8

═══════════════════════════════════════════════════════════════
PHASE 4: TESTING & VERIFICATION (Day 5)
═══════════════════════════════════════════════════════════════

Step 8: Test Deployment
├── Script: scripts/test_deployment.py
├── Command: python scripts/test_deployment.py
├── Purpose: Verify all resources are working
├── What it does:
│   ├── Validates AWS credentials
│   ├── Verifies Cognito configuration
│   ├── Checks Guardrails configuration
│   ├── Tests AgentCore Runtime access
│   └── Verifies service access
├── Expected Output:
│   ✅ All deployment tests passed!
├── Time: ~1 minute
└── Next Step: Step 9

Step 9: Test Scalability (Optional)
├── Script: scripts/test_scalability.py
├── Command: python scripts/test_scalability.py --concurrent-users 100
├── Purpose: Test concurrent user handling
├── What it does:
│   ├── Sends concurrent requests to Runtime
│   ├── Measures response times
│   ├── Tracks success rates
│   └── Reports metrics
├── Expected Output:
│   ✅ Test complete!
│   ✅ Successful: 100/100
│   ✅ Average response time: 2.5s
├── Time: ~5-10 minutes
└── Next Step: Step 10 (if deploying to production)

═══════════════════════════════════════════════════════════════
PHASE 5: FRONTEND DEPLOYMENT (Optional - Production)
═══════════════════════════════════════════════════════════════

Step 10: Deploy Streamlit UI to Production
├── Script: scripts/deploy_streamlit_production.py
├── Command: python scripts/deploy_streamlit_production.py
├── Purpose: Deploy Streamlit UI to ECS Fargate with ALB
├── What it does:
│   ├── Builds Docker image
│   ├── Pushes to ECR
│   ├── Creates ECS cluster and service
│   ├── Sets up Application Load Balancer
│   └── Configures HTTPS
├── Expected Output:
│   ✅ Streamlit UI deployed
│   ✅ URL: https://your-alb-url.us-east-2.elb.amazonaws.com
├── Time: ~15-20 minutes
└── Next Step: Step 11

Step 11: Setup Domain Name (Optional)
├── Script: scripts/setup_domain.py
├── Command: python scripts/setup_domain.py --domain your-domain.com
├── Purpose: Configure custom domain with SSL
├── What it does:
│   ├── Requests SSL certificate from ACM
│   ├── Creates Route 53 hosted zone (if needed)
│   ├── Updates ALB with certificate
│   └── Configures DNS records
├── Expected Output:
│   ✅ Domain configured: https://your-domain.com
├── Time: ~10-15 minutes
└── Next Step: Done!
```

**5.3 One-Command Deployment (Alternative)**

Instead of running scripts individually:

```bash
# Option 1: Python script
python scripts/deploy_all.py --cognito-pool-id <your-pool-id> --region us-east-2

# Option 2: Shell script
bash scripts/deploy_all.sh
```

**What it does**: Runs Steps 1-5 automatically in sequence

**When to use**: After initial setup, for automated deployments

**5.4 What Each Script Does (Detailed Table)**

| Script | Purpose | When to Run | Input | Output | Time | Next Step |
|--------|---------|-------------|-------|--------|------|-----------|
| `validate_environment.py` | Check prerequisites | FIRST | None | Validation results | 30s | Step 2 |
| `create_cognito_pool.py` | Create Cognito pool | If no pool exists | Pool name | Pool ID, Client ID | 2-3m | Step 3 |
| `verify_cognito.py` | Verify existing pool | If pool exists | Pool ID | Verification results | 1m | Step 3 |
| `setup_aws_resources.py` | Create AWS resources | After Cognito | None | Log groups, ECR repo | 1-2m | Step 4 |
| `setup_guardrails.py` | Create guardrails | After AWS resources | None | Guardrail ID | 1-2m | Step 5 |
| `setup_agentcore_resources.py` | Create AgentCore resources | After guardrails | None | Identity ARN | 1m | Step 6 |
| `agentcore configure` | Configure runtime | After resources | Interactive | Config file | 2-3m | Step 7 |
| `agentcore launch` | Deploy runtime | After configure | None | Runtime ARN | 10-15m | Step 8 |
| `test_deployment.py` | Test deployment | After launch | None | Test results | 1m | Step 9 |
| `test_scalability.py` | Test scalability | After tests | Concurrent users | Metrics | 5-10m | Done |

**5.5 Troubleshooting Each Step**

For each step, provide:
- **Common errors** and solutions
- **How to verify** step completed successfully
- **What to check** if something fails
- **Rollback steps** if needed

**Example format for each script:**

```
Script: scripts/validate_environment.py
├── Common Errors:
│   ├── "AWS credentials not found"
│   │   └── Solution: Run `aws configure` or set AWS_ACCESS_KEY_ID
│   ├── "Bedrock model access denied"
│   │   └── Solution: Enable model access in AWS Console → Bedrock → Model access
│   └── "Cognito User Pool not found"
│       └── Solution: Check COGNITO_USER_POOL_ID in .env file
├── How to Verify:
│   └── All checks show ✅ (green checkmarks)
├── What to Check:
│   ├── AWS credentials: `aws sts get-caller-identity`
│   ├── Bedrock access: `aws bedrock list-foundation-models --region us-east-2`
│   └── Cognito access: `aws cognito-idp list-user-pools --region us-east-2`
└── Rollback: Not needed (validation only)
```

#### Section 6: Common Workflows

**6.1 First-Time Setup Workflow (Complete)**

```
Day 1: Environment Setup
├── Install Python 3.10+
├── Install AWS CLI
├── Configure AWS credentials
├── Enable Bedrock model access
├── Get Cognito User Pool ID (or create one)
├── Create virtual environment
├── Install dependencies
└── Create .env file

Day 2: Infrastructure Setup
├── Run: python scripts/validate_environment.py
├── Run: python scripts/create_cognito_pool.py --pool-name my-pool
│   OR: python scripts/verify_cognito.py --pool-id <existing-pool-id>
├── Run: python scripts/setup_aws_resources.py
├── Run: python scripts/setup_guardrails.py
└── Run: python scripts/setup_agentcore_resources.py

Day 3-4: Runtime Deployment
├── Run: agentcore configure
│   ├── Entrypoint: runtime/agent_runtime.py
│   ├── OAuth: Cognito
│   └── Memory: Both (STM + LTM)
└── Run: agentcore launch
    └── Wait for deployment (~10-15 minutes)

Day 5: Testing
├── Run: python scripts/test_deployment.py
├── Run: python scripts/test_scalability.py --concurrent-users 10
└── Test locally: streamlit run frontend/app.py
```

**6.2 Adding a New Agent Workflow (SIMPLIFIED)**

```
1. Create agents/new_agent.py
   ├── Create Strands Agent (same pattern as cloud_engineer_agent.py)
   ├── Import tools as needed
   └── Add agent-specific logic

2. Create prompts/new_agent/ directory
   ├── Create prompts/new_agent/system_prompt.py
   ├── Create prompts/new_agent/predefined_tasks.py (if needed)
   └── Define prompts

3. Update runtime (if needed)
   ├── Import new agent: from agents.new_agent import execute_custom_task
   └── Use agent as needed

4. Test locally
   ├── python runtime/test_runtime_local.py
   └── Test agent functionality

5. Deploy
   └── agentcore launch (re-deploys runtime)
```

**6.3 Updating Prompts Workflow**

```
1. Edit prompt file
   └── prompts/cloud_engineer/system_prompt.py

2. Test locally
   ├── python runtime/test_runtime_local.py
   └── Verify prompt changes

3. Deploy
   └── agentcore launch (re-deploys runtime)

4. Verify
   └── Test in Streamlit UI
```

**6.4 Testing Changes Workflow**

```
1. Run unit tests
   └── pytest tests/unit/

2. Run integration tests
   └── pytest tests/integration/

3. Test runtime locally
   └── python runtime/test_runtime_local.py

4. Test scalability
   └── python scripts/test_scalability.py --concurrent-users 10
```

**6.5 Daily Development Workflow**

```
1. Activate virtual environment
   └── source .venv/bin/activate  (Linux/Mac)
   └── .venv\Scripts\activate     (Windows)

2. Start Streamlit locally
   └── streamlit run frontend/app.py

3. Make changes
   └── Edit files as needed

4. Test changes
   └── Refresh browser, test functionality

5. Commit changes
   └── git add, git commit
```

#### Section 7: Quick Reference

**7.1 Command Cheat Sheet**

```bash
# Environment Validation
python scripts/validate_environment.py

# Cognito Setup
python scripts/create_cognito_pool.py --pool-name my-pool
python scripts/verify_cognito.py --pool-id <pool-id>

# Infrastructure Setup
python scripts/setup_aws_resources.py
python scripts/setup_guardrails.py
python scripts/setup_agentcore_resources.py

# Runtime Deployment
agentcore configure --entrypoint runtime/agent_runtime.py
agentcore launch

# Testing
python scripts/test_deployment.py
python scripts/test_scalability.py --concurrent-users 100
python runtime/test_runtime_local.py

# Frontend
streamlit run frontend/app.py
streamlit run frontend/app.py --server.port 8501

# One-Command Deployment
python scripts/deploy_all.py --cognito-pool-id <pool-id>
bash scripts/deploy_all.sh

# Configuration Updates
python scripts/update_config.py --key AGENT_RUNTIME_ARN --value <arn>

# Rollback
python scripts/rollback.py --resource-type runtime
```

**7.2 File Locations Quick Reference**

```
Entry Points:
├── Runtime: runtime/agent_runtime.py
├── Frontend: frontend/app.py
└── Agent: agents/cloud_engineer_agent.py

Configuration:
├── Environment: .env
├── Requirements: requirements.txt
└── Agent Config: agents/config/cloud_engineer_config.py

Prompts:
├── System Prompt: prompts/cloud_engineer/system_prompt.py
└── Tasks: prompts/cloud_engineer/predefined_tasks.py

Scripts:
├── Validation: scripts/validate_environment.py
├── Cognito: scripts/create_cognito_pool.py, scripts/verify_cognito.py
├── Setup: scripts/setup_*.py
└── Testing: scripts/test_*.py
```

**7.3 Environment Variables Quick Reference**

```
Required:
├── AWS_REGION=us-east-2
├── AWS_ACCOUNT_ID=<your-account-id>
├── COGNITO_USER_POOL_ID=<pool-id>
└── COGNITO_CLIENT_ID=<client-id>

Generated (by scripts):
├── AGENT_RUNTIME_ARN=<runtime-arn>
├── MEMORY_RESOURCE_ARN=<memory-arn>
├── BEDROCK_GUARDRAIL_ID=<guardrail-id>
└── WORKLOAD_IDENTITY_NAME=<identity-name>
```

**7.4 Common Commands**

```bash
# Check AWS credentials
aws sts get-caller-identity

# List Bedrock models
aws bedrock list-foundation-models --region us-east-2

# List Cognito pools
aws cognito-idp list-user-pools --max-results 10 --region us-east-2

# Check AgentCore Runtime
agentcore runtime list

# View logs
aws logs tail /aws/bedrock-agentcore/runtimes --follow
```

---

#### Section 8: Next Steps After Setup

**8.1 Development**
- Start Streamlit locally: `streamlit run frontend/app.py`
- Make changes to agents/prompts
- Test locally before deploying

**8.2 Testing**
- Run unit tests: `pytest tests/unit/`
- Run integration tests: `pytest tests/integration/`
- Test scalability: `python scripts/test_scalability.py`

**8.3 Deployment**
- Deploy updates: `agentcore launch`
- Verify deployment: `python scripts/test_deployment.py`

**8.4 Monitoring**
- CloudWatch logs: Check `/aws/bedrock-agentcore/runtimes`
- CloudWatch metrics: Check AgentCore metrics
- Guardrail violations: Check guardrail dashboard

---

#### Section 9: FAQ

**Q: Where do I start?**
A: Start with `GETTING_STARTED.md` → Section 5 → Step 1: Validate Environment

**Q: What script should I run first?**
A: `python scripts/validate_environment.py` - validates all prerequisites

**Q: Do I need to run all scripts?**
A: Yes, in sequence. Use `python scripts/deploy_all.py` for automation.

**Q: How do I add a new agent?**
A: See Section 6.2 → Adding a New Agent Workflow

**Q: How do I update prompts?**
A: Edit `prompts/cloud_engineer/system_prompt.py`, then `agentcore launch`

**Q: How do I test locally?**
A: `python runtime/test_runtime_local.py` or `streamlit run frontend/app.py`

**Q: Where are the logs?**
A: CloudWatch → `/aws/bedrock-agentcore/runtimes`

**Q: How do I know if deployment succeeded?**
A: Run `python scripts/test_deployment.py` - should show all ✅

**Q: Can I skip some steps?**
A: No, each step builds on previous steps. Follow the sequence.

**Q: What if a script fails?**
A: See Section 5.5 → Troubleshooting Each Step for that specific script

---

#### Section 10: Where to Get Help

- **Documentation**: `IMPLEMENTATION_PLAN.md` - Complete implementation guide
- **Troubleshooting**: `IMPLEMENTATION_PLAN.md` → Troubleshooting Guide
- **API Reference**: `docs/api-reference.md` - API documentation
- **Code Examples**: See docstrings in each module file
- **Common Issues**: `GETTING_STARTED.md` → Section 5.5 (Troubleshooting)

---

## 4. Required Code Changes Summary

### Files to Move
1. `cloud_engineer_agent.py` → `agents/cloud_engineer_agent.py`
2. System prompt → `prompts/cloud_engineer/system_prompt.py`
3. PREDEFINED_TASKS → `prompts/cloud_engineer/predefined_tasks.py`

### Files to Create
1. **Agents Module** (2-3 files, SIMPLIFIED):
   - `agents/cloud_engineer_agent.py` (moved from root)
   - `agents/__init__.py` (simple exports)
   - `agents/tools/mcp_setup.py` (optional, only if MCP setup needs to be shared)

2. **Prompts Module** (3-4 files, SIMPLIFIED):
   - `prompts/cloud_engineer/system_prompt.py` (moved from agent file)
   - `prompts/cloud_engineer/predefined_tasks.py` (moved from agent file)
   - `prompts/cloud_engineer/__init__.py` (simple exports)
   - `prompts/common/error_handling.py` (optional, only if needed)
   - `prompts/__init__.py` (simple exports)

3. **Documentation** (1 file):
   - `GETTING_STARTED.md` (comprehensive guide)

### Files to Update
1. `runtime/agent_runtime.py` - Import from `agents/cloud_engineer_agent.py`
2. `frontend/app.py` - Import from `agents/cloud_engineer_agent.py` (if needed)
3. `scripts/deploy_all.py` - Add execution sequence documentation

### Changes Summary (SIMPLIFIED)
- **No factory patterns** - Direct imports
- **No registry** - Simple file structure
- **No complex managers** - Simple functions
- **Just organization** - Move code to proper folders
- **Simple imports** - `from agents.cloud_engineer_agent import ...`

---

## 5. Benefits Summary

### Modular Agents Structure
- ✅ Easy to add new agents (just create new file, same pattern)
- ✅ Clear separation of concerns (each agent self-contained)
- ✅ Simple direct imports (no factory/registry complexity)
- ✅ Easy testing (test agents independently)
- ✅ Strands-friendly (works directly with Strands Agent pattern)

### Modular Prompts Structure
- ✅ Centralized prompt management (all prompts in one place)
- ✅ Easy to update prompts (edit files, no code changes)
- ✅ Version control prompts (track prompt changes)
- ✅ Simple imports (direct file imports)

### Comprehensive Guide
- ✅ Newbies can get started quickly (clear step-by-step)
- ✅ Understand flow (complete system flow explained)
- ✅ Script execution sequence (exact order with explanations)
- ✅ Troubleshooting guidance (for each step)
- ✅ Common workflows (first-time setup, adding agents, etc.)

---

## 6. Implementation Order (SIMPLIFIED)

1. **Create folder structure** (`agents/`, `prompts/cloud_engineer/`)
2. **Extract prompts** (system prompt and PREDEFINED_TASKS from agent file)
3. **Move agent file** (`cloud_engineer_agent.py` to `agents/`)
4. **Update agent imports** (import prompts from new locations)
5. **Update runtime imports** (import agent from `agents/` folder)
6. **Create GETTING_STARTED.md** (comprehensive guide with all sections)
7. **Test everything** (ensure all imports work, scripts execute correctly)

### Simple Migration Steps:
1. Create `prompts/cloud_engineer/system_prompt.py` - Extract system prompt
2. Create `prompts/cloud_engineer/predefined_tasks.py` - Extract PREDEFINED_TASKS
3. Move `cloud_engineer_agent.py` → `agents/cloud_engineer_agent.py`
4. Update agent file to import from prompts folder
5. Update `runtime/agent_runtime.py` to import from `agents/` folder
6. Test - Should work exactly as before, just better organized

---

## 7. Questions for Clarification

1. **Agent Selection**: Should runtime support multiple agents simultaneously, or one agent per runtime deployment?
   - **Recommendation**: One agent per runtime (simpler). If needed later, can add simple selection logic without factory pattern.

2. **Prompt Versioning**: Do we need prompt versioning system, or just file-based versioning?
   - **Recommendation**: File-based (Git versioning) - simple and effective.

3. **MCP Setup Sharing**: Do we need shared MCP setup utilities, or keep it in each agent?
   - **Recommendation**: Keep in agent file unless it's truly shared. Only create `agents/tools/mcp_setup.py` if needed.

4. **Prompt Updates**: Can prompts be updated without redeploying runtime (hot reload)?
   - **Recommendation**: No hot reload initially (requires runtime redeploy), but prompts are separate so easy to update.

5. **Guide Format**: Should GETTING_STARTED.md include ASCII diagrams or reference external images?
   - **Recommendation**: ASCII diagrams (works in text, no external dependencies).

6. **Common Prompts**: Do we need `prompts/common/` folder?
   - **Recommendation**: Only create if prompts are actually shared. Start simple.

---

## 8. Notes (SIMPLIFIED APPROACH)

- **Simple & Direct**: No factory patterns, no registries, no complex abstractions
- **Strands-Friendly**: Works directly with Strands Agent pattern (no wrapper needed)
- **Backward Compatibility**: All existing functionality preserved
- **Easy Migration**: Just move files and update imports
- **Minimal Changes**: Only organizational changes, no architectural changes
- **Guide Priority**: GETTING_STARTED.md should be very visual and step-by-step for newbies
- **Visual Elements**: Use ASCII diagrams, tables, and clear formatting

### Key Principles:
- ✅ **Keep it simple** - Direct imports, no abstractions
- ✅ **Strands-native** - Work with Strands patterns, not against them
- ✅ **Organize, don't complicate** - Just move files to better folders
- ✅ **Easy to understand** - Any developer can follow the structure

---

## 9. Additional Considerations for GETTING_STARTED.md

### Visual Elements
- **ASCII Diagrams**: System architecture, data flow, execution sequence
- **Tables**: Script comparison, file locations, environment variables
- **Code Blocks**: Commands, examples, configuration snippets
- **Checklists**: Pre-deployment checklist, verification steps

### Newbie-Friendly Features
- **"What is..." sections**: Explain concepts simply
- **"Why..." sections**: Explain reasons behind decisions
- **"How to..." sections**: Step-by-step instructions
- **"Troubleshooting" sections**: Common issues and solutions
- **Visual Indicators**: ✅ ❌ ⚠️ 💡 📋 🚀 🔍

### Organization
- **Start Simple**: Basic concepts first
- **Build Complexity**: Gradually introduce advanced topics
- **Cross-References**: Link to detailed sections in IMPLEMENTATION_PLAN.md
- **Examples**: Real-world examples throughout

---

## 10. Expected Outcomes

After implementing this plan:

1. **Modular Structure**: Easy to add new agents without modifying existing code
2. **Prompt Management**: Centralized, easy-to-update prompts
3. **Newbie-Friendly**: Comprehensive guide helps newbies get started quickly
4. **Clear Flow**: Understanding of how everything works together
5. **Execution Sequence**: Clear step-by-step script execution order
6. **Better Organization**: Code is more organized and maintainable

