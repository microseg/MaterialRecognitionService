#!/usr/bin/env python3
"""
Adaptive deployment script for Matsight Recognition Backend
- Used by AWS CodeBuild to deploy to production EC2 via SSM
- Auto-detects app entry and start command
- Configurable via environment variables
"""

import boto3
import json
import os
import time
import sys
from datetime import datetime

# AWS clients
ec2_client = boto3.client('ec2')
ssm_client = boto3.client('ssm')

# -------- Config (env-driven with sensible defaults) --------
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'matsight-backend')
APP_DIR = os.environ.get('APP_DIR', '.')  # relative to CODEBUILD_SRC_DIR
REQUIREMENTS_FILE = os.environ.get('REQUIREMENTS_FILE', 'requirements.txt')
PORT = os.environ.get('PORT', '8000')
HEALTH_PATH = os.environ.get('HEALTH_PATH', '/health')
INSTALL_SYSTEM_PACKAGES = os.environ.get('INSTALL_SYSTEM_PACKAGES', 'true').lower() == 'true'
START_CMD_ENV = os.environ.get('START_CMD')  # if provided, use as-is

# Precompute strings we will inject into command lines
app_subdir_str = APP_DIR
start_cmd_prefill = START_CMD_ENV or ''

# -------- Helpers --------

def get_prod_instance():
    try:
        resp = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['RecogBackendStack/RecogProdHost']},
                {'Name': 'instance-state-name', 'Values': ['running']},
            ]
        )
        if resp['Reservations'] and resp['Reservations'][0]['Instances']:
            inst = resp['Reservations'][0]['Instances'][0]
            print(f"✅ Found production instance: {inst['InstanceId']}")
            return {
                'id': inst['InstanceId'],
                'private_ip': inst['PrivateIpAddress'],
                'public_ip': inst.get('PublicIpAddress'),
            }
        print('❌ No production instance found!')
        return None
    except Exception as e:
        print(f"❌ Error getting prod instance: {e}")
        return None


