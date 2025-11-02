"""
===============================================================================
SCRIPT NAME: destroy_all.py
===============================================================================

PURPOSE:
    Destroys ALL resources created during setup (complete teardown).

USAGE:
    python scripts/destroy_all.py [--dry-run] [--force] [--skip-cognito] [--skip-ecs]

OPTIONS:
    --dry-run: Show what would be deleted without actually deleting
    --force: Skip confirmation prompts
    --skip-cognito: Skip Cognito User Pool deletion (keep for reuse)
    --skip-ecs: Skip ECS/ALB deletion (keep production infrastructure)
    --region REGION: AWS region (default: from env or us-east-2)

WHAT THIS SCRIPT DOES:
    1. Lists ALL resources to be deleted (from .env + discovered orphaned resources)
    2. Prompts for confirmation (unless --force)
    3. Deletes resources in safe dependency order:
       a. ECS Services and Tasks
       b. ECS Task Definitions (deregister)
       c. ECS Clusters
       d. ALB Listeners
       e. ALB Target Groups (deregister targets first)
       f. Application Load Balancers
       g. Security Groups (with retry logic)
       h. Route 53 Records
       i. ACM Certificates
       j. AgentCore Runtime
       k. AgentCore Memory
       l. AgentCore Identity
       m. CloudWatch Log Groups
       n. ECR Repositories (with images)
       o. Bedrock Guardrails
       p. Cognito App Clients
       q. Cognito User Pools (optional)
       r. IAM Roles (detach policies first)
    4. Discovers orphaned resources by name pattern
    5. Updates .env file to remove deleted resource IDs
    6. Provides comprehensive summary with verification steps

OUTPUTS:
    - Complete list of resources to be deleted
    - Confirmation prompt (unless --force)
    - Detailed deletion progress
    - Updated .env file
    - Final summary

TROUBLESHOOTING:
    - Always use --dry-run first to preview deletions
    - Check dependencies before deleting
    - Some resources may take time to delete (wait for completion)
    - Manual cleanup may be required for some resources

RELATED FILES:
    - scripts/cleanup_resources.py - Cleanup AgentCore resources only
    - scripts/list_agentcore_resources.py - List resources before deletion

WARNING:
    This script PERMANENTLY DELETES ALL RESOURCES. Use with extreme caution!
    This is IRREVERSIBLE. Make sure you have backups if needed.

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv, set_key

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_config import setup_logger
from utils.aws_helpers import validate_aws_credentials, get_aws_region
import boto3
from botocore.exceptions import ClientError

logger = setup_logger(__name__)


def delete_ecs_service(ecs_client, cluster_name: str, service_name: str) -> bool:
    """Delete ECS service."""
    try:
        logger.info(f"   Stopping ECS service: {service_name}...")
        # Update service to 0 desired count first
        ecs_client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=0
        )
        
        # Wait for tasks to stop
        logger.info("   Waiting for tasks to stop...")
        waiter = ecs_client.get_waiter('services_stable')
        waiter.wait(cluster=cluster_name, services=[service_name])
        
        # Delete service
        ecs_client.delete_service(cluster=cluster_name, service=service_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ServiceNotFoundException':
            logger.info(f"   Service {service_name} not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete ECS service: {error_code}")
        return False


def delete_ecs_task_definitions(ecs_client, cluster_name: str) -> List[str]:
    """Delete ECS task definitions for this project. Returns list of deleted task definition ARNs."""
    deleted_tds = []
    try:
        # List all task definitions
        response = ecs_client.list_task_definitions(status='ACTIVE')
        for td_arn in response.get('taskDefinitionArns', []):
            # Check if task definition is for this project
            if 'cloud-engineer-agent' in td_arn.lower():
                try:
                    # Deregister task definition (cannot delete, only deregister)
                    ecs_client.deregister_task_definition(taskDefinition=td_arn)
                    deleted_tds.append(td_arn)
                    logger.info(f"   ✅ Deregistered task definition: {td_arn.split('/')[-1]}")
                except ClientError as e:
                    logger.warning(f"   ⚠️  Could not deregister task definition: {e}")
    except ClientError as e:
        logger.warning(f"   ⚠️  Could not list task definitions: {e}")
    return deleted_tds


def delete_ecs_cluster(ecs_client, cluster_name: str) -> bool:
    """Delete ECS cluster (deregisters task definitions first)."""
    try:
        # Deregister task definitions
        logger.info("   Deregistering ECS task definitions...")
        delete_ecs_task_definitions(ecs_client, cluster_name)
        time.sleep(2)
        
        # Now delete the cluster
        ecs_client.delete_cluster(cluster=cluster_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ClusterNotFoundException':
            logger.info(f"   Cluster {cluster_name} not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete ECS cluster: {error_code}")
        return False


def delete_alb_listeners(elb_client, alb_arn: str) -> List[str]:
    """Delete all listeners for an ALB. Returns list of deleted listener ARNs."""
    deleted_listeners = []
    try:
        # List all listeners for this ALB
        response = elb_client.describe_listeners(LoadBalancerArn=alb_arn)
        for listener in response.get('Listeners', []):
            listener_arn = listener['ListenerArn']
            try:
                elb_client.delete_listener(ListenerArn=listener_arn)
                deleted_listeners.append(listener_arn)
                logger.info(f"   ✅ Deleted listener: {listener_arn}")
            except ClientError as e:
                logger.warning(f"   ⚠️  Could not delete listener {listener_arn}: {e}")
    except ClientError as e:
        logger.warning(f"   ⚠️  Could not list listeners: {e}")
    return deleted_listeners


def delete_alb_target_groups(elb_client, alb_arn: Optional[str] = None) -> List[str]:
    """Delete all target groups for this project. Returns list of deleted target group ARNs."""
    deleted_tgs = []
    try:
        # List all target groups
        response = elb_client.describe_target_groups()
        for tg in response.get('TargetGroups', []):
            tg_arn = tg['TargetGroupArn']
            tg_name = tg.get('TargetGroupName', '')
            
            # Check if this target group matches our project or is associated with our ALB
            is_project_tg = 'cloud-engineer-agent' in tg_name.lower()
            is_alb_tg = False
            
            if alb_arn:
                # Check if target group is associated with this ALB
                try:
                    listeners = elb_client.describe_listeners(LoadBalancerArn=alb_arn)
                    for listener in listeners.get('Listeners', []):
                        for rule in listener.get('DefaultActions', []):
                            if rule.get('TargetGroupArn') == tg_arn:
                                is_alb_tg = True
                                break
                except ClientError:
                    pass
            
            if is_project_tg or is_alb_tg:
                try:
                    # First deregister targets
                    try:
                        targets = elb_client.describe_target_health(TargetGroupArn=tg_arn)
                        if targets.get('TargetHealthDescriptions'):
                            target_ids = [t['Target']['Id'] for t in targets['TargetHealthDescriptions']]
                            if target_ids:
                                elb_client.deregister_targets(
                                    TargetGroupArn=tg_arn,
                                    Targets=[{'Id': tid} for tid in target_ids]
                                )
                                logger.info(f"   ✅ Deregistered targets from {tg_name}")
                    except ClientError:
                        pass  # No targets or already deregistered
                    
                    elb_client.delete_target_group(TargetGroupArn=tg_arn)
                    deleted_tgs.append(tg_arn)
                    logger.info(f"   ✅ Deleted target group: {tg_name}")
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code == 'ResourceInUse':
                        logger.warning(f"   ⚠️  Target group {tg_name} still in use (will retry)")
                    else:
                        logger.warning(f"   ⚠️  Could not delete target group {tg_name}: {error_code}")
    except ClientError as e:
        logger.warning(f"   ⚠️  Could not list target groups: {e}")
    return deleted_tgs


def delete_target_group_standalone(elb_client, tg_arn: str) -> bool:
    """Delete a target group standalone (not associated with ALB)."""
    try:
        # Deregister targets first
        try:
            targets = elb_client.describe_target_health(TargetGroupArn=tg_arn)
            if targets.get('TargetHealthDescriptions'):
                target_ids = [t['Target']['Id'] for t in targets['TargetHealthDescriptions']]
                if target_ids:
                    elb_client.deregister_targets(
                        TargetGroupArn=tg_arn,
                        Targets=[{'Id': tid} for tid in target_ids]
                    )
        except ClientError:
            pass  # No targets or already deregistered
        
        elb_client.delete_target_group(TargetGroupArn=tg_arn)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Target group not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete target group: {error_code}")
        return False


def delete_application_load_balancer(elb_client, alb_arn: str) -> bool:
    """Delete Application Load Balancer (deletes listeners and target groups first)."""
    try:
        # Delete listeners first
        logger.info("   Deleting ALB listeners...")
        delete_alb_listeners(elb_client, alb_arn)
        
        # Wait a bit for listeners to be fully deleted
        time.sleep(3)
        
        # Delete target groups (both associated with ALB and project-named)
        logger.info("   Deleting ALB target groups...")
        delete_alb_target_groups(elb_client, alb_arn)
        
        # Also delete any orphaned target groups
        logger.info("   Deleting orphaned target groups...")
        delete_alb_target_groups(elb_client, None)  # Discover all project target groups
        
        # Wait a bit for target groups to be deregistered
        time.sleep(3)
        
        # Now delete the ALB
        elb_client.delete_load_balancer(LoadBalancerArn=alb_arn)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'LoadBalancerNotFound':
            logger.info(f"   ALB not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete ALB: {error_code}")
        return False


def delete_route53_record(route53_client, hosted_zone_id: str, record_name: str) -> bool:
    """Delete Route 53 record."""
    try:
        # Get current record
        response = route53_client.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        for record_set in response['ResourceRecordSets']:
            if record_set['Name'] == record_name or record_set['Name'] == record_name + '.':
                change_batch = {
                    'Changes': [{
                        'Action': 'DELETE',
                        'ResourceRecordSet': record_set
                    }]
                }
                route53_client.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id,
                    ChangeBatch=change_batch
                )
                return True
        logger.info(f"   Record {record_name} not found (already deleted)")
        return True
    except ClientError as e:
        logger.error(f"   ❌ Failed to delete Route 53 record: {e}")
        return False


def delete_acm_certificate(acm_client, certificate_arn: str) -> bool:
    """Delete ACM certificate."""
    try:
        acm_client.delete_certificate(CertificateArn=certificate_arn)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Certificate not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete certificate: {error_code}")
        return False


def delete_runtime_resource(runtime_id: str, region: str) -> bool:
    """Delete AgentCore Runtime."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_runtime(runtimeIdentifier=runtime_id)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Runtime not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete Runtime: {e}")
        return False


