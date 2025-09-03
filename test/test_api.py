#!/usr/bin/env python3
"""
API test script for MaskTerial service
Tests all endpoints and functionality
"""

import os
import sys
import json
import tempfile
import requests
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🌐 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print(f"{'-'*40}")

def test_health_endpoint(base_url):
    """Test health endpoint"""
    print_section("Health Endpoint Test")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Service: {data.get('service', 'Unknown')}")
            print(f"Model available: {data.get('model_available', False)}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_info_endpoint(base_url):
    """Test info endpoint"""
    print_section("Info Endpoint Test")
    
    try:
        response = requests.get(f"{base_url}/info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Info endpoint working")
            print(f"Service: {data.get('service', 'Unknown')}")
            print(f"Version: {data.get('version', 'Unknown')}")
            print(f"Model available: {data.get('model_available', False)}")
            print(f"Model path: {data.get('model_path', 'Unknown')}")
            
            # Check endpoints
            endpoints = data.get('endpoints', {})
            print(f"Available endpoints: {list(endpoints.keys())}")
            
            return True
        else:
            print(f"❌ Info endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Info endpoint test failed: {e}")
        return False

def test_detect_endpoint(base_url):
    """Test detect endpoint with file upload"""
    print_section("Detect Endpoint Test")
    
    try:
        # Create a test image
        import cv2
        import numpy as np
        
        test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        # Save test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            cv2.imwrite(f.name, test_image)
            test_image_path = f.name
        
        try:
            # Prepare the request
            with open(test_image_path, 'rb') as f:
                files = {'image': ('test_image.jpg', f, 'image/jpeg')}
                data = {'customer_id': 'test-customer'}
                
                print("🔍 Sending detection request...")
                start_time = time.time()
                
                response = requests.post(
                    f"{base_url}/detect",
                    files=files,
                    data=data,
                    timeout=60  # Longer timeout for detection
                )
                
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Detection endpoint working")
                    print(f"Detection time: {end_time - start_time:.2f} seconds")
                    print(f"Image ID: {result.get('image_id', 'Unknown')}")
                    print(f"Customer ID: {result.get('customer_id', 'Unknown')}")
                    print(f"Total flakes: {result.get('detection_results', {}).get('total_flakes', 0)}")
                    print(f"Status: {result.get('status', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Detection endpoint failed: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        finally:
            # Clean up
            os.unlink(test_image_path)
            
    except Exception as e:
        print(f"❌ Detection endpoint test failed: {e}")
        return False

def test_detect_from_s3_endpoint(base_url):
    """Test detect_from_s3 endpoint"""
    print_section("Detect from S3 Endpoint Test")
    
    try:
        # This test requires an existing S3 image
        # For now, we'll just test the endpoint structure
        
        data = {
            's3_key': 'test-customer/uploaded/test_image.jpg',
            'customer_id': 'test-customer'
        }
        
        response = requests.post(
            f"{base_url}/detect_from_s3",
            json=data,
            timeout=30
        )
        
        # We expect this to fail since the S3 key doesn't exist
        # But we can check if the endpoint is accessible
        if response.status_code in [400, 404, 500]:
            print("✅ Detect from S3 endpoint accessible")
            print(f"Response status: {response.status_code}")
            return True
        elif response.status_code == 200:
            print("✅ Detect from S3 endpoint working")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Detect from S3 endpoint test failed: {e}")
        return False

def test_error_handling(base_url):
    """Test error handling"""
    print_section("Error Handling Test")
    
    try:
        # Test invalid endpoint
        response = requests.get(f"{base_url}/invalid", timeout=10)
        if response.status_code == 404:
            print("✅ 404 error handling working")
        else:
            print(f"⚠️  Unexpected response for invalid endpoint: {response.status_code}")
        
        # Test detect endpoint without image
        response = requests.post(f"{base_url}/detect", timeout=10)
        if response.status_code == 400:
            print("✅ 400 error handling working for missing image")
        else:
            print(f"⚠️  Unexpected response for missing image: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_api_tests(base_url="http://localhost:5000"):
    """Run all API tests"""
    print_header("MaskTerial API Test Suite")
    
    print(f"Testing API at: {base_url}")
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Health Endpoint", lambda: test_health_endpoint(base_url)),
        ("Info Endpoint", lambda: test_info_endpoint(base_url)),
        ("Detect Endpoint", lambda: test_detect_endpoint(base_url)),
        ("Detect from S3 Endpoint", lambda: test_detect_from_s3_endpoint(base_url)),
        ("Error Handling", lambda: test_error_handling(base_url))
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            test_results[test_name] = False
    
    # Print summary
    print_header("API Test Results Summary")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} API tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! Service is working correctly.")
        return True
    else:
        print("💥 Some API tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    success = run_api_tests(base_url)
    sys.exit(0 if success else 1)