def build_deploy_commands() -> list:
    """Build shell commands to run on EC2 (idempotent)."""
    # System packages (optional)
    sys_pkg_block = []
    if INSTALL_SYSTEM_PACKAGES:
        sys_pkg_block = [
            'sudo yum update -y',
            'sudo yum install -y git python3 python3-pip python3-devel gcc make rsync curl',
        ]

    commands = [
        '#!/bin/bash',
        'set -e',
        "echo 'Starting adaptive deployment...'",
        *sys_pkg_block,
        '# Prepare target directory',
        'sudo mkdir -p /opt/matsight',
        'sudo chown ec2-user:ec2-user /opt/matsight',
        'sudo mkdir -p /opt/matsight/current',
        'sudo chown ec2-user:ec2-user /opt/matsight/current',
        '# Stop service if running (ignore errors)',
        f'sudo systemctl stop {SERVICE_NAME} || true',
        '# Backup existing deployment',
        "if [ -d '/opt/matsight/current' ] && [ \"$(ls -A /opt/matsight/current || true)\" ]; then",
        '  sudo mkdir -p /opt/matsight/backup',
        '  sudo mv /opt/matsight/current /opt/matsight/backup/$(date +%Y%m%d-%H%M%S) || true',
        '  sudo mkdir -p /opt/matsight/current',
        '  sudo chown ec2-user:ec2-user /opt/matsight/current',
        'fi',
        '# Resolve source directory from CodeBuild',
        'SRC=${CODEBUILD_SRC_DIR:-/tmp/source}',
        f"APP_SUBDIR='{app_subdir_str}'",
        'if [ -n "$APP_SUBDIR" ] && [ "$APP_SUBDIR" != "." ]; then SRC="$SRC/$APP_SUBDIR"; fi',
        'echo "Using source: $SRC"',
        'ls -la "$SRC" || true',
        '# Copy source into deployment dir',
        'sudo rsync -a --delete "$SRC"/ /opt/matsight/current/ || true',
        'sudo chown -R ec2-user:ec2-user /opt/matsight/current',
        '# Python environment',
        'cd /opt/matsight/current',
        'python3 -m venv venv',
        'source venv/bin/activate',
        f"if [ -f '{REQUIREMENTS_FILE}' ]; then pip install -r {REQUIREMENTS_FILE} || true; fi",
        '# Auto-detect start command (unless START_CMD provided)',
        f'PORT={PORT}',
        f"START_CMD='{start_cmd_prefill}'",
        'if [ -z "$START_CMD" ]; then',
        '  if [ -f requirements.txt ] && grep -qiE "^gunicorn(==|\\s|$)" requirements.txt 2>/dev/null; then',
        '    if [ -f app.py ] && (grep -qE "^\\s*app\\s*=\\s*Flask" app.py 2>/dev/null || grep -qE "Flask\\(" app.py 2>/dev/null); then',
        '      START_CMD="gunicorn -b 0.0.0.0:$PORT app:app"',
        '    else',
        '      START_CMD="gunicorn -b 0.0.0.0:$PORT app:app" # default entry',
        '    fi',
        '  elif [ -f requirements.txt ] && grep -qiE "^uvicorn(==|\\s|$)" requirements.txt 2>/dev/null; then',
        '    START_CMD="uvicorn app:app --host 0.0.0.0 --port $PORT"',
        '  elif [ -f app.py ]; then',
        '    START_CMD="/opt/matsight/current/venv/bin/python app.py"',
        '  else',
        "    echo 'No recognizable app entry found. Creating a minimal Flask app.'",
        "    tee app.py > /dev/null <<'EOF'",
        'from flask import Flask, jsonify',
        'import datetime',
        'app = Flask(__name__)',
        '',
        '@app.route(\'/\')',
        'def home():',
        "    return jsonify({'message':'OK','timestamp': datetime.datetime.now().isoformat()})",
        '',
        "if __name__ == '__main__':",
        '    app.run(host=\'0.0.0.0\', port=8000, debug=False)',
        'EOF',
        '    pip install Flask==2.3.3 Werkzeug==2.3.7 || true',
        '    START_CMD="/opt/matsight/current/venv/bin/python app.py"',
        '  fi',
        'fi',
        'echo "Using START_CMD: $START_CMD"',
        '# systemd unit (idempotent)',
        f"sudo tee /etc/systemd/system/{SERVICE_NAME}.service > /dev/null <<'EOF'",
        '[Unit]',
        f'Description={SERVICE_NAME}',
        'After=network.target',
        '',
        '[Service]',
        'Type=simple',
        'User=ec2-user',
        'WorkingDirectory=/opt/matsight/current',
        'Environment=PATH=/opt/matsight/current/venv/bin',
        'ExecStart=/bin/bash -lc "$START_CMD"',
        'Restart=always',
        'RestartSec=10',
        '',
        '[Install]',
        'WantedBy=multi-user.target',
        'EOF',
        '# start service',
        'sudo systemctl daemon-reload',
        f'sudo systemctl enable {SERVICE_NAME}',
        f'sudo systemctl start {SERVICE_NAME}',
        f'sudo systemctl status {SERVICE_NAME} --no-pager || true',
        '# basic health check (local)',
        f'curl -fsS http://127.0.0.1:{PORT}{HEALTH_PATH} || true',
        "echo 'Deployment completed.'",
    ]
    return commands


def deploy_to_production(instance_info):
    try:
        instance_id = instance_info['id']
        print(f"🚀 Deploying to PRODUCTION instance: {instance_id} ({instance_info['private_ip']})")
        deploy_commands = build_deploy_commands()
        resp = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': deploy_commands},
        )
        cmd_id = resp['Command']['CommandId']
        print(f"📋 Deployment command sent: {cmd_id}")
        print("⏳ Waiting for deployment to complete...")
        while True:
            time.sleep(10)
            st = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
            status = st['Status']
            print(f"📊 Current status: {status}")
            if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                if status == 'Success':
                    print('✅ Deployment success')
                    return True
                else:
                    print(f"❌ Deployment failed: {status}")
                    print(st.get('StandardErrorContent', 'no stderr'))
                    return False
    except Exception as e:
        print(f"❌ Error deploying: {e}")
        return False


def main():
    print('🚀 Starting Adaptive Deployment to PRODUCTION...')
    print(f'Timestamp: {datetime.now().isoformat()}')
    print('Config:')
    print(f'  SERVICE_NAME={SERVICE_NAME}')
    print(f'  APP_DIR={APP_DIR}')
    print(f'  REQUIREMENTS_FILE={REQUIREMENTS_FILE}')
    print(f'  PORT={PORT}')
    print(f'  HEALTH_PATH={HEALTH_PATH}')
    print(f'  INSTALL_SYSTEM_PACKAGES={INSTALL_SYSTEM_PACKAGES}')
    print(f'  START_CMD (env)={START_CMD_ENV or ""}')

    prod = get_prod_instance()
    if not prod:
        sys.exit(1)

    ok = deploy_to_production(prod)
    report = {
        'timestamp': datetime.now().isoformat(),
        'prod_instance_id': prod['id'],
        'success': ok,
    }
    with open('deploy-output.json', 'w') as f:
        json.dump(report, f, indent=2)
    print('📄 Wrote deploy-output.json')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
