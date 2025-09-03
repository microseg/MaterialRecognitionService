# MaskTerial Test Suite

This directory contains comprehensive tests for the MaskTerial service that can be run both locally and in cloud environments.

## 📁 Test Files

- **`test_environment.py`** - Tests environment setup, dependencies, and MaskTerial functionality
- **`test_api.py`** - Tests API endpoints and service functionality
- **`build_and_test.py`** - Main orchestration script for running all tests

## 🚀 Quick Start

### Local Testing (Full Test Suite)

```bash
# Run complete local test suite
python test/build_and_test.py --mode local

# Run with custom port
python test/build_and_test.py --mode local --port 5002

# Run without cleanup (keep containers for debugging)
python test/build_and_test.py --mode local --no-cleanup
```

### Cloud Testing (Build Only)

```bash
# Test Docker build and environment (for CI/CD)
python test/build_and_test.py --mode cloud
```

### Individual Tests

```bash
# Test environment only
python test/build_and_test.py --mode environment

# Test API only (requires running service)
python test/build_and_test.py --mode api --port 5000

# Test Docker build only
python test/build_and_test.py --mode build --tag my-image
```

## 🧪 Test Components

### Environment Tests (`test_environment.py`)

Tests the following components:

- ✅ **Python Environment** - Version, virtual environment
- ✅ **System Dependencies** - git, wget, unzip, docker, docker-compose
- ✅ **Python Dependencies** - torch, opencv, flask, boto3, detectron2, maskterial
- ✅ **MaskTerial Import** - Module import and class detection
- ✅ **Model Directory** - Model files and structure
- ✅ **Detector Initialization** - MaskTerial detector setup
- ✅ **Basic Detection** - Test detection on sample image
- ✅ **Flask Application** - App import and basic routes
- ✅ **Docker Build** - Dockerfile syntax validation

### API Tests (`test_api.py`)

Tests the following endpoints:

- ✅ **Health Endpoint** (`/health`) - Service health check
- ✅ **Info Endpoint** (`/info`) - Service information
- ✅ **Detect Endpoint** (`/detect`) - Image upload and detection
- ✅ **Detect from S3** (`/detect_from_s3`) - S3-based detection
- ✅ **Error Handling** - Invalid requests and error responses

## 🔧 Test Modes

### Local Mode (`--mode local`)

1. **Setup Environment** - Set test environment variables
2. **Environment Tests** - Run dependency and import tests
3. **Docker Build** - Build test Docker image
4. **Start Service** - Run service in Docker container
5. **API Tests** - Test all API endpoints
6. **Cleanup** - Remove test containers and images

### Cloud Mode (`--mode cloud`)

1. **Setup Environment** - Set test environment variables
2. **Environment Tests** - Run dependency and import tests
3. **Docker Build** - Build test Docker image
4. **Cleanup** - Remove test images

### Individual Modes

- **`environment`** - Run only environment tests
- **`api`** - Run only API tests (requires running service)
- **`build`** - Run only Docker build test

## 📋 Prerequisites

### Local Testing

- Python 3.8+
- Docker and Docker Compose
- Git, wget, unzip
- All Python dependencies installed

### Cloud Testing

- Python 3.8+
- Docker
- All Python dependencies installed

## 🔍 Test Output

The test suite provides detailed output with:

- ✅ **Success indicators** - Green checkmarks for passed tests
- ❌ **Error indicators** - Red X marks for failed tests
- ⚠️ **Warning indicators** - Yellow warnings for non-critical issues
- 📊 **Summary** - Overall test results and statistics

### Example Output

```
================================================================================
🚀 Running Local Tests
================================================================================

📋 Setting up Environment
--------------------------------------------------
✅ Environment variables set for testing

📋 Running Environment Tests
--------------------------------------------------
🔧 Environment tests
Command: python test/test_environment.py
✅ Environment tests completed successfully

📋 Building Docker Image
--------------------------------------------------
🔧 Docker build with tag: maskterial-test
Command: docker build -t maskterial-test .
✅ Docker build with tag: maskterial-test completed successfully

================================================================================
🎉 All Tests Passed!
================================================================================
✅ The MaskTerial service is ready for deployment.
```

## 🛠️ Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Check Docker is running
   - Ensure sufficient disk space
   - Verify Dockerfile syntax

2. **Environment Tests Fail**
   - Install missing dependencies
   - Check Python version compatibility
   - Verify MaskTerial installation

3. **API Tests Fail**
   - Ensure service is running on correct port
   - Check service logs for errors
   - Verify network connectivity

### Debug Mode

```bash
# Run with verbose output and no cleanup
python test/build_and_test.py --mode local --no-cleanup

# Check running containers
docker ps

# Check service logs
docker logs maskterial-test-service

# Manual cleanup
docker stop maskterial-test-service
docker rm maskterial-test-service
docker rmi maskterial-test
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Test MaskTerial Service

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python test/build_and_test.py --mode cloud
```

### AWS CodeBuild Example

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.11
    commands:
      - pip install -r requirements.txt
  
  build:
    commands:
      - python test/build_and_test.py --mode cloud
      - docker build -t $ECR_REPO_URI:$IMAGE_TAG .
```

## 📝 Customization

### Adding New Tests

1. Create new test function in appropriate test file
2. Add test to the test list in `build_and_test.py`
3. Update this README with new test description

### Environment Variables

The test suite uses these environment variables:

- `MODEL_PATH` - Path to MaskTerial models
- `S3_BUCKET_NAME` - S3 bucket for testing
- `DYNAMODB_TABLE_NAME` - DynamoDB table for testing
- `AWS_DEFAULT_REGION` - AWS region for testing

### Custom Test Configuration

```bash
# Custom Docker image tag
python test/build_and_test.py --tag my-custom-tag

# Custom service port
python test/build_and_test.py --port 8080

# Skip cleanup for debugging
python test/build_and_test.py --no-cleanup
```

## 📞 Support

For issues with the test suite:

1. Check the troubleshooting section above
2. Review test output for specific error messages
3. Run individual test modes to isolate issues
4. Check service logs for detailed error information
