# Calculator Application Deployment Guide

## Overview

This guide explains how to deploy the fixed calculator application code to production environment to resolve storage functionality issues.

## Problem Summary

Current production environment issues:
1. **Float Type Error**: DynamoDB doesn't support Float types, needs conversion to Decimal
2. **Permission Issues**: EC2 instance lacks DynamoDB access permissions

## Fixes Applied

### 1. Code Fixes
- ✅ Added `convert_to_decimal()` function
- ✅ Fixed `save_calculation_result()` and `save_error_result()` functions
- ✅ All float values converted to Decimal types

### 2. Permission Fixes
- ✅ Added DynamoDB permissions in EC2 module
- ✅ Allowed EC2 instance to access CustomerImages-Dev table

## Deployment Steps

### Step 1: Verify Local Code
```bash
# Navigate to application directory
cd MaterialRecognitionService/MaterialRecognitionService

# Verify the application code is ready for deployment
# Note: Local testing files have been removed for production deployment
```

### Step 2: Commit Code to GitHub
```bash
# Add modified files
git add app.py

# Commit changes
git commit -m "Fix DynamoDB Float type issue and add Decimal conversion"

# Push to remote repository
git push origin main
```

### Step 3: Deploy CDK Updates
```bash
# Navigate to CDK directory
cd ../MaterialRecognitionServiceCDK

# Deploy EC2 permission updates
cdk deploy --require-approval never
```

### Step 4: Trigger CI/CD Pipeline
After code is pushed to GitHub, the CI/CD pipeline will automatically:
1. Build new Docker image
2. Push to ECR
3. Deploy to EC2 instance

### Step 5: Verify Deployment
```bash
# Test API endpoint
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/divide/10/5

# Expected output should include:
# "storage_status": "saved"
```

## Testing and Verification

### 1. Health Check
```bash
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/health
```

### 2. Storage Test
```bash
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/storage/test
```

### 3. Calculation Test
```bash
# Addition
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/add/10/5

# Division
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/divide/10/5

# Error handling
curl https://vlaxtfau1c.execute-api.us-east-1.amazonaws.com/prod/divide/10/0
```

## Expected Results

After successful deployment, all API calls should return:
```json
{
  "operation": "division",
  "a": 10,
  "b": 5,
  "result": 2.0,
  "storage_status": "saved"
}
```

Instead of the previous:
```json
{
  "a": 10,
  "b": 5,
  "error": "Float types are not supported. Use Decimal types instead.",
  "operation": "division",
  "result": 2.0,
  "storage_status": "failed"
}
```

## Troubleshooting

### 1. If Deployment Fails
- Check GitHub Actions logs
- Verify ECR image was built successfully
- Check EC2 instance logs

### 2. If Permissions Still Have Issues
- Verify CDK deployment was successful
- Check if IAM roles were updated correctly
- Restart EC2 instance to apply new IAM policies

### 3. If Storage Still Fails
- Check application logs for specific error messages
- Verify S3 bucket and DynamoDB table exist
- Confirm environment variables are set correctly

## Monitoring

Monitor the following metrics after deployment:
- API response time
- Storage success rate
- Error rate
- S3 and DynamoDB usage

## Rollback Plan

If deployment issues occur, you can:
1. Rollback to previous GitHub commit
2. Redeploy previous Docker image
3. Restore previous CDK configuration

## Summary

This deployment will resolve:
- ✅ DynamoDB Float type errors
- ✅ EC2 instance permission issues
- ✅ Complete storage workflow

After deployment completion, the calculator application will be able to:
- Execute mathematical operations
- Save results to S3
- Save metadata to DynamoDB
- Provide complete storage status feedback
