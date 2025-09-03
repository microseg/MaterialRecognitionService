#!/usr/bin/env python3
"""
Simple Calculator API Service with Storage Testing
A Flask-based calculator API for testing CI/CD pipeline workflow and AWS storage
"""

from flask import Flask, request, jsonify
import os
import json
import uuid
import subprocess
import sys
from datetime import datetime, timedelta
from decimal import Decimal

app = Flask(__name__)

def install_boto3():
    """Attempt to install boto3 if not available"""
    try:
        import boto3
        return True, "boto3 already available"
    except ImportError:
        try:
            print("boto3 not found, attempting to install...")
            
            # Simplified installation method, prioritize system-level installation
            installation_methods = [
                # Method 1: System installation with sudo
                ["sudo", sys.executable, "-m", "pip", "install", "boto3==1.34.0"],
                # Method 2: Direct pip3 system installation
                ["sudo", "pip3", "install", "boto3==1.34.0"],
                # Method 3: User installation as fallback
                [sys.executable, "-m", "pip", "install", "--user", "boto3==1.34.0"],
            ]
            
            for i, method in enumerate(installation_methods, 1):
                try:
                    print(f"Trying installation method {i}: {' '.join(method)}")
                    result = subprocess.run(method, capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        print(f"Installation method {i} succeeded")
                        # Verify installation
                        try:
                            import boto3
                            print(f"boto3 version: {boto3.__version__}")
                            return True, f"boto3 installed successfully using method {i}"
                        except Exception as e:
                            print(f"boto3 import failed after installation: {e}")
                            continue
                    else:
                        print(f"Installation method {i} failed: {result.stderr}")
                except Exception as e:
                    print(f"Installation method {i} exception: {e}")
                    continue
            
            return False, "All installation methods failed"
            
        except Exception as e:
            error_msg = f"Exception during boto3 installation: {str(e)}"
            print(error_msg)
            return False, error_msg

# Initialize storage variables
BOTO3_AVAILABLE = False
s3_client = None
dynamodb = None
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "matsight-customer-images-dev")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "CustomerImages-Dev")

# Try to import boto3, and install if not available
try:
    import boto3
    BOTO3_AVAILABLE = True
    print(f"boto3 imported successfully, version: {boto3.__version__}")
except ImportError:
    print("boto3 not available, attempting automatic installation...")
    try:
        success, message = install_boto3()
        if success:
            try:
                import boto3
                BOTO3_AVAILABLE = True
                print(f"boto3 installed and imported successfully, version: {boto3.__version__}")
            except Exception as e:
                print(f"Failed to import boto3 after installation: {e}")
                BOTO3_AVAILABLE = False
        else:
            print(f"Failed to install boto3: {message}")
            BOTO3_AVAILABLE = False
    except Exception as e:
        print(f"Exception during boto3 installation process: {e}")
        BOTO3_AVAILABLE = False

# Initialize AWS clients if boto3 is available
if BOTO3_AVAILABLE:
    try:
        # Set AWS region
        aws_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        print(f"Initializing AWS clients in region: {aws_region}")
        
        s3_client = boto3.client("s3", region_name=aws_region)
        dynamodb = boto3.resource("dynamodb", region_name=aws_region)
        print("AWS clients initialized successfully")
        
        # Test connection
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            print(f"S3 bucket {BUCKET_NAME} is accessible")
        except Exception as e:
            print(f"S3 bucket {BUCKET_NAME} not accessible: {e}")
            
        try:
            table = dynamodb.Table(TABLE_NAME)
            table.table_status
            print(f"DynamoDB table {TABLE_NAME} is accessible")
        except Exception as e:
            print(f"DynamoDB table {TABLE_NAME} not accessible: {e}")
            
    except Exception as e:
        print(f"Failed to initialize AWS clients: {e}")
        BOTO3_AVAILABLE = False
else:
    print("Storage features will be disabled due to boto3 unavailability")

@app.route("/")
def hello():
    return "Material Recognition Service Calculator with Storage Testing!"

@app.route("/simple-test")
def simple_test():
    """Simple test endpoint that doesn't depend on boto3"""
    return {
        "status": "success",
        "message": "Application is running",
        "boto3_available": BOTO3_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }, 200

