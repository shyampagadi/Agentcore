"""
===============================================================================
MODULE: predefined_tasks.py
===============================================================================

PURPOSE:
    Predefined tasks dictionary for Cloud Engineer Agent.

WHEN TO USE THIS MODULE:
    - Agent initialization: Loaded by cloud_engineer_agent.py
    - Task selection: Used by frontend to display available tasks

USAGE EXAMPLES:
    from prompts.cloud_engineer.predefined_tasks import PREDEFINED_TASKS
    
    task_description = PREDEFINED_TASKS.get("ec2_status")
    all_tasks = PREDEFINED_TASKS

WHAT THIS MODULE DOES:
    1. Contains dictionary of predefined cloud engineering tasks
    2. Provides task descriptions for quick selection
    3. Organized by category for easy navigation

RELATED FILES:
    - agents/cloud_engineer_agent.py - Uses this dictionary

AUTHOR: Enterprise Cloud Engineer Agent Project
DATE: 2025-01-XX
VERSION: 1.0.0
===============================================================================
"""

PREDEFINED_TASKS = {
    # Single Resource Operations (CloudFormation MCP)
    "ec2_status": "List all EC2 instances and their status",
    "s3_buckets": "List all S3 buckets and their creation dates",
    "cloudwatch_alarms": "Check for any CloudWatch alarms in ALARM state",
    "iam_users": "List all IAM users and their last activity",
    "security_groups": "Analyze security groups for potential vulnerabilities",
    "lambda_functions": "List all Lambda functions and their runtime",
    "rds_instances": "Check status of all RDS instances",
    "vpc_analysis": "Analyze VPC configuration and suggest improvements",
    "ebs_volumes": "Find unattached EBS volumes that could be removed",
    "create_s3_bucket": "Create a new S3 bucket with best practices",
    "create_ec2_instance": "Create a new EC2 instance with proper configuration",
    "create_rds_database": "Create a new RDS database instance",
    "create_vpc": "Create a new VPC with subnets and routing",
    "create_lambda_function": "Create a new Lambda function",
    "create_iam_role": "Create a new IAM role with proper permissions",
    "create_security_group": "Create a new security group with proper rules",

    # Complete Infrastructure Stacks
    "create_website_infrastructure": "Create complete website infrastructure stack (VPC, EC2, RDS, ALB)",
    "create_web_application": "Create complete web application stack with load balancing",
    "create_database_stack": "Create complete database infrastructure stack",
    "create_monitoring_stack": "Create complete monitoring and alerting stack",
    "create_security_stack": "Create complete security infrastructure stack",
    "create_backup_stack": "Create complete backup and disaster recovery stack",
    "create_development_environment": "Create complete development environment stack",
    "create_staging_environment": "Create complete staging environment stack",
    "create_production_environment": "Create complete production environment stack",
    "create_ecommerce_platform": "Create complete e-commerce platform infrastructure",
    "create_api_backend": "Create complete API backend infrastructure",
    "create_microservices_stack": "Create complete microservices infrastructure",
    "create_data_pipeline": "Create complete data processing pipeline",
    "create_ml_infrastructure": "Create complete machine learning infrastructure",

    # AWS Best Practices and Guidance
    "security_best_practices": "Get AWS security best practices and recommendations",
    "cost_optimization_guidance": "Get AWS cost optimization best practices and tips",
    "performance_optimization": "Get AWS performance optimization recommendations",
    "compliance_guidance": "Get AWS compliance and governance best practices",
    "disaster_recovery_planning": "Get AWS disaster recovery planning guidance",
    "monitoring_best_practices": "Get AWS monitoring and observability best practices",
    "networking_best_practices": "Get AWS networking and VPC best practices",
    "database_best_practices": "Get AWS database design and optimization best practices",
    "serverless_best_practices": "Get AWS serverless architecture best practices",
    "container_best_practices": "Get AWS container and Kubernetes best practices",

    # Infrastructure Management
    "update_infrastructure": "Update existing infrastructure stack",
    "scale_infrastructure": "Scale infrastructure up or down",
    "backup_infrastructure": "Create backup of existing infrastructure",
    "restore_infrastructure": "Restore infrastructure from backup",
    "delete_infrastructure": "Delete complete infrastructure stack",
    "infrastructure_audit": "Audit existing infrastructure for compliance",
    "infrastructure_documentation": "Generate infrastructure documentation",

    # Cost Analysis and Optimization (Cost Explorer MCP)
    "analyze_monthly_costs": "Analyze current month AWS spending by service and region",
    "cost_trend_analysis": "Analyze cost trends and patterns over last 6 months",
    "identify_cost_savings": "Identify top cost optimization opportunities and recommendations",
    "service_cost_breakdown": "Get detailed cost breakdown by AWS service",
    "regional_cost_analysis": "Analyze costs by AWS region and availability zone",
    "resource_utilization_costs": "Analyze resource utilization and associated costs",
    "budget_variance_analysis": "Compare actual spending against budgets and forecasts",
    "cost_anomaly_detection": "Detect unusual spending patterns and cost anomalies",
    
    # AWS Architecture Diagrams
    "generate_architecture_diagram": "Generate AWS architecture diagram from current infrastructure",
    "create_3tier_diagram": "Create 3-tier web application architecture diagram",
    "visualize_vpc_architecture": "Generate VPC and networking architecture diagram",
    "create_serverless_diagram": "Generate serverless architecture diagram",
    "diagram_microservices": "Create microservices architecture diagram"
}

