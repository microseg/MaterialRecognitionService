#!/usr/bin/env python3
"""
Comprehensive test script for MaskTerial environment
Tests dependencies, imports, model loading, and basic functionality
"""

import os
import sys
import subprocess
import tempfile
import json
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print(f"{'-'*40}")

def test_python_environment():
    """Test Python environment and version"""
    print_section("Python Environment")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    return True

def test_system_dependencies():
    """Test system dependencies"""
    print_section("System Dependencies")
    
    dependencies = [
        ('git', '--version'),
        ('wget', '--version'),
        ('unzip', '-v'),
        ('docker', '--version'),
        ('docker-compose', '--version')
    ]
    
    all_available = True
    for dep, version_flag in dependencies:
        try:
            result = subprocess.run([dep, version_flag], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"✅ {dep}: {version}")
            else:
                print(f"❌ {dep}: Not available")
                all_available = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {dep}: Not found")
            all_available = False
    
    return all_available

def test_python_dependencies():
    """Test Python package dependencies"""
    print_section("Python Dependencies")
    
    required_packages = [
        'torch', 'torchvision', 'torchaudio',
        'opencv-python', 'numpy', 'PIL',
        'flask', 'boto3', 'gunicorn',
        'detectron2', 'maskterial'
    ]
    
    all_available = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: Available")
        except ImportError:
            print(f"❌ {package}: Not available")
            all_available = False
    
    return all_available

def test_maskterial_import():
    """Test MaskTerial import and basic functionality"""
    print_section("MaskTerial Import Test")
    
    try:
        import maskterial
        print("✅ MaskTerial module imported successfully")
        
        # Check available classes
        print(f"Available classes: {[item for item in dir(maskterial) if not item.startswith('_')]}")
        
        # Try to find the main class
        if hasattr(maskterial, 'MaskTerial'):
            print("✅ Found MaskTerial class")
            return True, 'MaskTerial'
        else:
            print("⚠️  MaskTerial class not found")
            return False, None
            
    except ImportError as e:
        print(f"❌ Failed to import MaskTerial: {e}")
        return False, None

def test_model_directory():
    """Test model directory and files"""
    print_section("Model Directory Test")
    
    model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
    print(f"Model path: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Model directory does not exist: {model_path}")
        return False
    
    print(f"✅ Model directory exists")
    
    # List files
    try:
        files = os.listdir(model_path)
        print(f"Found {len(files)} files:")
        for file in files:
            file_path = os.path.join(model_path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size:,} bytes)")
            else:
                print(f"  📂 {file}/")
        
        # Check for essential files
        essential_files = ['config.yaml', 'model_final.pth', 'meta_data.json']
        missing_files = []
        for file in essential_files:
            if file not in files:
                missing_files.append(file)
        
        if missing_files:
            print(f"⚠️  Missing essential files: {missing_files}")
            return False
        else:
            print("✅ All essential model files present")
            return True
            
    except Exception as e:
        print(f"❌ Error listing model directory: {e}")
        return False

def test_detector_initialization():
    """Test detector initialization"""
    print_section("Detector Initialization Test")
    
    try:
        import maskterial
        model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
        
        # Try to initialize the detector
        if hasattr(maskterial, 'MaskTerial'):
            detector_class = getattr(maskterial, 'MaskTerial')
            try:
                # Try initialization without model_path first
                detector = detector_class()
                print("✅ MaskTerial detector initialized successfully")
                return True
            except Exception as e:
                print(f"⚠️  Failed to initialize without parameters: {e}")
                try:
                    # Try with model_path as fallback
                    detector = detector_class(model_path=model_path)
                    print("✅ MaskTerial detector initialized with model_path")
                    return True
                except Exception as e2:
                    print(f"❌ Failed to initialize with model_path: {e2}")
                    return False
        else:
            print("❌ MaskTerial class not available")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize detector: {e}")
        return False

def test_basic_detection():
    """Test basic detection functionality"""
    print_section("Basic Detection Test")
    
    try:
        import maskterial
        import cv2
        import numpy as np
        import tempfile
        
        model_path = os.environ.get('MODEL_PATH', '/opt/maskterial/models')
        
        # Create a test image
        test_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        
        # Save test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            cv2.imwrite(f.name, test_image)
            test_image_path = f.name
        
        try:
            # Initialize detector
            detector_class = getattr(maskterial, 'MaskTerial')
            try:
                detector = detector_class()
            except Exception:
                detector = detector_class(model_path=model_path)
            
            # Perform detection
            print("🔍 Performing test detection...")
            start_time = time.time()
            results = detector.detect(test_image_path)
            end_time = time.time()
            
            print(f"✅ Detection completed in {end_time - start_time:.2f} seconds")
            print(f"Results: {results}")
            
            return True
            
        finally:
            # Clean up
            os.unlink(test_image_path)
            
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print_section("Flask Application Test")
    
    try:
        # Import the app
        from maskterial_app import app
        
        # Test basic routes
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test info endpoint
            response = client.get('/info')
            if response.status_code == 200:
                print("✅ Info endpoint working")
                info = response.get_json()
                print(f"Service: {info.get('service', 'Unknown')}")
                print(f"Model available: {info.get('model_available', False)}")
            else:
                print(f"❌ Info endpoint failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_docker_build():
    """Test Docker build process"""
    print_section("Docker Build Test")
    
    try:
        # Check if Dockerfile exists
        dockerfile_path = "Dockerfile"
        if not os.path.exists(dockerfile_path):
            print(f"❌ Dockerfile not found: {dockerfile_path}")
            return False
        
        print(f"✅ Dockerfile found: {dockerfile_path}")
        
        # Test docker build (dry run)
        print("🔧 Testing Docker build...")
        result = subprocess.run([
            'docker', 'build', '--dry-run', '-f', dockerfile_path, '.'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Docker build syntax is valid")
            return True
        else:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker build test timed out")
        return False
    except Exception as e:
        print(f"❌ Docker build test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return results"""
    print_header("MaskTerial Environment Test Suite")
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Python Environment", test_python_environment),
        ("System Dependencies", test_system_dependencies),
        ("Python Dependencies", test_python_dependencies),
        ("MaskTerial Import", test_maskterial_import),
        ("Model Directory", test_model_directory),
        ("Detector Initialization", test_detector_initialization),
        ("Basic Detection", test_basic_detection),
        ("Flask Application", test_flask_app),
        ("Docker Build", test_docker_build)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            test_results[test_name] = False
    
    # Print summary
    print_header("Test Results Summary")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Environment is ready.")
        return True
    else:
        print("💥 Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
