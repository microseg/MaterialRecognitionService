#!/usr/bin/env python3
"""
Simple test deployment script for debugging
"""

import os
import json
from datetime import datetime

def main():
    """Main function"""
    print("🚀 Starting simple deployment test...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Print environment variables
    print("Environment variables:")
    print(f"  PROD_INSTANCE_ID: {os.environ.get('PROD_INSTANCE_ID', 'NOT_SET')}")
    print(f"  PROD_PRIVATE_IP: {os.environ.get('PROD_PRIVATE_IP', 'NOT_SET')}")
    print(f"  VPC_ID: {os.environ.get('VPC_ID', 'NOT_SET')}")
    print(f"  DEV_SG_ID: {os.environ.get('DEV_SG_ID', 'NOT_SET')}")
    
    # Create a simple deployment report
    deployment_report = {
        'timestamp': datetime.now().isoformat(),
        'status': 'success',
        'message': 'Simple deployment test completed successfully',
        'prod_instance_id': os.environ.get('PROD_INSTANCE_ID', 'unknown'),
        'prod_private_ip': os.environ.get('PROD_PRIVATE_IP', 'unknown')
    }
    
    # Save report
    with open('deploy-output.json', 'w') as f:
        json.dump(deployment_report, f, indent=2)
    
    print("✅ Simple deployment test completed successfully!")
    print("📄 Created deploy-output.json")
    
    return 0

if __name__ == '__main__':
    exit(main())
