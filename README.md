# Material Recognition Service with MaskTerial

A comprehensive AWS-based service for 2D material flake detection using the MaskTerial deep learning model. This service provides a complete pipeline for processing microscopy images, detecting 2D materials, and storing results in AWS S3 and DynamoDB.

## Features

- **MaskTerial Integration**: Uses the state-of-the-art MaskTerial model for 2D material detection
- **AWS Integration**: Seamless integration with S3 for image storage and DynamoDB for metadata
- **RESTful API**: Flask-based API with endpoints for image upload and S3-based processing
- **Docker Support**: Containerized deployment with GPU support
- **CI/CD Pipeline**: Automated deployment using AWS CDK
- **Monitoring**: CloudWatch integration for logging and monitoring
- **Scalable Architecture**: Designed for high availability and scalability

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

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Node.js (v16+)
- Docker (for local testing)
- Python 3.8+

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MaterialRecognitionService
   ```

2. **Set up environment variables**:
   ```bash
   export S3_BUCKET_NAME=your-s3-bucket-name
   export DYNAMODB_TABLE_NAME=your-dynamodb-table-name
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.maskterial.yml up --build
   ```

4. **Test the service**:
   ```bash
   python test_maskterial.py
   ```

### AWS Deployment

1. **Deploy infrastructure**:
   ```bash
   cd MaterialRecognitionServiceCDK
   npm install
   cdk deploy
   ```

2. **Configure EC2 instance**:
   ```bash
   # Create SSH key pair
   aws ec2 create-key-pair --key-name maskterial-key --query 'KeyMaterial' --output text > maskterial-key.pem
   chmod 400 maskterial-key.pem
   
   # SSH into instance
   ssh -i maskterial-key.pem ec2-user@<EC2_PUBLIC_IP>
   ```

3. **Verify deployment**:
   ```bash
   curl http://localhost:5000/health
   ```

## API Endpoints

### Health Check
```http
GET /health
```

### Service Information
```http
GET /info
```

### Detect from Uploaded Image
```http
POST /detect
Content-Type: multipart/form-data

Parameters:
- image: Image file
- customer_id: Customer identifier (optional)
```

### Detect from S3
```http
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

## MaskTerial Model

This service integrates the [MaskTerial](https://github.com/Jaluus/MaskTerial) model, which is a foundation model for automated 2D material flake detection. The model provides:

- **Robust Detection**: Less sensitive to camera noise and brightness differences
- **Interpretable Results**: Uses well-understood features from literature
- **Backwards Compatibility**: Can use previous GMM models if needed
- **Open Source**: Fully open-source under MIT license
- **Pretrained Weights**: Available for immediate use with minimal fine-tuning

### Model Features

- Detects multiple 2D materials (graphene, hBN, MoS2, WS2, etc.)
- Provides confidence scores and bounding boxes
- Handles low-contrast materials effectively
- Requires minimal training data (5-10 images) for new materials

## Development

### Project Structure

```
MaterialRecognitionService/
├── MaterialRecognitionService/
│   ├── app.py                 # Original calculator service
│   ├── maskterial_app.py      # MaskTerial API service
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile.maskterial  # Docker configuration
│   ├── test_maskterial.py     # Test script
│   └── docker-compose.maskterial.yml
├── MaterialRecognitionServiceCDK/
│   ├── lib/
│   │   ├── stack.ts           # Main CDK stack
│   │   └── modules/
│   │       ├── storage/       # S3 and DynamoDB modules
│   │       └── maskterial-module.ts
│   └── package.json
└── docs/
```

### Adding New Features

1. **New API Endpoints**: Add to `maskterial_app.py`
2. **Infrastructure Changes**: Modify CDK modules in `lib/modules/`
3. **Model Updates**: Update Dockerfile and requirements.txt
4. **Testing**: Add tests to `test_maskterial.py`

## Monitoring and Logging

### CloudWatch Integration

- Application logs: `/aws/ec2/maskterial/app`
- Docker logs: `/aws/ec2/maskterial/docker`
- Health checks: Every 30 seconds
- Cron monitoring: Every 5 minutes

### Health Checks

```bash
# Application health
curl http://localhost:5000/health

# Docker health
docker ps
docker logs <container_id>
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**:
   - Check GPU drivers and CUDA installation
   - Verify model files are in correct location
   - Check MaskTerial installation

2. **AWS Connectivity**:
   - Verify IAM roles and policies
   - Check security group configurations
   - Ensure correct region settings

3. **Performance Issues**:
   - Monitor EC2 instance resources
   - Check GPU utilization
   - Review CloudWatch metrics

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

## Security

### Best Practices

1. **Network Security**:
   - Use security groups to restrict access
   - Enable SSL/TLS for API communication
   - Consider VPC endpoints for AWS services

2. **Data Security**:
   - Enable S3 bucket encryption
   - Use DynamoDB encryption at rest
   - Implement proper IAM roles

3. **Application Security**:
   - Keep dependencies updated
   - Validate all inputs
   - Use secure image handling

## Cost Optimization

### Recommendations

1. **EC2 Instances**:
   - Use spot instances for non-critical workloads
   - Right-size based on usage patterns
   - Implement auto-scaling

2. **Storage**:
   - Use S3 lifecycle policies
   - Implement data retention
   - Monitor storage usage

3. **DynamoDB**:
   - Use on-demand billing for variable workloads
   - Implement auto-scaling
   - Monitor capacity usage

## Support

For issues and questions:

1. Check the [deployment guide](MASKTERIAL_DEPLOYMENT_GUIDE.md)
2. Review CloudWatch logs
3. Open an issue in the repository
4. Contact the development team

## References

- [MaskTerial Paper](https://arxiv.org/abs/2412.09333)
- [MaskTerial GitHub](https://github.com/Jaluus/MaskTerial)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.