def delete_memory_resource(memory_id: str, region: str) -> bool:
    """Delete AgentCore Memory."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_memory_resource(memoryIdentifier=memory_id)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Memory not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete Memory: {e}")
        return False


def delete_identity_resource(identity_name: str, region: str) -> bool:
    """Delete AgentCore Identity."""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name=region)
        client.delete_workload_identity(workloadIdentityName=identity_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Identity not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete Identity: {e}")
        return False


def delete_guardrail_resource(guardrail_id: str, region: str) -> bool:
    """Delete Bedrock Guardrail."""
    try:
        client = boto3.client('bedrock', region_name=region)
        client.delete_guardrail(guardrailIdentifier=guardrail_id)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Guardrail not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete Guardrail: {e}")
        return False


def delete_cloudwatch_log_group(logs_client, log_group_name: str) -> bool:
    """Delete CloudWatch log group."""
    try:
        logs_client.delete_log_group(logGroupName=log_group_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   Log group {log_group_name} not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete log group: {error_code}")
        return False


def delete_ecr_repository(ecr_client, repo_name: str) -> bool:
    """Delete ECR repository."""
    try:
        # Delete all images first
        try:
            images = ecr_client.list_images(repositoryName=repo_name)
            if images.get('imageIds'):
                ecr_client.batch_delete_image(
                    repositoryName=repo_name,
                    imageIds=images['imageIds']
                )
                logger.info(f"   Deleted {len(images['imageIds'])} images from repository")
        except ClientError:
            pass  # No images or already empty
        
        ecr_client.delete_repository(repositoryName=repo_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'RepositoryNotFoundException':
            logger.info(f"   Repository {repo_name} not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete ECR repository: {error_code}")
        return False


def delete_cognito_app_clients(cognito_client, pool_id: str) -> List[str]:
    """Delete all app clients for a Cognito User Pool. Returns list of deleted client IDs."""
    deleted_clients = []
    try:
        response = cognito_client.list_user_pool_clients(UserPoolId=pool_id)
        for client in response.get('UserPoolClients', []):
            client_id = client['ClientId']
            try:
                cognito_client.delete_user_pool_client(
                    UserPoolId=pool_id,
                    ClientId=client_id
                )
                deleted_clients.append(client_id)
                logger.info(f"   ✅ Deleted app client: {client_id}")
            except ClientError as e:
                logger.warning(f"   ⚠️  Could not delete app client {client_id}: {e}")
    except ClientError as e:
        logger.warning(f"   ⚠️  Could not list app clients: {e}")
    return deleted_clients


def delete_cognito_user_pool(cognito_client, pool_id: str) -> bool:
    """Delete Cognito User Pool (deletes app clients first)."""
    try:
        # Delete app clients first
        logger.info("   Deleting Cognito app clients...")
        delete_cognito_app_clients(cognito_client, pool_id)
        time.sleep(2)
        
        # Now delete the User Pool
        cognito_client.delete_user_pool(UserPoolId=pool_id)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.info(f"   User Pool not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete Cognito User Pool: {error_code}")
        return False


def discover_orphaned_resources(region: str, skip_cognito: bool, skip_ecs: bool) -> List[Tuple[str, str, str, dict]]:
    """Discover orphaned resources that might not be in .env file."""
    resources = []
    project_prefix = 'cloud-engineer-agent'
    
    try:
        # Discover log groups by prefix
        logs_client = boto3.client('logs', region_name=region)
        try:
            paginator = logs_client.get_paginator('describe_log_groups')
            for page in paginator.paginate():
                for log_group in page.get('logGroups', []):
                    log_group_name = log_group['logGroupName']
                    if ('bedrock-agentcore' in log_group_name or 
                        'cloud-engineer-agent' in log_group_name or
                        '/ecs/' in log_group_name and project_prefix in log_group_name):
                        resources.append(('log_group', log_group_name, f'CloudWatch Log Group: {log_group_name}', {}))
        except ClientError:
            pass
        
        # Discover ECR repositories by name pattern
        ecr_client = boto3.client('ecr', region_name=region)
        try:
            response = ecr_client.describe_repositories()
            for repo in response.get('repositories', []):
                repo_name = repo['repositoryName']
                if project_prefix in repo_name.lower():
                    resources.append(('ecr', repo_name, f'ECR Repository: {repo_name}', {}))
        except ClientError:
            pass
        
        # Discover ECS clusters by name pattern
        if not skip_ecs:
            ecs_client = boto3.client('ecs', region_name=region)
            try:
                response = ecs_client.list_clusters()
                for cluster_arn in response.get('clusterArns', []):
                    cluster_name = cluster_arn.split('/')[-1]
                    if project_prefix in cluster_name.lower():
                        resources.append(('ecs_cluster', cluster_name, f'ECS Cluster: {cluster_name}', {}))
            except ClientError:
                pass
            
            # Discover ALBs by name pattern
            elb_client = boto3.client('elbv2', region_name=region)
            try:
                response = elb_client.describe_load_balancers()
                for alb in response.get('LoadBalancers', []):
                    alb_name = alb['LoadBalancerName']
                    if project_prefix in alb_name.lower():
                        resources.append(('alb', alb['LoadBalancerArn'], f'ALB: {alb_name}', {}))
                
                # Discover orphaned target groups
                tg_response = elb_client.describe_target_groups()
                for tg in tg_response.get('TargetGroups', []):
                    tg_name = tg.get('TargetGroupName', '')
                    if project_prefix in tg_name.lower():
                        resources.append(('target_group', tg['TargetGroupArn'], f'Target Group: {tg_name}', {}))
            except ClientError:
                pass
        
        # Discover Cognito User Pools by name pattern
        if not skip_cognito:
            cognito_client = boto3.client('cognito-idp', region_name=region)
            try:
                response = cognito_client.list_user_pools(MaxResults=60)
                for pool in response.get('UserPools', []):
                    pool_name = pool['Name']
                    if project_prefix in pool_name.lower():
                        resources.append(('cognito', pool['Id'], f'Cognito User Pool: {pool_name}', {}))
            except ClientError:
                pass
        
        # Discover AgentCore resources by name pattern
        agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
        try:
            # Memory resources
            try:
                mem_response = agentcore_client.list_memory_resources()
                for mem in mem_response.get('memoryResources', []):
                    mem_name = mem.get('name', '')
                    if project_prefix in mem_name.lower():
                        resources.append(('memory', mem['memoryResourceId'], f'AgentCore Memory: {mem_name}', {}))
            except ClientError:
                pass
            
            # Identity resources
            try:
                ident_response = agentcore_client.list_workload_identities()
                for ident in ident_response.get('workloadIdentities', []):
                    ident_name = ident.get('name', '')
                    if project_prefix in ident_name.lower():
                        resources.append(('identity', ident['workloadIdentityId'], f'AgentCore Identity: {ident_name}', {}))
            except ClientError:
                pass
            
            # Runtime resources
            try:
                rt_response = agentcore_client.list_runtimes()
                for rt in rt_response.get('runtimes', []):
                    rt_name = rt.get('name', '')
                    if project_prefix in rt_name.lower() or 'cloud-engineer-agent' in rt_name.lower():
                        resources.append(('runtime', rt['runtimeId'], f'AgentCore Runtime: {rt_name}', {}))
            except ClientError:
                pass
        except ClientError:
            pass
        
        # Discover IAM roles by name pattern
        iam_client = boto3.client('iam')
        try:
            paginator = iam_client.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page.get('Roles', []):
                    role_name = role['RoleName']
                    if project_prefix in role_name.lower():
                        resources.append(('iam_role', role_name, f'IAM Role: {role_name}', {}))
        except ClientError:
            pass
        
        # Discover Bedrock Guardrails by name pattern
        bedrock_client = boto3.client('bedrock', region_name=region)
        try:
            response = bedrock_client.list_guardrails()
            for guardrail in response.get('guardrails', []):
                guardrail_name = guardrail.get('name', '')
                if project_prefix in guardrail_name.lower():
                    resources.append(('guardrail', guardrail['guardrailId'], f'Bedrock Guardrail: {guardrail_name}', {}))
        except ClientError:
            pass
        
        # Discover security groups by name/tag pattern (for ECS/ALB)
        if not skip_ecs:
            ec2_client = boto3.client('ec2', region_name=region)
            try:
                response = ec2_client.describe_security_groups()
                for sg in response.get('SecurityGroups', []):
                    sg_name = sg.get('GroupName', '')
                    sg_description = sg.get('Description', '')
                    # Check if security group is for our project
                    if (project_prefix in sg_name.lower() or 
                        project_prefix in sg_description.lower() or
                        'cloud-engineer-agent' in sg_name.lower()):
                        # Only delete if not default
                        if sg_name != 'default':
                            resources.append(('security_group', sg['GroupId'], f'Security Group: {sg_name}', {}))
            except ClientError:
                pass
        
    except Exception as e:
        logger.warning(f"   ⚠️  Error discovering orphaned resources: {e}")
    
    return resources


def delete_iam_role(iam_client, role_name: str) -> bool:
    """Delete IAM role (detaches policies first)."""
    try:
        # List and detach all policies
        try:
            # List attached policies
            paginator = iam_client.get_paginator('list_attached_role_policies')
            for page in paginator.paginate(RoleName=role_name):
                for policy in page.get('AttachedPolicies', []):
                    iam_client.detach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy['PolicyArn']
                    )
                    logger.info(f"   ✅ Detached policy: {policy['PolicyArn']}")
            
            # List inline policies
            inline_policies = iam_client.list_role_policies(RoleName=role_name)
            for policy_name in inline_policies.get('PolicyNames', []):
                iam_client.delete_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name
                )
                logger.info(f"   ✅ Deleted inline policy: {policy_name}")
            
            # List instance profiles
            instance_profiles = iam_client.list_instance_profiles_for_role(RoleName=role_name)
            for profile in instance_profiles.get('InstanceProfiles', []):
                iam_client.remove_role_from_instance_profile(
                    InstanceProfileName=profile['InstanceProfileName'],
                    RoleName=role_name
                )
                logger.info(f"   ✅ Removed role from instance profile: {profile['InstanceProfileName']}")
        except ClientError as e:
            logger.warning(f"   ⚠️  Could not detach policies: {e}")
        
        # Now delete the role
        iam_client.delete_role(RoleName=role_name)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            logger.info(f"   Role {role_name} not found (already deleted)")
            return True
        logger.error(f"   ❌ Failed to delete IAM role: {error_code}")
        return False


def delete_security_group(ec2_client, sg_id: str) -> bool:
    """Delete security group."""
    try:
        ec2_client.delete_security_group(GroupId=sg_id)
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'InvalidGroup.NotFound':
            logger.info(f"   Security group not found (already deleted)")
            return True
        if error_code == 'DependencyViolation':
            logger.warning(f"   ⚠️  Security group {sg_id} still in use (skipping, will retry later)")
            return False  # Return False so we can retry
        logger.error(f"   ❌ Failed to delete security group: {error_code}")
        return False


def collect_all_resources(env_vars: dict, skip_cognito: bool, skip_ecs: bool, region: str) -> List[Tuple[str, str, str, dict]]:
    """Collect all resources to delete (from .env and discovered orphaned resources)."""
    resources = []
    seen_resources = set()  # Track resources to avoid duplicates
    
    # Helper to add resource if not seen
    def add_resource(rtype, rid, rname, extra):
        key = (rtype, rid)
        if key not in seen_resources:
            seen_resources.add(key)
            resources.append((rtype, rid, rname, extra))
    
    # ECS Resources (if not skipped)
    if not skip_ecs:
        if env_vars.get('ECS_CLUSTER_NAME'):
            add_resource('ecs_cluster', env_vars['ECS_CLUSTER_NAME'], 'ECS Cluster', {})
        if env_vars.get('ECS_SERVICE_NAME') and env_vars.get('ECS_CLUSTER_NAME'):
            add_resource('ecs_service', env_vars['ECS_SERVICE_NAME'], 'ECS Service', {'cluster': env_vars['ECS_CLUSTER_NAME']})
        if env_vars.get('ALB_ARN'):
            add_resource('alb', env_vars['ALB_ARN'], 'Application Load Balancer', {})
        if env_vars.get('ROUTE53_RECORD_NAME') and env_vars.get('ROUTE53_HOSTED_ZONE_ID'):
            add_resource('route53', env_vars['ROUTE53_RECORD_NAME'], 'Route 53 Record', {'hosted_zone_id': env_vars['ROUTE53_HOSTED_ZONE_ID']})
        if env_vars.get('ACM_CERTIFICATE_ARN'):
            add_resource('acm', env_vars['ACM_CERTIFICATE_ARN'], 'ACM Certificate', {})
    
    # AgentCore Resources
    if env_vars.get('AGENT_RUNTIME_ARN') or env_vars.get('AGENT_RUNTIME_ID'):
        runtime_id = env_vars.get('AGENT_RUNTIME_ARN') or env_vars.get('AGENT_RUNTIME_ID')
        add_resource('runtime', runtime_id, 'AgentCore Runtime', {})
    
    if env_vars.get('MEMORY_RESOURCE_ID') or env_vars.get('MEMORY_RESOURCE_ARN'):
        memory_id = env_vars.get('MEMORY_RESOURCE_ID') or env_vars.get('MEMORY_RESOURCE_ARN')
        add_resource('memory', memory_id, 'AgentCore Memory', {})
    
    if env_vars.get('WORKLOAD_IDENTITY_NAME'):
        add_resource('identity', env_vars['WORKLOAD_IDENTITY_NAME'], 'AgentCore Identity', {})
    
    # CloudWatch Log Groups (from .env)
    log_groups = [
        '/aws/bedrock-agentcore/runtimes',
        '/aws/bedrock-agentcore/memory',
        '/ecs/cloud-engineer-agent-service',
        '/aws/cloud-engineer-agent/streamlit'
    ]
    for log_group in log_groups:
        add_resource('log_group', log_group, f'CloudWatch Log Group: {log_group}', {})
    
    # ECR Repository
    if env_vars.get('ECR_REPOSITORY_NAME'):
        add_resource('ecr', env_vars['ECR_REPOSITORY_NAME'], 'ECR Repository', {})
    
    # Guardrail
    if env_vars.get('BEDROCK_GUARDRAIL_ID'):
        add_resource('guardrail', env_vars['BEDROCK_GUARDRAIL_ID'], 'Bedrock Guardrail', {})
    
    # Cognito User Pool (if not skipped)
    if not skip_cognito and env_vars.get('COGNITO_USER_POOL_ID'):
        add_resource('cognito', env_vars['COGNITO_USER_POOL_ID'], 'Cognito User Pool', {})
    
    # Discover orphaned resources
    logger.info("   🔍 Discovering orphaned resources...")
    orphaned = discover_orphaned_resources(region, skip_cognito, skip_ecs)
    for rtype, rid, rname, extra in orphaned:
        add_resource(rtype, rid, rname, extra)
    
    if orphaned:
        logger.info(f"   ✅ Found {len(orphaned)} orphaned resources")
    
    return resources


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Destroy ALL resources created during setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be deleted (safe)
  python scripts/destroy_all.py --dry-run

  # Destroy everything (with confirmation)
  python scripts/destroy_all.py

  # Destroy everything without confirmation (dangerous!)
  python scripts/destroy_all.py --force

  # Destroy everything except Cognito and ECS
  python scripts/destroy_all.py --skip-cognito --skip-ecs
        """
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts (DANGEROUS!)'
    )
    parser.add_argument(
        '--skip-cognito',
        action='store_true',
        help='Skip Cognito User Pool deletion (keep for reuse)'
    )
    parser.add_argument(
        '--skip-ecs',
        action='store_true',
        help='Skip ECS/ALB deletion (keep production infrastructure)'
    )
    parser.add_argument(
        '--region',
        default=None,
        help='AWS region (default: from env or us-east-2)'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No resources will be deleted")
    else:
        logger.warning("="*80)
        logger.warning("⚠️  WARNING: This will PERMANENTLY DELETE ALL RESOURCES!")
        logger.warning("⚠️  This action is IRREVERSIBLE!")
        logger.warning("="*80)
    
    logger.info("🗑️  Destroying ALL resources...")
    
    if not validate_aws_credentials():
        logger.error("❌ AWS credentials not configured")
        return 1
    
    load_dotenv()
    region = args.region or get_aws_region()
    logger.info(f"   Region: {region}")
    
    # Collect all environment variables
    env_vars = {
        'ECS_CLUSTER_NAME': os.getenv('ECS_CLUSTER_NAME'),
        'ECS_SERVICE_NAME': os.getenv('ECS_SERVICE_NAME'),
        'ALB_ARN': os.getenv('ALB_ARN'),
        'ROUTE53_RECORD_NAME': os.getenv('ROUTE53_RECORD_NAME'),
        'ROUTE53_HOSTED_ZONE_ID': os.getenv('ROUTE53_HOSTED_ZONE_ID'),
        'ACM_CERTIFICATE_ARN': os.getenv('ACM_CERTIFICATE_ARN'),
        'AGENT_RUNTIME_ARN': os.getenv('AGENT_RUNTIME_ARN'),
        'AGENT_RUNTIME_ID': os.getenv('AGENT_RUNTIME_ID'),
        'MEMORY_RESOURCE_ID': os.getenv('MEMORY_RESOURCE_ID'),
        'MEMORY_RESOURCE_ARN': os.getenv('MEMORY_RESOURCE_ARN'),
        'WORKLOAD_IDENTITY_NAME': os.getenv('WORKLOAD_IDENTITY_NAME'),
        'ECR_REPOSITORY_NAME': os.getenv('ECR_REPOSITORY_NAME') or 'cloud-engineer-agent-runtime',
        'BEDROCK_GUARDRAIL_ID': os.getenv('BEDROCK_GUARDRAIL_ID'),
        'COGNITO_USER_POOL_ID': os.getenv('COGNITO_USER_POOL_ID'),
    }
    
    # Collect all resources (from .env and discovered orphaned resources)
    resources = collect_all_resources(env_vars, args.skip_cognito, args.skip_ecs, region)
    
    if not resources:
        logger.info("   No resources found to delete.")
        return 0
    
    # Display resources to delete
    logger.info("\n" + "="*80)
    logger.info("RESOURCES TO DELETE:")
    logger.info("="*80)
    
    # Group by type for better display
    by_type = {}
    for rtype, rid, rname, extra in resources:
        if rtype not in by_type:
            by_type[rtype] = []
        by_type[rtype].append((rname, rid))
    
    type_names = {
        'ecs_service': 'ECS Services',
        'ecs_cluster': 'ECS Clusters',
        'target_group': 'Target Groups',
        'alb': 'Application Load Balancers',
        'route53': 'Route 53 Records',
        'acm': 'ACM Certificates',
        'runtime': 'AgentCore Runtime',
        'memory': 'AgentCore Memory',
        'identity': 'AgentCore Identity',
        'log_group': 'CloudWatch Log Groups',
        'ecr': 'ECR Repositories',
        'guardrail': 'Bedrock Guardrails',
        'cognito': 'Cognito User Pools',
        'iam_role': 'IAM Roles',
        'security_group': 'Security Groups',
    }
    
    for rtype in ['ecs_service', 'ecs_cluster', 'target_group', 'alb', 'route53', 'acm', 'runtime', 'memory', 'identity', 'log_group', 'ecr', 'guardrail', 'cognito', 'iam_role', 'security_group']:
        if rtype in by_type:
            logger.info(f"\n{type_names.get(rtype, rtype.upper())}:")
            for rname, rid in by_type[rtype]:
                logger.info(f"  - {rname}: {rid}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Total: {len(resources)} resources")
    logger.info("="*80)
    
    if args.dry_run:
        logger.info("\n✅ DRY RUN complete. No resources deleted.")
        logger.info("   Remove --dry-run flag to actually delete resources.")
        return 0
    
    # Confirm deletion
    if not args.force:
        logger.warning("\n⚠️  Are you ABSOLUTELY SURE you want to delete ALL these resources?")
        logger.warning("   This action is PERMANENT and IRREVERSIBLE!")
        response = input("Type 'DESTROY ALL' to confirm: ")
        if response != 'DESTROY ALL':
            logger.info("   Deletion cancelled.")
            return 0
    
    # Delete resources in safe order
    # Order: ECS Service -> ECS Cluster -> Target Groups (orphaned) -> ALB (listeners/TGs) -> Route53 -> ACM -> Runtime -> Memory -> Identity -> Log Groups -> ECR -> Guardrail -> Cognito -> IAM Roles -> Security Groups (final)
    deletion_order = ['ecs_service', 'ecs_cluster', 'target_group', 'alb', 'route53', 'acm', 'runtime', 'memory', 'identity', 'log_group', 'ecr', 'guardrail', 'cognito', 'iam_role', 'security_group']
    ordered_resources = sorted(resources, key=lambda x: deletion_order.index(x[0]) if x[0] in deletion_order else 99)
    
    logger.info("\n🗑️  Deleting resources...")
    deleted = []
    failed = []
    
    # Initialize AWS clients
    ecs_client = boto3.client('ecs', region_name=region)
    elb_client = boto3.client('elbv2', region_name=region)
    route53_client = boto3.client('route53', region_name=region)
    acm_client = boto3.client('acm', region_name=region)
    logs_client = boto3.client('logs', region_name=region)
    ecr_client = boto3.client('ecr', region_name=region)
    cognito_client = boto3.client('cognito-idp', region_name=region)
    iam_client = boto3.client('iam')
    ec2_client = boto3.client('ec2', region_name=region)
    
    for rtype, rid, rname, extra in ordered_resources:
        logger.info(f"\n   Deleting {rname} ({rid})...")
        
        success = False
        try:
            if rtype == 'ecs_service':
                success = delete_ecs_service(ecs_client, extra['cluster'], rid)
            elif rtype == 'ecs_cluster':
                success = delete_ecs_cluster(ecs_client, rid)
            elif rtype == 'alb':
                success = delete_application_load_balancer(elb_client, rid)
            elif rtype == 'target_group':
                success = delete_target_group_standalone(elb_client, rid)
            elif rtype == 'route53':
                success = delete_route53_record(route53_client, extra['hosted_zone_id'], rid)
            elif rtype == 'acm':
                success = delete_acm_certificate(acm_client, rid)
            elif rtype == 'runtime':
                success = delete_runtime_resource(rid, region)
            elif rtype == 'memory':
                success = delete_memory_resource(rid, region)
            elif rtype == 'identity':
                success = delete_identity_resource(rid, region)
            elif rtype == 'log_group':
                success = delete_cloudwatch_log_group(logs_client, rid)
            elif rtype == 'ecr':
                success = delete_ecr_repository(ecr_client, rid)
            elif rtype == 'guardrail':
                success = delete_guardrail_resource(rid, region)
            elif rtype == 'cognito':
                success = delete_cognito_user_pool(cognito_client, rid)
            elif rtype == 'iam_role':
                success = delete_iam_role(iam_client, rid)
            elif rtype == 'security_group':
                success = delete_security_group(ec2_client, rid)
        except Exception as e:
            logger.error(f"   ❌ Unexpected error: {e}")
            success = False
        
        if success:
            logger.info(f"   ✅ {rname} deleted successfully")
            deleted.append((rtype, rname))
            
            # Update .env file
            env_key_map = {
                'ecs_cluster': 'ECS_CLUSTER_NAME',
                'ecs_service': 'ECS_SERVICE_NAME',
                'alb': 'ALB_ARN',
                'target_group': [],  # Target groups not stored in .env
                'route53': 'ROUTE53_RECORD_NAME',
                'acm': 'ACM_CERTIFICATE_ARN',
                'runtime': ['AGENT_RUNTIME_ARN', 'AGENT_RUNTIME_ID'],
                'memory': ['MEMORY_RESOURCE_ARN', 'MEMORY_RESOURCE_ID'],
                'identity': ['WORKLOAD_IDENTITY_NAME', 'WORKLOAD_IDENTITY_ARN'],
                'ecr': 'ECR_REPOSITORY_NAME',
                'guardrail': ['BEDROCK_GUARDRAIL_ID', 'BEDROCK_GUARDRAIL_VERSION'],
                'cognito': ['COGNITO_USER_POOL_ID', 'COGNITO_CLIENT_ID'],
                'iam_role': [],  # IAM roles not stored in .env
                'security_group': [],  # Security groups not stored in .env
            }
            
            keys_to_clear = env_key_map.get(rtype, [])
            if isinstance(keys_to_clear, str):
                keys_to_clear = [keys_to_clear]
            
            for key in keys_to_clear:
                if key in env_vars and env_vars[key]:
                    set_key('.env', key, '', quote_mode='never')
        else:
            logger.error(f"   ❌ Failed to delete {rname}")
            failed.append((rtype, rname))
        
        # Small delay between deletions
        time.sleep(2)
    
    # Retry failed security groups (they might have been in use before)
    logger.info("\n🔄 Retrying failed security group deletions...")
    security_groups_to_retry = [(rtype, rid, rname, extra) for rtype, rid, rname, extra in resources if rtype == 'security_group' and (rtype, rname) in [(f[0], f[1]) for f in failed]]
    for rtype, rid, rname, extra in security_groups_to_retry:
        logger.info(f"   Retrying {rname} ({rid})...")
        success = delete_security_group(ec2_client, rid)
        if success:
            logger.info(f"   ✅ {rname} deleted successfully")
            deleted.append((rtype, rname))
            failed.remove((rtype, rname))
        time.sleep(1)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DESTRUCTION SUMMARY")
    logger.info("="*80)
    logger.info(f"   Deleted: {len(deleted)}")
    logger.info(f"   Failed: {len(failed)}")
    
    if deleted:
        logger.info("\n   Successfully deleted:")
        for rtype, rname in deleted:
            logger.info(f"     ✅ {rname}")
    
    if failed:
        logger.info("\n   Failed to delete:")
        for rtype, rname in failed:
            logger.info(f"     ❌ {rname}")
        logger.info("\n   💡 You may need to manually delete these resources from AWS Console")
    
    logger.info("\n" + "="*80)
    
    if not failed:
        logger.info("✅ All resources destroyed successfully!")
        logger.info("   💡 .env file has been updated")
        logger.info("   💡 You can now run setup scripts again to recreate everything")
        logger.info("\n🔍 Final verification recommended:")
        logger.info("   python scripts/list_agentcore_resources.py --resource-type all")
        logger.info("   python scripts/verify_agentcore_resources.py --all")
        logger.info("\n💡 To verify no orphaned resources remain:")
        logger.info("   aws ecs list-clusters | grep cloud-engineer-agent")
        logger.info("   aws elbv2 describe-load-balancers | grep cloud-engineer-agent")
        logger.info("   aws ecr describe-repositories | grep cloud-engineer-agent")
        logger.info("   aws cognito-idp list-user-pools | grep cloud-engineer-agent")
        logger.info("   aws iam list-roles | grep cloud-engineer-agent")
    else:
        logger.warning("⚠️  Some resources could not be deleted")
        logger.info("   💡 Common reasons:")
        logger.info("      - Resources still in use (wait a few minutes and retry)")
        logger.info("      - Security groups attached to other resources")
        logger.info("      - IAM roles attached to instance profiles")
        logger.info("   💡 Check AWS Console for manual cleanup")
        logger.info("   💡 Run script again after a few minutes to clean up remaining resources")
        logger.info("   💡 Orphaned resources will be discovered and deleted on next run")
    
    logger.info("="*80)
    
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

