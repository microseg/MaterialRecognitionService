#!/usr/bin/env python3
"""
Test script for Calculator API
Demonstrates how to interact with the calculator API endpoints
"""

import requests
import json

# API base URL - replace with your EC2 instance IP
API_BASE_URL = "http://34.234.208.1:8000"

def test_api_info():
    """Test the main API endpoint"""
    print("🔍 Testing API information...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data['message']}")
            print(f"📊 Version: {data['version']}")
            print(f"🌍 Environment: {data['environment']}")
            return True
        else:
            print(f"❌ Failed to get API info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_health():
    """Test the health endpoint"""
    print("\n🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in health check: {e}")
        return False

def test_get_operations():
    """Test GET-based operations"""
    print("\n🧮 Testing GET operations...")
    
    # Test addition
    try:
        response = requests.get(f"{API_BASE_URL}/add/10/5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Addition: {data['a']} + {data['b']} = {data['result']}")
        else:
            print(f"❌ Addition failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in addition: {e}")
    
    # Test subtraction
    try:
        response = requests.get(f"{API_BASE_URL}/subtract/10/3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Subtraction: {data['a']} - {data['b']} = {data['result']}")
        else:
            print(f"❌ Subtraction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in subtraction: {e}")
    
    # Test multiplication
    try:
        response = requests.get(f"{API_BASE_URL}/multiply/4/7")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multiplication: {data['a']} * {data['b']} = {data['result']}")
        else:
            print(f"❌ Multiplication failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in multiplication: {e}")
    
    # Test division
    try:
        response = requests.get(f"{API_BASE_URL}/divide/15/3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Division: {data['a']} / {data['b']} = {data['result']}")
        else:
            print(f"❌ Division failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in division: {e}")

def test_post_calculations():
    """Test POST-based calculations"""
    print("\n📤 Testing POST calculations...")
    
    # Test addition via POST
    try:
        data = {
            "operation": "add",
            "a": 25,
            "b": 15
        }
        response = requests.post(f"{API_BASE_URL}/calculate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ POST Addition: {result['a']} + {result['b']} = {result['result']}")
        else:
            print(f"❌ POST Addition failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in POST addition: {e}")
    
    # Test multiplication via POST
    try:
        data = {
            "operation": "multiply",
            "a": 6,
            "b": 8
        }
        response = requests.post(f"{API_BASE_URL}/calculate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ POST Multiplication: {result['a']} * {result['b']} = {result['result']}")
        else:
            print(f"❌ POST Multiplication failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in POST multiplication: {e}")

def test_error_handling():
    """Test error handling"""
    print("\n⚠️ Testing error handling...")
    
    # Test division by zero
    try:
        response = requests.get(f"{API_BASE_URL}/divide/10/0")
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Division by zero handled: {data['error']}")
        else:
            print(f"❌ Division by zero not handled properly: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in division by zero test: {e}")
    
    # Test invalid operation
    try:
        data = {
            "operation": "invalid",
            "a": 10,
            "b": 5
        }
        response = requests.post(f"{API_BASE_URL}/calculate", json=data)
        if response.status_code == 400:
            result = response.json()
            print(f"✅ Invalid operation handled: {result['error']}")
        else:
            print(f"❌ Invalid operation not handled properly: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in invalid operation test: {e}")

def main():
    """Main test function"""
    print("🧮 Calculator API Test Suite")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_api_info():
        print("❌ Cannot connect to API. Please check if the service is running.")
        return
    
    if not test_health():
        print("❌ Health check failed. Service may not be healthy.")
        return
    
    # Test operations
    test_get_operations()
    test_post_calculations()
    test_error_handling()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
