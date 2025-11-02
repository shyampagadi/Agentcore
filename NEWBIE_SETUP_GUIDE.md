# Newbie Setup & Implementation Guide - Enterprise Cloud Engineer Agent

**Welcome!** This is your complete step-by-step guide to set up and deploy the Enterprise Cloud Engineer Agent from scratch. Follow this guide phase by phase, and verify each step using AWS Console before moving to the next.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pre-Setup Checklist](#pre-setup-checklist)
3. [Phase 1: Foundation Setup](#phase-1-foundation-setup)
4. [Phase 2: Runtime Deployment](#phase-2-runtime-deployment)
5. [Phase 3: Testing & Verification](#phase-3-testing--verification)
6. [Phase 4: Production Deployment](#phase-4-production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Overview

### What You'll Build

By the end of this guide, you'll have:
- ✅ **Multi-user Cloud Engineer Agent** - Handles 100+ concurrent users
- ✅ **Secure Authentication** - Cognito User Pool integration
- ✅ **Content Safety** - Bedrock Guardrails for compliance
- ✅ **Persistent Memory** - Conversation history and knowledge retention
- ✅ **Production-Ready UI** - Streamlit app deployed on AWS
- ✅ **Auto-Scaling** - AgentCore Runtime handles load automatically

### Time Investment

- **Phase 1**: 30-45 minutes (Foundation Setup)
- **Phase 2**: 15-20 minutes (Runtime Deployment)
- **Phase 3**: 10-15 minutes (Testing)
- **Phase 4**: 20-30 minutes (Production Deployment)
- **Total**: ~75-110 minutes

---

## Pre-Setup Checklist

Before starting, verify you have:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **AWS CLI 2.x** installed (`aws --version`)
- [ ] **AWS Account** with admin access
- [ ] **AWS Credentials** configured (`aws sts get-caller-identity` works)
- [ ] **Bedrock Model Access** enabled (Claude Sonnet 3.7)
- [ ] **Git** installed (`git --version`)
- [ ] **Code Editor** (VS Code recommended)

### Verify AWS Access

```bash
# Check AWS credentials
aws sts get-caller-identity
# Expected: Returns your AWS account ID, user ARN, etc.

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-2 | grep claude
# Expected: Shows Claude models (e.g., anthropic.claude-sonnet-3-7)

# Check region
aws configure get region
# Expected: us-east-2 (or set it)
```

**If any check fails:**
- AWS credentials: Run `aws configure`
- Bedrock access: Go to AWS Console → Bedrock → Model access → Enable Claude Sonnet 3.7
- Region: Run `aws configure set region us-east-2`

---

## Phase 1: Foundation Setup

**Goal**: Set up all AWS resources and infrastructure needed for the agent.

**What You'll Achieve**: 
- ✅ Cognito User Pool for authentication
- ✅ Bedrock Guardrails for content safety
- ✅ AgentCore Identity and Memory resources
- ✅ CloudWatch logs for monitoring
- ✅ ECR repository for container images

**Time**: 30-45 minutes

---

### Step 1: Validate Environment

**Command:**
```bash
python scripts/validate_environment.py
```

**What It Does:**
- Checks Python version
- Verifies AWS credentials
- Validates Bedrock model access
- Checks required dependencies
- Verifies .env file exists

**Expected Output:**
```
✅ Python version: 3.11.x
✅ AWS credentials configured
✅ Region us-east-2 accessible
✅ Bedrock access verified
✅ Cognito access verified
✅ All dependencies installed
✅ .env file found
```

**Verify in AWS Console:**
1. Go to: https://console.aws.amazon.com/
2. Check top-right corner: Your account name should be visible
3. Check region selector: Should show `us-east-2` (or your configured region)

**Achievement**: ✅ Environment validated and ready

**If Errors:**
- Missing dependencies: `pip install -r requirements.txt`
- AWS credentials: `aws configure`
- Bedrock access: Enable in AWS Console → Bedrock → Model access

---

### Step 2: Create Cognito User Pool

**Command:**
```bash
python scripts/create_cognito_pool.py --pool-name cloud-engineer-agent-pool --region us-east-2
```

**What It Does:**
- Creates Cognito User Pool
- Creates App Client for authentication
- Configures OAuth flows
- Sets up password policies
- Updates .env file with credentials

**Expected Output:**
```
🚀 Creating Cognito User Pool...
✅ User Pool created: us-east-2_abc123xyz
✅ App Client created: 1a2b3c4d5e6f7g8h9i0j
✅ Configuration saved to .env
```

**Verify in AWS Console:**
1. Go to: https://console.aws.amazon.com/cognito/
2. Click: **User pools** (left menu)
3. Find: `cloud-engineer-agent-pool`
4. Click on it
5. Verify:
   - **General settings** → Status: Active
   - **App integration** → App client name exists
   - Copy **User pool ID** (you'll need this!)

**Check .env File:**
```bash
cat .env | grep COGNITO
# Should show:
# COGNITO_USER_POOL_ID=us-east-2_abc123xyz
# COGNITO_CLIENT_ID=1a2b3c4d5e6f7g8h9i0j
```

**Achievement**: ✅ Authentication infrastructure ready

**If Errors:**
- Permission denied: Check IAM permissions for `cognito-idp:CreateUserPool`
- Pool already exists: Use `python scripts/verify_cognito.py --pool-id <your-pool-id>`

---

### Step 3: Setup Base AWS Resources

**Command:**
```bash
python scripts/setup_aws_resources.py --region us-east-2
```

**What It Does:**
- Creates CloudWatch log groups for logging
- Creates ECR repository for container images
- Sets up log retention policies

**Expected Output:**
```
🚀 Setting up AWS resources...
✅ Created log group: /aws/bedrock-agentcore/runtimes
✅ Created log group: /aws/bedrock-agentcore/memory
✅ Created ECR repository: cloud-engineer-agent-runtime
✅ Resources created successfully
```

**Verify in AWS Console:**

**CloudWatch Logs:**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click: **Log groups** (left menu)
3. Search for: `/aws/bedrock-agentcore/`
4. Verify these log groups exist:
   - `/aws/bedrock-agentcore/runtimes`
   - `/aws/bedrock-agentcore/memory`

**ECR Repository:**
1. Go to: https://console.aws.amazon.com/ecr/
2. Click: **Repositories** (left menu)
3. Find: `cloud-engineer-agent-runtime`
4. Verify:
   - Status: Active
   - Region: us-east-2

**Achievement**: ✅ Monitoring and container registry ready

**If Errors:**
- IAM permissions: Ensure you have permissions for `logs:CreateLogGroup` and `ecr:CreateRepository`
- Region mismatch: Ensure region is `us-east-2`

---

### Step 4: Setup Guardrails

**Command:**
```bash
python scripts/setup_guardrails.py
```

**What It Does:**
- Creates Bedrock Guardrail
- Configures content filters (profanity, hate speech, violence)
- Sets up topic blocking for cloud engineering
- Updates .env file with guardrail ID

**Expected Output:**
```
🚀 Setting up Bedrock Guardrails...
✅ Guardrail created: abc123def456ghi789jkl
✅ Guardrail version: 1
✅ Configuration saved to .env
```

**Verify in AWS Console:**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click: **Guardrails** (left menu)
3. Find: `cloud-engineer-agent-guardrail`
4. Click on it
5. Verify:
   - **Status**: Active
   - **Version**: 1 (or latest)
   - **Content filters**: Configured (profanity, hate speech, etc.)
   - Copy **Guardrail ID** (you'll need this!)

**Check .env File:**
```bash
cat .env | grep GUARDRAIL
# Should show:
# BEDROCK_GUARDRAIL_ID=abc123def456ghi789jkl
# BEDROCK_GUARDRAIL_VERSION=1
```

**Achievement**: ✅ Content safety and compliance configured

**If Errors:**
- Permission denied: Check IAM permissions for `bedrock:CreateGuardrail`
- Guardrail already exists: Delete old one or use different name

---

### Step 5: Setup AgentCore Resources

**Option A: Individual Scripts (Recommended for Learning)**

```bash
# Step 5a: Create Identity
python scripts/create_agentcore_identity.py

# Step 5b: Create Memory
python scripts/create_agentcore_memory.py --enable-ltm
```

**Option B: Combined Script (Faster)**

```bash
python scripts/setup_agentcore_resources.py --create-memory
```

**What It Does:**
- Creates Workload Identity for AgentCore Runtime
- Creates Memory resource with Short-Term Memory (STM) and Long-Term Memory (LTM)
- Configures memory strategies
- Updates .env file with resource ARNs

**Expected Output:**
```
🚀 Creating AgentCore resources...
✅ Workload Identity created: arn:aws:bedrock-agentcore:us-east-2:123456789012:workload-identity/abc123
✅ Memory resource created: arn:aws:bedrock-agentcore:us-east-2:123456789012:memory-resource/xyz789
✅ Memory ID: mem-abc123def456
✅ Status: ACTIVE
✅ Configuration saved to .env
```

**Verify in AWS Console:**

**Workload Identity:**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click: **AgentCore** → **Identity** (left menu)
3. Find: `cloud-engineer-agent-workload-identity`
4. Verify:
   - Status: Active
   - Copy **Identity ARN**

**Memory Resource:**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click: **AgentCore** → **Memory** (left menu)
3. Find: `cloud-engineer-agent-memory`
4. Verify:
   - Status: Active
   - Strategies: EventStrategy (STM), SemanticStrategy (LTM)
   - Copy **Memory ID** and **Memory ARN**

**Check .env File:**
```bash
cat .env | grep -E "WORKLOAD_IDENTITY|MEMORY"
# Should show:
# WORKLOAD_IDENTITY_NAME=cloud-engineer-agent-workload-identity
# WORKLOAD_IDENTITY_ARN=arn:aws:bedrock-agentcore:...
# MEMORY_RESOURCE_ID=mem-abc123def456
# MEMORY_RESOURCE_ARN=arn:aws:bedrock-agentcore:...
```

**Verify Using Script:**
```bash
python scripts/verify_agentcore_resources.py --all
# Should show all resources as verified ✅
```

**Achievement**: ✅ AgentCore Identity and Memory ready

**If Errors:**
- Memory creation fails: Ensure `bedrock-agentcore-starter-toolkit` is installed: `pip install bedrock-agentcore-starter-toolkit`
- Permission denied: Check IAM permissions for `bedrock-agentcore-control:CreateWorkloadIdentity` and `bedrock-agentcore-control:CreateMemoryResource`
- Resource already exists: Use different name or delete existing resource

---

### Phase 1 Achievement Summary

**✅ What You've Built:**
- Cognito User Pool for user authentication
- CloudWatch log groups for monitoring
- ECR repository for container images
- Bedrock Guardrail for content safety
- AgentCore Identity for runtime authentication
- AgentCore Memory for conversation persistence

**✅ Verify Everything:**
```bash
# List all resources
python scripts/list_agentcore_resources.py --resource-type all

# Verify all resources
python scripts/verify_agentcore_resources.py --all

# Expected: All resources show ✅ ACTIVE status
```

**✅ Next Phase**: Ready to deploy Agent Runtime!

---

## Phase 2: Runtime Deployment

**Goal**: Deploy your agent to AgentCore Runtime so it can handle requests.

**What You'll Achieve:**
- ✅ Agent wrapped with AgentCore SDK
- ✅ Runtime deployed and accessible
- ✅ Memory integration working
- ✅ Guardrails integrated
- ✅ Runtime endpoint URL

**Time**: 15-20 minutes

---

### Step 6: Configure Agent Runtime

**Command:**
```bash
agentcore configure -e runtime/agent_runtime.py --region us-east-2
```

**What It Does:**
- Configures AgentCore Runtime settings
- Sets up OAuth provider (Cognito)
- Configures Memory integration
- Sets execution role
- Creates configuration file

**Interactive Prompts:**
```
Entrypoint file: runtime/agent_runtime.py
Execution Role: [Press Enter to auto-create]
ECR Repository: cloud-engineer-agent-runtime
OAuth Configuration: yes
  Discovery URL: https://cognito-idp.us-east-2.amazonaws.com/<pool-id>/.well-known/openid-configuration
  Client ID: <your-client-id>
Memory Configuration: yes
  Enable Long-Term Memory: yes
Network Mode: Public
```

**Expected Output:**
```
✅ Configuration saved to .bedrock_agentcore.yaml
✅ OAuth provider configured
✅ Memory integration configured
✅ Ready to deploy!
```

**Verify Configuration:**
```bash
cat .bedrock_agentcore.yaml
# Should show configuration with:
# - entrypoint: runtime/agent_runtime.py
# - oauth: configured
# - memory: configured
```

**Achievement**: ✅ Runtime configuration ready

**If Errors:**
- `agentcore` command not found: Install `pip install bedrock-agentcore-starter-toolkit`
- OAuth URL invalid: Check Cognito User Pool ID in .env
- Memory not found: Verify Memory resource exists: `python scripts/verify_agentcore_resources.py --check-memory`

---

### Step 7: Deploy Agent Runtime

**Command:**
```bash
agentcore launch
```

**What It Does:**
- Builds container image (via AWS CodeBuild)
- Pushes image to ECR repository
- Creates Memory resource (if not created earlier)
- Deploys Runtime
- Configures Identity integration
- Sets up CloudWatch logging

**Expected Output:**
```
🚀 Building container image...
⏳ Building via CodeBuild... (this may take 5-10 minutes)
✅ Image built and pushed to ECR
✅ Memory resource ready
✅ Deploying Runtime...
✅ Runtime deployed successfully!
Runtime ARN: arn:aws:bedrock-agentcore:us-east-2:123456789012:runtime/abc123
Runtime Endpoint: https://abc123.execute-api.us-east-2.amazonaws.com/invocations
✅ Configuration saved to .env
```

**Verify in AWS Console:**

**AgentCore Runtime:**
1. Go to: https://console.aws.amazon.com/bedrock/
2. Click: **AgentCore** → **Runtimes** (left menu)
3. Find: Your runtime (usually named after your project)
4. Verify:
   - **Status**: Active
   - **Endpoint**: Copy the endpoint URL
   - **Memory**: Shows Memory resource attached
   - **Identity**: Shows Identity attached

**ECR Repository:**
1. Go to: https://console.aws.amazon.com/ecr/
2. Click: `cloud-engineer-agent-runtime`
3. Click: **Images** tab
4. Verify:
   - Latest image exists
   - Image pushed within last 10 minutes

**CloudWatch Logs:**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click: **Log groups** → `/aws/bedrock-agentcore/runtimes`
3. Verify:
   - Recent log streams exist
   - Logs show runtime initialization

**Check .env File:**
```bash
cat .env | grep RUNTIME
# Should show:
# AGENT_RUNTIME_ARN=arn:aws:bedrock-agentcore:...
# AGENT_RUNTIME_ENDPOINT=https://...
```

**Verify Using Script:**
```bash
python scripts/get_resource_status.py --resource-type runtime --resource-id <runtime-id>
# Should show status: ACTIVE
```

**Achievement**: ✅ Agent Runtime deployed and accessible!

**If Errors:**
- Build fails: Check CodeBuild logs in AWS Console → CodeBuild → Build projects
- Deployment timeout: Runtime deployment can take 10-15 minutes, be patient
- Memory creation fails: Memory may have been created automatically, verify with `python scripts/list_agentcore_resources.py --resource-type memory`

---

### Phase 2 Achievement Summary

**✅ What You've Built:**
- Agent Runtime deployed and running
- Container image in ECR
- Memory integration active
- Guardrails integrated
- Runtime endpoint accessible

**✅ Verify Everything:**
```bash
# Test runtime endpoint
curl -X POST https://<runtime-endpoint>/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, test"}'

# Expected: Response from agent (may require authentication)
```

**✅ Next Phase**: Ready to test everything!

---

## Phase 3: Testing & Verification

**Goal**: Verify all components work correctly before production deployment.

**What You'll Achieve:**
- ✅ All resources verified
- ✅ Runtime tested
- ✅ Scalability tested
- ✅ Local UI working

**Time**: 10-15 minutes

---

### Step 8: Test Deployment

**Command:**
```bash
python scripts/test_deployment.py
```

**What It Does:**
- Validates AWS credentials
- Verifies Cognito User Pool
- Checks Guardrail configuration
- Tests Runtime endpoint access
- Validates Memory integration

**Expected Output:**
```
🧪 Testing deployment...
✅ AWS credentials valid
✅ Cognito User Pool accessible
✅ Guardrail configured
✅ Runtime endpoint accessible
✅ Memory resource accessible
✅ All tests passed!
```

**Verify in AWS Console:**

**CloudWatch Metrics:**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click: **Metrics** → **All metrics**
3. Search for: `BedrockAgentCore`
4. Verify:
   - Runtime metrics available
   - Request counts visible

**Achievement**: ✅ All components verified and working

**If Errors:**
- Runtime not accessible: Check Runtime status in AWS Console
- Memory errors: Verify Memory resource exists: `python scripts/verify_agentcore_resources.py --check-memory`

---

### Step 9: Test Scalability (Optional)

**Command:**
```bash
python scripts/test_scalability.py --concurrent-users 10
```

**What It Does:**
- Sends concurrent requests to Runtime
- Measures response times
- Tracks success rates
- Reports metrics

**Expected Output:**
```
🧪 Testing scalability...
Sending 10 concurrent requests...
✅ All requests completed
Average response time: 2.3s
Success rate: 100%
✅ Scalability test passed!
```

**Verify in AWS Console:**

**CloudWatch Metrics:**
1. Go to: https://console.aws.amazon.com/cloudwatch/
2. Click: **Metrics** → **BedrockAgentCore**
3. View:
   - **RequestCount**: Should show 10 requests
   - **ResponseTime**: Should show average response time
   - **ErrorRate**: Should be 0%

**Achievement**: ✅ Scalability verified

**If Errors:**
- Timeout errors: Increase concurrent users gradually
- Rate limiting: Check Runtime quotas in AWS Console

---

### Step 10: Run Streamlit UI Locally

**Command:**
```bash
streamlit run frontend/app.py
```

**What It Does:**
- Starts Streamlit development server
- Opens browser automatically
- Connects to Runtime endpoint
- Provides UI for testing

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

**Verify in Browser:**
1. Open: http://localhost:8501
2. Verify:
   - Login page appears
   - Can authenticate with Cognito
   - Chat interface loads
   - Can send messages to agent

**Achievement**: ✅ Local UI working

**If Errors:**
- Port 8501 in use: Change port: `streamlit run frontend/app.py --server.port 8502`
- Authentication fails: Check Cognito configuration in .env
- Runtime errors: Verify Runtime endpoint in .env

---

### Phase 3 Achievement Summary

**✅ What You've Verified:**
- All resources accessible
- Runtime responding correctly
- Scalability confirmed
- Local UI functional

**✅ Next Phase**: Ready for production deployment!

---

## Phase 4: Production Deployment

**Goal**: Deploy Streamlit UI to production with auto-scaling and HTTPS.

**What You'll Achieve:**
- ✅ ECS Fargate cluster
- ✅ Application Load Balancer
- ✅ HTTPS with SSL certificate
- ✅ Auto-scaling configured
- ✅ Production URL

**Time**: 20-30 minutes

---

### Step 11: Deploy Streamlit UI to Production

**Command:**
```bash
python scripts/deploy_streamlit_production.py \
  --cluster-name cloud-engineer-agent-cluster \
  --service-name cloud-engineer-agent-service \
  --desired-count 2 \
  --region us-east-2
```

**What It Does:**
- Creates ECS Fargate cluster
- Creates task definition for Streamlit
- Creates ECS service
- Creates Application Load Balancer
- Configures target groups
- Sets up security groups
- Configures auto-scaling

**Expected Output:**
```
🚀 Deploying Streamlit UI to production...
✅ ECS cluster created
✅ Task definition created
✅ ECS service created
✅ Application Load Balancer created
✅ Service is running!
ALB DNS: cloud-engineer-agent-alb-1234567890.us-east-2.elb.amazonaws.com
✅ Configuration saved to .env
```

**Verify in AWS Console:**

**ECS Cluster:**
1. Go to: https://console.aws.amazon.com/ecs/
2. Click: **Clusters** → `cloud-engineer-agent-cluster`
3. Verify:
   - Status: Active
   - Running tasks: 2 (or your desired count)

**ECS Service:**
1. Click: **Services** tab → `cloud-engineer-agent-service`
2. Verify:
   - Status: Running
   - Desired count: 2
   - Running count: 2
   - Health: Healthy

**Application Load Balancer:**
1. Go to: https://console.aws.amazon.com/ec2/
2. Click: **Load Balancers** (left menu)
3. Find: `cloud-engineer-agent-alb`
4. Verify:
   - State: Active
   - DNS name: Copy this URL
   - Listeners: HTTP (port 80) configured

**Check .env File:**
```bash
cat .env | grep -E "ALB|ECS|PRODUCTION"
# Should show:
# ALB_DNS_NAME=cloud-engineer-agent-alb-1234567890.us-east-2.elb.amazonaws.com
# ECS_CLUSTER_NAME=cloud-engineer-agent-cluster
# ECS_SERVICE_NAME=cloud-engineer-agent-service
```

**Test Production URL:**
```bash
curl http://<alb-dns-name>
# Expected: HTML response from Streamlit app
```

**Achievement**: ✅ Production UI deployed!

**If Errors:**
- ECS service not starting: Check CloudWatch logs for task errors
- ALB health checks failing: Verify security groups allow traffic
- Port conflicts: Ensure port 8501 is available in task definition

---

### Step 12: Setup Domain Name (Optional)

**Command:**
```bash
python scripts/setup_domain.py \
  --domain-name yourdomain.com \
  --subdomain agent \
  --alb-arn <your-alb-arn> \
  --region us-east-2
```

**What It Does:**
- Creates Route 53 hosted zone (if needed)
- Requests SSL certificate from ACM
- Validates certificate (DNS or email)
- Configures HTTPS listener on ALB
- Creates Route 53 A record
- Updates Cognito callback URLs

**Expected Output:**
```
🚀 Setting up domain name...
✅ Route 53 hosted zone configured
✅ SSL certificate requested
⏳ Validating certificate... (may take 5-10 minutes)
✅ Certificate validated
✅ HTTPS listener configured
✅ Route 53 record created
✅ Production URL: https://agent.yourdomain.com
✅ Cognito callback URLs updated
```

**Verify in AWS Console:**

**Route 53:**
1. Go to: https://console.aws.amazon.com/route53/
2. Click: **Hosted zones** → `yourdomain.com`
3. Verify:
   - A record for `agent.yourdomain.com` exists
   - Points to ALB DNS

**Certificate Manager:**
1. Go to: https://console.aws.amazon.com/acm/
2. Find: Certificate for `*.yourdomain.com` or `agent.yourdomain.com`
3. Verify:
   - Status: Issued
   - Validation: Valid

**Application Load Balancer:**
1. Go to: https://console.aws.amazon.com/ec2/
2. Click: **Load Balancers** → Your ALB
3. Click: **Listeners** tab
4. Verify:
   - HTTPS (port 443) listener exists
   - SSL certificate attached

**Test HTTPS URL:**
```bash
curl https://agent.yourdomain.com
# Expected: HTML response (should work with HTTPS)
```

**Achievement**: ✅ Production URL with HTTPS configured!

**If Errors:**
- Certificate validation fails: Check DNS records in Route 53
- HTTPS not working: Verify certificate is attached to ALB listener
- Domain not resolving: Wait 5-10 minutes for DNS propagation

---

### Phase 4 Achievement Summary

**✅ What You've Built:**
- Production Streamlit UI deployed on ECS Fargate
- Application Load Balancer for high availability
- HTTPS with SSL certificate
- Auto-scaling configured
- Production URL accessible

**✅ Final Verification:**
```bash
# List all resources
python scripts/list_agentcore_resources.py --resource-type all

# Verify all resources
python scripts/verify_agentcore_resources.py --all

# Test production URL
curl https://agent.yourdomain.com
```

**✅ You're Done!** 🎉

---

## Troubleshooting

### Common Issues

**Issue: Script fails with "Permission denied"**
- **Solution**: Check IAM permissions. Ensure your user/role has permissions for:
  - Cognito: `cognito-idp:*`
  - Bedrock: `bedrock:*`, `bedrock-agentcore-control:*`
  - ECS: `ecs:*`
  - ECR: `ecr:*`
  - CloudWatch: `logs:*`
  - Route 53: `route53:*`
  - ACM: `acm:*`

**Issue: Runtime deployment fails**
- **Solution**: 
  1. Check CodeBuild logs: AWS Console → CodeBuild → Build projects
  2. Verify Dockerfile exists: `ls runtime/Dockerfile`
  3. Check .env has all required variables
  4. Verify Memory resource exists: `python scripts/verify_agentcore_resources.py --check-memory`

**Issue: ECS service not starting**
- **Solution**:
  1. Check CloudWatch logs: AWS Console → CloudWatch → Log groups → `/ecs/cloud-engineer-agent-service`
  2. Verify task definition: Check environment variables
  3. Check security groups: Ensure ALB can reach ECS tasks
  4. Verify ALB health checks: Check target group health

**Issue: Authentication fails in UI**
- **Solution**:
  1. Verify Cognito User Pool ID in .env
  2. Check Cognito callback URLs include your domain
  3. Verify App Client exists in Cognito
  4. Check browser console for errors

**Issue: Memory not working**
- **Solution**:
  1. Verify Memory resource exists: `python scripts/list_agentcore_resources.py --resource-type memory`
  2. Check Memory status: `python scripts/get_resource_status.py --resource-type memory --resource-id <id>`
  3. Verify Runtime has Memory attached: Check Runtime configuration in AWS Console

### Getting Help

- **Check Logs**: Always check CloudWatch logs first
- **Verify Resources**: Use `python scripts/verify_agentcore_resources.py --all`
- **List Resources**: Use `python scripts/list_agentcore_resources.py --resource-type all`
- **Check Status**: Use `python scripts/get_resource_status.py` for detailed resource status

---

## Success Checklist

After completing all phases, you should have:

- [ ] Cognito User Pool created and configured
- [ ] CloudWatch log groups created
- [ ] ECR repository created with container image
- [ ] Bedrock Guardrail created and configured
- [ ] AgentCore Identity created
- [ ] AgentCore Memory created
- [ ] AgentCore Runtime deployed and active
- [ ] ECS cluster running with Streamlit UI
- [ ] Application Load Balancer configured
- [ ] Domain name configured (optional)
- [ ] HTTPS working (if domain configured)
- [ ] All resources verified via scripts

**Congratulations!** 🎉 You've successfully deployed an enterprise-grade Cloud Engineer Agent!

---

## Next Steps

1. **Create Test Users**: Add users to Cognito User Pool
2. **Monitor**: Set up CloudWatch dashboards
3. **Scale**: Configure auto-scaling policies
4. **Customize**: Update agent prompts and behavior
5. **Extend**: Add more agents or features

For detailed information, see:
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Project overview and flow
- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) - Detailed architecture and implementation
- [MODULAR_STRUCTURE_PLAN.md](./MODULAR_STRUCTURE_PLAN.md) - Code structure and organization

