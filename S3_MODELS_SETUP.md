# MaskTerial Models S3 Setup

This document explains how to set up MaskTerial models in S3 for efficient deployment.

## Overview

Instead of downloading models during Docker build (which makes the image very large), we now:
1. Store models in a dedicated S3 bucket (`matsight-maskterial-models`)
2. Download models at runtime when the container starts
3. Cache models locally for subsequent runs

## Benefits

- **Smaller Docker images**: No large model files in the image
- **Faster builds**: No model download during build process
- **Better versioning**: Models can be updated independently
- **Cost optimization**: Avoid duplicate storage across containers
- **Flexibility**: Easy to switch between different model versions

## Setup Process

### 1. Deploy Infrastructure

First, deploy the CDK stack which creates the models S3 bucket:

```bash
cd MaterialRecognitionServiceCDK
npm install
cdk deploy
```

### 2. Upload Models to S3

Run the upload script to download models from Zenodo and upload them to S3:

```bash
cd MaterialRecognitionService
python upload_models_to_s3.py
```

This script will:
- Download all MaskTerial models from Zenodo
- Extract the model files
- Upload them to the `matsight-maskterial-models` S3 bucket
- Organize them by model type (SEG_M2F_*, CLS_AMM_*)

### 3. Verify Upload

Check that models are uploaded correctly:

```bash
aws s3 ls s3://matsight-maskterial-models/ --recursive
```

You should see files like:
```
SEG_M2F_GrapheneH/config.yaml
SEG_M2F_GrapheneH/model_final.pth
SEG_M2F_GrapheneH/cov.npy
...
CLS_AMM_GrapheneH/config.yaml
CLS_AMM_GrapheneH/model_final.pth
...
```

## Runtime Behavior

When the container starts:

1. **Model Download**: The `download_models_from_s3()` function runs
2. **Check Local Cache**: If models already exist locally, skip download
3. **Download Missing Models**: Download only missing model files from S3
4. **Initialize Detector**: Load models and initialize MaskTerial detector

## Environment Variables

The following environment variables control model behavior:

- `MODELS_S3_BUCKET`: S3 bucket name for models (default: `matsight-maskterial-models`)
- `MODEL_PATH`: Local path for models (default: `/opt/maskterial/models`)
- `AWS_DEFAULT_REGION`: AWS region for S3 access

## Model Structure

Models are organized in S3 as follows:

```
matsight-maskterial-models/
├── SEG_M2F_GrapheneH/
│   ├── config.yaml
│   ├── model_final.pth
│   ├── cov.npy
│   ├── loc.npy
│   ├── meta_data.json
│   └── model.pth
├── SEG_M2F_GrapheneL/
│   └── ...
├── CLS_AMM_GrapheneH/
│   └── ...
└── ...
```

## Troubleshooting

### Models Not Downloading

1. Check S3 bucket permissions:
   ```bash
   aws s3 ls s3://matsight-maskterial-models/
   ```

2. Verify EC2 instance role has S3 read access

3. Check CloudWatch logs for download errors

### Slow Model Loading

1. Consider using larger instance types for faster network
2. Models are cached locally after first download
3. Subsequent container starts will be faster

### Model Version Updates

To update models:

1. Upload new models to S3 with different keys
2. Update the `required_models` list in `maskterial_app.py`
3. Redeploy the application

## Cost Considerations

- **S3 Storage**: ~2GB for all models
- **S3 Transfer**: One-time cost per container instance
- **Network**: Data transfer from S3 to EC2

## Security

- Models bucket is private by default
- EC2 instances have read-only access via IAM roles
- No public access to model files
- Models are encrypted at rest in S3