@app.route("/health")
def health():
    storage_status = "available" if BOTO3_AVAILABLE else "unavailable"
    
    # Add detailed diagnostic information
    diagnostic_info = {
        "boto3_available": BOTO3_AVAILABLE,
        "s3_client_initialized": s3_client is not None,
        "dynamodb_initialized": dynamodb is not None,
        "bucket_name": BUCKET_NAME,
        "table_name": TABLE_NAME,
        "aws_region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    }
    
    # If boto3 is available, test connection
    if BOTO3_AVAILABLE:
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            diagnostic_info["s3_accessible"] = True
        except Exception as e:
            diagnostic_info["s3_accessible"] = False
            diagnostic_info["s3_error"] = str(e)
            
        try:
            table = dynamodb.Table(TABLE_NAME)
            table.table_status
            diagnostic_info["dynamodb_accessible"] = True
        except Exception as e:
            diagnostic_info["dynamodb_accessible"] = False
            diagnostic_info["dynamodb_error"] = str(e)
    
    return {
        "status": "healthy", 
        "service": "Material Recognition Service",
        "storage": storage_status,
        "diagnostic": diagnostic_info
    }, 200

@app.route("/add/<int:a>/<int:b>")
def add(a, b):
    result = a + b
    try:
        if BOTO3_AVAILABLE:
            save_calculation_result("addition", a, b, result)
            return {"operation": "addition", "a": a, "b": b, "result": result, "storage_status": "saved"}, 200
        else:
            return {"operation": "addition", "a": a, "b": b, "result": result, "storage_status": "unavailable"}, 200
    except Exception as e:
        return {"operation": "addition", "a": a, "b": b, "result": result, "storage_status": "failed", "error": str(e)}, 200

@app.route("/subtract/<int:a>/<int:b>")
def subtract(a, b):
    result = a - b
    try:
        if BOTO3_AVAILABLE:
            save_calculation_result("subtraction", a, b, result)
            return {"operation": "subtraction", "a": a, "b": b, "result": result, "storage_status": "saved"}, 200
        else:
            return {"operation": "subtraction", "a": a, "b": b, "result": result, "storage_status": "unavailable"}, 200
    except Exception as e:
        return {"operation": "subtraction", "a": a, "b": b, "result": result, "storage_status": "failed", "error": str(e)}, 200

@app.route("/multiply/<int:a>/<int:b>")
def multiply(a, b):
    result = a * b
    try:
        if BOTO3_AVAILABLE:
            save_calculation_result("multiplication", a, b, result)
            return {"operation": "multiplication", "a": a, "b": b, "result": result, "storage_status": "saved"}, 200
        else:
            return {"operation": "multiplication", "a": a, "b": b, "result": result, "storage_status": "unavailable"}, 200
    except Exception as e:
        return {"operation": "multiplication", "a": a, "b": b, "result": result, "storage_status": "failed", "error": str(e)}, 200

@app.route("/divide/<int:a>/<int:b>")
def divide(a, b):
    if b == 0:
        try:
            if BOTO3_AVAILABLE:
                save_error_result("division", a, b, "Division by zero error")
                return {"error": "you cannot divide by zero", "storage_status": "saved"}, 400
            else:
                return {"error": "you cannot divide by zero", "storage_status": "unavailable"}, 400
        except Exception as e:
            return {"error": "you cannot divide by zero", "storage_status": "failed", "error": str(e)}, 400
    
    result = a / b
    try:
        if BOTO3_AVAILABLE:
            save_calculation_result("division", a, b, result)
            return {"operation": "division", "a": a, "b": b, "result": result, "storage_status": "saved"}, 200
        else:
            return {"operation": "division", "a": a, "b": b, "result": result, "storage_status": "unavailable"}, 200
    except Exception as e:
        return {"operation": "division", "a": a, "b": b, "result": result, "storage_status": "failed", "error": str(e)}, 200

@app.route("/storage/test")
def test_storage():
    if not BOTO3_AVAILABLE:
        return {"status": "error", "message": "boto3 not available"}, 500
    
    try:
        # Test S3
        test_s3_connection()
        # Test DynamoDB
        test_dynamodb_connection()
        return {"status": "success", "message": "Storage connections working"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/storage/s3/test")
def test_s3():
    if not BOTO3_AVAILABLE:
        return {"status": "error", "message": "boto3 not available"}, 500
    
    try:
        test_s3_connection()
        return {"status": "success", "message": "S3 connection working"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/storage/dynamodb/test")
def test_dynamodb():
    if not BOTO3_AVAILABLE:
        return {"status": "error", "message": "boto3 not available"}, 500
    
    try:
        test_dynamodb_connection()
        return {"status": "success", "message": "DynamoDB connection working"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/storage/save-test")
def save_test_data():
    if not BOTO3_AVAILABLE:
        return {"status": "error", "message": "boto3 not available"}, 500
    
    try:
        # Save test data to S3
        test_key = f"test/data-{uuid.uuid4()}.json"
        test_data = {"timestamp": datetime.now().isoformat(), "test": True}
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=test_key,
            Body=json.dumps(test_data),
            ContentType="application/json"
        )

        # Save test data to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        test_item = {
            "customerID": "test-customer",
            "imageID": f"test-{uuid.uuid4()}",
            "createdAt": int(datetime.now().timestamp()),
            "type": "TEST",
            "s3Key": test_key,
            "thumbnailKey": test_key,
            "status": "active",
            "expiresAt": int((datetime.now() + timedelta(days=30)).timestamp())
        }
        table.put_item(Item=test_item)
        
        return {
            "status": "success",
            "s3_key": test_key,
            "dynamodb_item": test_item
        }, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/diagnose")
def diagnose():
    """Detailed diagnostic endpoint for checking boto3 and AWS connection status"""
    import sys
    import subprocess
    
    diagnosis = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "python_path": sys.path,
        "environment_variables": {
            "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
            "AWS_ACCESS_KEY_ID": "***" if os.environ.get("AWS_ACCESS_KEY_ID") else None,
            "AWS_SECRET_ACCESS_KEY": "***" if os.environ.get("AWS_SECRET_ACCESS_KEY") else None,
            "S3_BUCKET_NAME": BUCKET_NAME,
            "DYNAMODB_TABLE_NAME": TABLE_NAME
        },
        "boto3_status": {
            "available": BOTO3_AVAILABLE,
            "version": None,
            "location": None
        },
        "aws_clients": {
            "s3_client": s3_client is not None,
            "dynamodb_resource": dynamodb is not None
        },
        "connection_tests": {}
    }
    
    # Check boto3 detailed information
    if BOTO3_AVAILABLE:
        try:
            diagnosis["boto3_status"]["version"] = boto3.__version__
            diagnosis["boto3_status"]["location"] = boto3.__file__
        except Exception as e:
            diagnosis["boto3_status"]["error"] = str(e)
    
    # Test AWS connection
    if BOTO3_AVAILABLE:
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            diagnosis["connection_tests"]["s3"] = "success"
        except Exception as e:
            diagnosis["connection_tests"]["s3"] = f"failed: {str(e)}"
            
        try:
            table = dynamodb.Table(TABLE_NAME)
            table.table_status
            diagnosis["connection_tests"]["dynamodb"] = "success"
        except Exception as e:
            diagnosis["connection_tests"]["dynamodb"] = f"failed: {str(e)}"
    
    # Check pip installed packages
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            diagnosis["installed_packages"] = result.stdout
        else:
            diagnosis["installed_packages"] = f"Error: {result.stderr}"
    except Exception as e:
        diagnosis["installed_packages"] = f"Exception: {str(e)}"
    
    return diagnosis, 200

@app.route("/info")
def info():
    return {
        "service": "Material Recognition Service Calculator with Storage",
        "version": "1.0.0",
        "storage": {
            "available": BOTO3_AVAILABLE,
            "s3_bucket": BUCKET_NAME if BOTO3_AVAILABLE else "N/A",
            "dynamodb_table": TABLE_NAME if BOTO3_AVAILABLE else "N/A"
        },
        "endpoints": {
            "health": "/health",
            "diagnose": "/diagnose",
            "add": "/add/{a}/{b}",
            "subtract": "/subtract/{a}/{b}",
            "multiply": "/multiply/{a}/{b}",
            "divide": "/divide/{a}/{b}",
            "calculate": "/calculate (POST)",
            "storage_test": "/storage/test",
            "storage_s3_test": "/storage/s3/test",
            "storage_dynamodb_test": "/storage/dynamodb/test",
            "storage_save_test": "/storage/save-test",
            "info": "/info"
        },
        "example_usage": {
            "GET": "/add/10/5",
            "POST": "/calculate with JSON: {\"operation\": \"add\", \"a\": 10, \"b\": 5}",
            "storage_test": "/storage/test",
            "diagnose": "/diagnose",
            "divide_test": "/divide/10/0 (will save error to storage)"
        }
    }, 200

def convert_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_decimal(item) for item in obj]
    else:
        return obj

