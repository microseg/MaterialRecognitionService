#!/usr/bin/env python3
"""
Automated deployment script for Matsight Recognition Backend
This script is used by AWS CodeBuild to deploy to all EC2 instances
"""

import boto3
import json
import os
import subprocess
import time
from datetime import datetime

# AWS clients
ec2_client = boto3.client('ec2')
ssm_client = boto3.client('ssm')

def get_all_dev_instances():
    """Get all development EC2 instances (for reference only)"""
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['MatsightUser-*']
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        )
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'private_ip': instance['PrivateIpAddress'],
                    'public_ip': instance.get('PublicIpAddress'),
                    'name': next((tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'), 'Unknown')
                })
        
        return instances
    except Exception as e:
        print(f"Error getting dev instances: {e}")
        return []

def get_prod_instance():
    """Get production EC2 instance"""
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['RecogBackendStack/RecogProdHost']
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        )
        
        if response['Reservations'] and response['Reservations'][0]['Instances']:
            instance = response['Reservations'][0]['Instances'][0]
            return {
                'id': instance['InstanceId'],
                'private_ip': instance['PrivateIpAddress'],
                'public_ip': instance.get('PublicIpAddress')
            }
        return None
    except Exception as e:
        print(f"Error getting prod instance: {e}")
        return None

def deploy_to_instance(instance_info, is_prod=False):
    """Deploy code to a specific instance using SSM"""
    try:
        instance_id = instance_info['id']
        private_ip = instance_info['private_ip']
        
        print(f"Deploying to {'PRODUCTION' if is_prod else 'DEV'} instance: {instance_id} ({private_ip})")
        
        # Create deployment script
        deploy_commands = [
            "#!/bin/bash",
            "set -e",
            "echo 'Starting deployment...'",
            "",
            "# Update system",
            "sudo yum update -y",
            "",
            "# Install dependencies",
            "sudo yum install -y git python3 python3-pip python3-devel gcc make rsync",
            "",
            "# Create deployment directory",
            "sudo mkdir -p /opt/matsight",
            "sudo chown ec2-user:ec2-user /opt/matsight",
            "",
            "# Stop existing services",
            "sudo systemctl stop matsight-backend || true",
            "",
            "# Backup existing deployment",
            "if [ -d '/opt/matsight/current' ]; then",
            "  sudo mv /opt/matsight/current /opt/matsight/backup-$(date +%Y%m%d-%H%M%S)",
            "fi",
            "",
            "# Create new deployment directory",
            "sudo mkdir -p /opt/matsight/current",
            "sudo chown ec2-user:ec2-user /opt/matsight/current",
            "",
            "# Copy source code",
            "sudo cp -r /tmp/source/* /opt/matsight/current/",
            "",
            "# Set up Python environment",
            "cd /opt/matsight/current",
            "python3 -m venv venv",
            "source venv/bin/activate",
            "pip install -r requirements.txt || true",
            "",
            "# Set up systemd service",
            "sudo tee /etc/systemd/system/matsight-backend.service > /dev/null <<'EOF'",
            "[Unit]",
            "Description=Matsight Recognition Backend",
            "After=network.target",
            "",
            "[Service]",
            "Type=simple",
            "User=ec2-user",
            "WorkingDirectory=/opt/matsight/current",
            "Environment=PATH=/opt/matsight/current/venv/bin",
            "ExecStart=/opt/matsight/current/venv/bin/python app.py",
            "Restart=always",
            "RestartSec=10",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "",
            "# Reload systemd and start service",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable matsight-backend",
            "sudo systemctl start matsight-backend",
            "",
            "# Check service status",
            "sudo systemctl status matsight-backend --no-pager",
            "",
            "echo 'Deployment completed successfully!'"
        ]
        
        # Execute deployment via SSM
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': deploy_commands
            }
        )
        
        command_id = response['Command']['CommandId']
        print(f"Deployment command sent: {command_id}")
        
        # Wait for command completion
        while True:
            time.sleep(5)
            status_response = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            status = status_response['Status']
            if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                if status == 'Success':
                    print(f"✅ Deployment to {instance_id} completed successfully")
                    return True
                else:
                    print(f"❌ Deployment to {instance_id} failed: {status}")
                    return False
                    
    except Exception as e:
        print(f"Error deploying to {instance_id}: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting Matsight Recognition Backend deployment to PRODUCTION...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Get instances (dev instances for reference only)
    dev_instances = get_all_dev_instances()
    prod_instance = get_prod_instance()
    
    print(f"Found {len(dev_instances)} development instances (for reference)")
    if prod_instance:
        print(f"Found 1 production instance: {prod_instance['id']}")
    
    # Only deploy to production instance
    prod_success = False
    if prod_instance:
        print(f"\n--- Deploying to PRODUCTION instance ---")
        prod_success = deploy_to_instance(prod_instance, is_prod=True)
    else:
        print("❌ No production instance found!")
        exit(1)
    
    # Create deployment report
    deployment_report = {
        'timestamp': datetime.now().isoformat(),
        'dev_instances_total': len(dev_instances),
        'dev_instances_deployed': 0,  # Dev instances are not auto-deployed
        'prod_instance_success': prod_success,
        'overall_success': prod_success
    }
    
    # Save report
    with open('deploy-output.json', 'w') as f:
        json.dump(deployment_report, f, indent=2)
    
    # Print summary
    print(f"\n📊 Deployment Summary:")
    print(f"   Development instances: {len(dev_instances)} (not auto-deployed)")
    print(f"   Production instance: {'✅ Success' if prod_success else '❌ Failed'}")
    print(f"   Overall: {'✅ SUCCESS' if deployment_report['overall_success'] else '❌ FAILED'}")
    
    # Exit with appropriate code
    if deployment_report['overall_success']:
        print("🎉 Production deployment completed successfully!")
        print("💡 Development instances can be updated manually from their respective EC2s")
        exit(0)
    else:
        print("💥 Production deployment failed!")
        exit(1)

if __name__ == '__main__':
    main()
