# Material Recognition Service

**🚀 Production Ready - ECR Deployment**

A production-ready application with automated CI/CD deployment workflow using AWS ECR and EC2.

## Overview

This service demonstrates a modern containerized deployment pipeline using:
- **Backend**: Python Flask API with AWS S3/DynamoDB integration
- **Containerization**: Docker with Python 3.11
- **Infrastructure**: AWS CDK with EC2, ECR, CodePipeline, S3, DynamoDB
- **Deployment**: Automated CI/CD via GitHub webhooks with ECR image deployment

## Current Status

- ✅ Infrastructure deployed with CDK
- ✅ ECR repository configured
- ✅ CI/CD pipeline configured (GitHub → CodeBuild → ECR → EC2)
- ✅ Docker containerization
- ✅ Automated deployment to EC2 via SSM
- ✅ AWS storage integration (S3 + DynamoDB)

## Architecture

### Deployment Flow
1. **Source**: GitHub mainline branch triggers pipeline
2. **Build**: AWS CodeBuild builds Docker image
3. **Push**: Image pushed to AWS ECR repository
4. **Deploy**: SSM commands deploy container to EC2 instance

### Container Details
- **Base Image**: Python 3.11 slim
- **Web Server**: Gunicorn with 4 workers
- **Port**: 5000
- **Health Check**: `/health` endpoint

## Local Development

### Prerequisites
- Docker
- Python 3.11
- AWS CLI configured

### Running Locally
```bash
# Build Docker image
docker build -t material-recognition-service .

# Run container
docker run -p 5000:5000 material-recognition-service

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:5000/add/5/3
```

### Development without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Test endpoints
curl http://localhost:5000/health
```

## API Endpoints

### Core Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Basic calculation
curl http://localhost:5000/add/5/3

# Root endpoint
curl http://localhost:5000/
```

### Storage Endpoints
```bash
# Storage status
curl http://localhost:5000/storage/test

# S3 test
curl http://localhost:5000/storage/s3/test

# DynamoDB test
curl http://localhost:5000/storage/dynamodb/test

# Save test data
curl http://localhost:5000/storage/save-test

# Diagnostic information
curl http://localhost:5000/diagnose
```

## Infrastructure

### AWS Resources
- **ECR Repository**: Stores Docker images
- **EC2 Instance**: Runs the application container
- **CodePipeline**: Orchestrates CI/CD workflow
- **CodeBuild**: Builds and pushes Docker images
- **S3 Bucket**: `matsight-customer-images-dev`
- **DynamoDB Table**: `CustomerImages-Dev`

### IAM Permissions
- ECR push/pull permissions for CodeBuild
- SSM command execution for EC2 deployment
- S3 and DynamoDB access for application

## Deployment

### Manual Deployment
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t material-recognition-service .
docker tag material-recognition-service:latest <ecr-repo-uri>:latest
docker push <ecr-repo-uri>:latest

# Deploy to EC2 (via SSM)
aws ssm send-command --instance-ids <instance-id> --document-name "AWS-RunShellScript" --parameters '{"commands":["docker pull <ecr-repo-uri>:latest","docker stop material-recognition || true","docker rm material-recognition || true","docker run -d --name material-recognition -p 5000:5000 --restart always <ecr-repo-uri>:latest"]}'
```

### Automated Deployment
The pipeline automatically:
1. Monitors GitHub mainline branch
2. Builds Docker image on code changes
3. Pushes to ECR repository
4. Deploys to EC2 instance via SSM

## Monitoring

### Container Status
```bash
# Check container status
docker ps

# View container logs
docker logs material-recognition

# Check application health
curl http://localhost:5000/health
```

### System Status
```bash
# Check systemd service (if applicable)
systemctl status material-recognition.service

# View application logs
journalctl -u material-recognition.service -f
```

## Troubleshooting

### Common Issues
1. **Container won't start**: Check Docker logs and port conflicts
2. **ECR login failed**: Verify AWS credentials and region
3. **SSM deployment failed**: Check instance permissions and connectivity
4. **Application errors**: Check container logs and health endpoint

### Debug Commands
```bash
# Check ECR repository
aws ecr describe-repositories

# List ECR images
aws ecr list-images --repository-name material-recognition-service

# Check SSM command status
aws ssm get-command-invocation --command-id <command-id> --instance-id <instance-id>
```

## Configuration

### Environment Variables
- `PORT`: Application port (default: 5000)
- `AWS_DEFAULT_REGION`: AWS region for services
- `AWS_ACCESS_KEY_ID`: AWS access key (if not using IAM roles)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (if not using IAM roles)

### Docker Configuration
- **Memory**: 512MB minimum
- **CPU**: 1 vCPU minimum
- **Storage**: 10GB minimum
- **Network**: Port 5000 exposed

## Security

- **Container Security**: Non-root user, minimal base image
- **Network Security**: VPC isolation, security groups
- **IAM Security**: Least privilege principle
- **Secrets Management**: AWS Secrets Manager for sensitive data

---

*This application is production-ready and follows AWS best practices for containerized deployments.*