def save_calculation_result(operation, a, b, result):
    """Save calculation result to storage with enhanced metadata"""
    if not BOTO3_AVAILABLE:
        return
    
    calculation_id = f"calc-{uuid.uuid4()}"
    calculation_data = {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }

    # Save to S3
    s3_key = f"calculations/{calculation_id}.json"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(calculation_data),
        ContentType="application/json"
    )

    # Save to DynamoDB with enhanced metadata structure
    table = dynamodb.Table(TABLE_NAME)
    metadata = {
        "operation": operation,
        "operand_a": a,
        "operand_b": b,
        "result": result,
        "uploadSource": "api",
        "originalFilename": f"{operation}_calculation.json"
    }
    
    # Convert metadata to use Decimal for float values
    metadata = convert_to_decimal(metadata)
    
    item = {
        "customerID": "calculator-user",
        "imageID": calculation_id,
        "createdAt": int(datetime.now().timestamp()),
        "type": "CALCULATION",
        "s3Key": s3_key,
        "thumbnailKey": s3_key,
        "status": "active",
        "materialType": "calculation",
        "imageSize": len(json.dumps(calculation_data)),
        "imageFormat": "json",
        "processingStatus": "completed",
        "metadata": metadata,
        "expiresAt": int((datetime.now() + timedelta(days=30)).timestamp())
    }
    table.put_item(Item=item)

