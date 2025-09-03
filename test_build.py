#!/usr/bin/env python3
"""
Simple test script to verify the build process
"""

import os
import sys

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import boto3
        print("✅ Boto3 imported successfully")
    except ImportError as e:
        print(f"❌ Boto3 import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
        print(f"   PyTorch version: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    required_vars = [
        'S3_BUCKET_NAME',
        'DYNAMODB_TABLE_NAME',
        'AWS_DEFAULT_REGION'
    ]
    
    print("\n🔧 Environment Variables:")
    for var in required_vars:
        value = os.environ.get(var, 'NOT_SET')
        if value != 'NOT_SET':
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: {value}")
    
    return True

if __name__ == "__main__":
    print("🧪 Running build verification tests...\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test environment
    env_ok = test_environment()
    
    print(f"\n📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    
    if imports_ok and env_ok:
        print("\n🎉 All tests passed! Build verification successful.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please check the build configuration.")
        sys.exit(1)
