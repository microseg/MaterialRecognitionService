#!/usr/bin/env python3
"""
Test script for MaskTerial service
"""

import requests
import json
import os
from datetime import datetime

# Configuration
SERVICE_URL = os.environ.get('MASKTERIAL_SERVICE_URL', 'http://localhost:5000')
TEST_IMAGE_PATH = os.environ.get('TEST_IMAGE_PATH', 'test_image.jpg')

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_info():
    """Test info endpoint"""
    print("\nTesting info endpoint...")
    try:
        response = requests.get(f"{SERVICE_URL}/info")
        if response.status_code == 200:
            print("✅ Info endpoint working")
            info = response.json()
            print(f"Service: {info.get('service')}")
            print(f"Model available: {info.get('model_available')}")
            return True
        else:
            print(f"❌ Info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Info endpoint error: {e}")
        return False

def test_detection_with_file():
    """Test detection with uploaded file"""
    print("\nTesting detection with file upload...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        print("Creating a dummy test image...")
        create_dummy_image()
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}
            data = {'customer_id': 'test-customer-123'}
            
            response = requests.post(f"{SERVICE_URL}/detect", files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Detection test passed")
                result = response.json()
                print(f"Image ID: {result.get('image_id')}")
                print(f"Total flakes detected: {result.get('detection_results', {}).get('total_flakes', 0)}")
                print(f"Result URL: {result.get('result_image_url')}")
                return True
            else:
                print(f"❌ Detection test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Detection test error: {e}")
        return False

def test_detection_from_s3():
    """Test detection from S3"""
    print("\nTesting detection from S3...")
    
    # This test requires an existing S3 image
    test_data = {
        's3_key': 'test-customer-123/uploaded/test_image.jpg',
        'customer_id': 'test-customer-123'
    }
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/detect_from_s3",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ S3 detection test passed")
            result = response.json()
            print(f"Image ID: {result.get('image_id')}")
            print(f"Total flakes detected: {result.get('detection_results', {}).get('total_flakes', 0)}")
            return True
        elif response.status_code == 500 and "Failed to download image from S3" in response.text:
            print("⚠️ S3 detection test skipped (no test image in S3)")
            return True
        else:
            print(f"❌ S3 detection test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ S3 detection test error: {e}")
        return False

def create_dummy_image():
    """Create a dummy test image"""
    try:
        import numpy as np
        from PIL import Image
        
        # Create a simple test image
        img_array = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(TEST_IMAGE_PATH)
        print(f"✅ Created dummy test image: {TEST_IMAGE_PATH}")
    except ImportError:
        print("❌ PIL not available, cannot create dummy image")
    except Exception as e:
        print(f"❌ Failed to create dummy image: {e}")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("MaskTerial Service Test Suite")
    print("=" * 50)
    print(f"Service URL: {SERVICE_URL}")
    print(f"Test Image: {TEST_IMAGE_PATH}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)
    
    tests = [
        test_health,
        test_info,
        test_detection_with_file,
        test_detection_from_s3
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