def save_error_result(operation, a, b, error_message):
    """Save error result to storage with enhanced metadata"""
    if not BOTO3_AVAILABLE:
        return
    
    error_id = f"error-{uuid.uuid4()}"
    error_data = {
        "operation": operation,
        "a": a,
        "b": b,
        "error": error_message,
        "timestamp": datetime.now().isoformat()
    }

    # Save to S3
    s3_key = f"errors/{error_id}.json"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(error_data),
        ContentType="application/json"
    )

    # Save to DynamoDB with enhanced metadata structure
    table = dynamodb.Table(TABLE_NAME)
    metadata = {
        "operation": operation,
        "operand_a": a,
        "operand_b": b,
        "error": error_message,
        "uploadSource": "api",
        "originalFilename": f"{operation}_error.json"
    }
    
    # Convert metadata to use Decimal for float values
    metadata = convert_to_decimal(metadata)
    
    item = {
        "customerID": "calculator-user",
        "imageID": error_id,
        "createdAt": int(datetime.now().timestamp()),
        "type": "ERROR",
        "s3Key": s3_key,
        "thumbnailKey": s3_key,
        "status": "active",
        "materialType": "error",
        "imageSize": len(json.dumps(error_data)),
        "imageFormat": "json",
        "processingStatus": "completed",
        "metadata": metadata,
        "expiresAt": int((datetime.now() + timedelta(days=30)).timestamp())
    }
    table.put_item(Item=item)

def test_s3_connection():
    """Test S3 connection"""
    if not BOTO3_AVAILABLE:
        raise Exception("boto3 not available")
    s3_client.head_bucket(Bucket=BUCKET_NAME)

def test_dynamodb_connection():
    """Test DynamoDB connection"""
    if not BOTO3_AVAILABLE:
        raise Exception("boto3 not available")
    table = dynamodb.Table(TABLE_NAME)
    table.table_status

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
 