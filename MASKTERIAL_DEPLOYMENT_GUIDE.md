# MaskTerial Deployment Guide

This guide explains how to deploy the MaskTerial 2D Material Detection Service using AWS CDK.

## Overview

The MaskTerial service is a Flask-based API that uses the MaskTerial deep learning model to detect 2D material flakes in microscopy images. The service integrates with AWS S3 for image storage and DynamoDB for metadata management.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │   API Gateway   │    │   Load Balancer │
│                 │───▶│                 │───▶│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   S3 Bucket     │◀───│   DynamoDB      │◀───│  MaskTerial     │
│   (Images)      │    │   (Metadata)    │    │  EC2 Instance   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

1. **AWS Account**: You need an AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI
3. **Node.js**: Install Node.js (version 16 or later)
4. **CDK**: Install AWS CDK CLI
5. **Docker**: Install Docker for local testing
6. **Git**: Install Git

## Installation

### 1. Install Dependencies

```bash
# Install AWS CDK CLI
npm install -g aws-cdk

# Install project dependencies
cd MaterialRecognitionServiceCDK
npm install
```

### 2. Configure AWS Credentials

```bash
aws configure
```

### 3. Bootstrap CDK (if not already done)

```bash
cdk bootstrap
```

## Deployment

### 1. Deploy the Infrastructure

```bash
# Deploy with default configuration
cdk deploy

# Or deploy with custom configuration
cdk deploy \
  --context s3BucketName=matsight-customer-images-prod \
  --context dynamoDBTableName=CustomerImagesProd \
  --context enableStorageAutoScaling=true
```

### 2. Environment Variables

The deployment will output important information including:
- S3 bucket name
- DynamoDB table name
- EC2 instance ID
- Service URLs

### 3. Configure EC2 Instance

After deployment, you need to:

1. **Create SSH Key Pair**:
   ```bash
   aws ec2 create-key-pair --key-name maskterial-key --query 'KeyMaterial' --output text > maskterial-key.pem
   chmod 400 maskterial-key.pem
   ```

2. **SSH into the EC2 instance**:
   ```bash
   ssh -i maskterial-key.pem ec2-user@<EC2_PUBLIC_IP>
   ```

3. **Verify the service is running**:
   ```bash
   curl http://localhost:5000/health
   ```

## Local Development

### 1. Run with Docker Compose

```bash
# Set environment variables
export S3_BUCKET_NAME=your-s3-bucket-name
export DYNAMODB_TABLE_NAME=your-dynamodb-table-name
export AWS_DEFAULT_REGION=us-east-1

# Run the service
docker-compose -f docker-compose.maskterial.yml up --build
```

### 2. Test the Service

```bash
# Run tests
python test_maskterial.py

# Or test manually
curl http://localhost:5000/health
curl http://localhost:5000/info
```

## API Endpoints

### Health Check
```
GET /health
```

### Service Information
```
GET /info
```

### Detect from Uploaded Image
```
POST /detect
Content-Type: multipart/form-data

Parameters:
- image: Image file
- customer_id: Customer identifier (optional)
```

### Detect from S3
```
POST /detect_from_s3
Content-Type: application/json

Body:
{
  "s3_key": "customer-123/uploaded/image.jpg",
  "customer_id": "customer-123"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket for storing images | `matsight-customer-images` |
| `DYNAMODB_TABLE_NAME` | DynamoDB table for metadata | `CustomerImages` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |
| `MODEL_PATH` | Path to MaskTerial models | `/opt/maskterial/models` |
| `ENABLE_GPU` | Enable GPU support | `false` |

### S3 Bucket Structure

```
s3://matsight-customer-images/
├── {customerID}/
│   ├── uploaded/
│   │   ├── {imageID}_original.jpg
│   │   └── {imageID}_thumbnail.jpg
│   └── saved-result/
│       ├── {imageID}_result.jpg
│       └── {imageID}_thumbnail.jpg
```

### DynamoDB Schema

| Field | Type | Description |
|-------|------|-------------|
| customerID | String | Partition Key |
| imageID | String | Sort Key |
| createdAt | Number | Creation timestamp |
| type | String | Image type |
| s3Key | String | S3 object key |
| materialType | String | Detected material |
| processingStatus | String | Processing status |
| metadata | Object | Detection results |

## Monitoring and Logging

### CloudWatch Logs

The service automatically sends logs to CloudWatch:
- Application logs: `/aws/ec2/maskterial/app`
- Docker logs: `/aws/ec2/maskterial/docker`

### Health Checks

The service includes health checks:
- Application health: `GET /health`
- Docker health check: Every 30 seconds
- Cron job: Every 5 minutes

## Troubleshooting

### Common Issues

1. **Model not loading**:
   - Check if MaskTerial is properly installed
   - Verify model files are in the correct location
   - Check GPU drivers if using GPU

2. **S3 access denied**:
   - Verify IAM roles and policies
   - Check bucket permissions
   - Ensure correct region configuration

3. **DynamoDB errors**:
   - Verify table exists and is accessible
   - Check IAM permissions
   - Verify table schema

### Debug Commands

```bash
# Check service status
sudo systemctl status docker
docker ps

# View logs
docker logs <container_id>
tail -f /opt/maskterial/logs/app.log

# Test AWS connectivity
aws s3 ls s3://your-bucket-name
aws dynamodb describe-table --table-name your-table-name
```

## Security Considerations

1. **Network Security**:
   - Use security groups to restrict access
   - Consider using VPC endpoints for AWS services
   - Enable SSL/TLS for API communication

2. **Data Security**:
   - Enable S3 bucket encryption
   - Use DynamoDB encryption at rest
   - Implement proper IAM roles and policies

3. **Application Security**:
   - Keep dependencies updated
   - Use secure image handling
   - Implement input validation

## Cost Optimization

1. **EC2 Instance Types**:
   - Use spot instances for non-critical workloads
   - Right-size instances based on usage
   - Consider auto-scaling groups

2. **Storage**:
   - Use S3 lifecycle policies
   - Implement data retention policies
   - Monitor storage usage

3. **DynamoDB**:
   - Use on-demand billing for variable workloads
   - Implement auto-scaling for predictable workloads
   - Monitor read/write capacity

## Support

For issues and questions:
1. Check the logs in CloudWatch
2. Review the troubleshooting section
3. Open an issue in the GitHub repository
4. Contact the development team

## References

- [MaskTerial GitHub Repository](https://github.com/Jaluus/MaskTerial)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
