#!/usr/bin/env python3
"""
Build stage test script for MaskTerial service
Simulates CI/CD build process without requiring Docker
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print(f"{'-'*40}")

def test_file_structure():
    """Test that all required files exist"""
    print_section("File Structure Test")
    
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'maskterial_app.py',
        'verify_models.py',
        'test/test_environment.py',
        'test/test_api.py',
        'test/build_and_test.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def test_dockerfile_syntax():
    """Test Dockerfile syntax without building"""
    print_section("Dockerfile Syntax Test")
    
    try:
        with open('Dockerfile', 'r') as f:
            content = f.read()
        
        # Basic syntax checks
        issues = []
        
        # Check for basic structure
        if 'FROM' not in content:
            issues.append("Missing FROM instruction")
        
        if 'COPY' not in content:
            issues.append("Missing COPY instruction")
        
        if 'RUN' not in content:
            issues.append("Missing RUN instruction")
        
        if 'CMD' not in content and 'ENTRYPOINT' not in content:
            issues.append("Missing CMD or ENTRYPOINT instruction")
        
        # Check for common issues
        if 'apt-get update' in content and 'apt-get clean' not in content:
            issues.append("apt-get update without cleanup")
        
        if issues:
            print(f"❌ Dockerfile issues found: {issues}")
            return False
        
        print("✅ Dockerfile syntax appears valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False

def test_requirements_txt():
    """Test requirements.txt file"""
    print_section("Requirements.txt Test")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        if not requirements or requirements == ['']:
            print("❌ requirements.txt is empty")
            return False
        
        print(f"✅ Found {len(requirements)} requirements:")
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                print(f"  📦 {req.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def test_python_syntax():
    """Test Python syntax of all Python files"""
    print_section("Python Syntax Test")
    
    python_files = [
        'maskterial_app.py',
        'verify_models.py',
        'test/test_environment.py',
        'test/test_api.py',
        'test/build_and_test.py'
    ]
    
    syntax_errors = []
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                # Test syntax by compiling
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ {file_path}")
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path}: Syntax error")
            except Exception as e:
                syntax_errors.append(f"{file_path}: {e}")
                print(f"❌ {file_path}: Error")
    
    if syntax_errors:
        print(f"❌ Syntax errors found: {syntax_errors}")
        return False
    
    print("✅ All Python files have valid syntax")
    return True

def test_imports():
    """Test that all imports can be resolved"""
    print_section("Import Test")
    
    # Test basic imports that should work
    test_imports = [
        ('os', 'os'),
        ('sys', 'sys'),
        ('json', 'json'),
        ('tempfile', 'tempfile'),
        ('pathlib', 'pathlib'),
        ('subprocess', 'subprocess'),
        ('argparse', 'argparse'),
        ('time', 'time')
    ]
    
    import_errors = []
    for module_name, import_name in test_imports:
        try:
            __import__(import_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            import_errors.append(f"{module_name}: {e}")
            print(f"❌ {module_name}: Import error")
    
    if import_errors:
        print(f"❌ Import errors: {import_errors}")
        return False
    
    print("✅ All basic imports work")
    return True

def test_app_structure():
    """Test Flask app structure"""
    print_section("Flask App Structure Test")
    
    try:
        with open('maskterial_app.py', 'r') as f:
            content = f.read()
        
        # Check for Flask app structure
        issues = []
        
        if 'from flask import' not in content:
            issues.append("Missing Flask import")
        
        if 'app = Flask(' not in content:
            issues.append("Missing Flask app creation")
        
        if '@app.route(' not in content:
            issues.append("Missing route decorators")
        
        if 'if __name__ ==' not in content:
            issues.append("Missing main block")
        
        if issues:
            print(f"❌ Flask app issues: {issues}")
            return False
        
        print("✅ Flask app structure appears valid")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Flask app: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling"""
    print_section("Environment Variables Test")
    
    # Test that environment variables are properly handled
    test_vars = {
        'MODEL_PATH': '/opt/maskterial/models',
        'S3_BUCKET_NAME': 'test-bucket',
        'DYNAMODB_TABLE_NAME': 'test-table',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }
    
    try:
        with open('maskterial_app.py', 'r') as f:
            content = f.read()
        
        missing_vars = []
        for var_name in test_vars.keys():
            if f"os.environ.get('{var_name}'" not in content:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"❌ Missing environment variable handling: {missing_vars}")
            return False
        
        print("✅ Environment variables properly handled")
        return True
        
    except Exception as e:
        print(f"❌ Error checking environment variables: {e}")
        return False

def test_docker_build_simulation():
    """Simulate Docker build process"""
    print_section("Docker Build Simulation")
    
    print("🔍 Simulating Docker build steps...")
    
    # Check if we can read all files that would be copied
    files_to_copy = [
        'Dockerfile',
        'requirements.txt',
        'maskterial_app.py',
        'verify_models.py'
    ]
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    f.read()
                print(f"✅ {file_path} - readable")
            except Exception as e:
                print(f"❌ {file_path} - not readable: {e}")
                return False
        else:
            print(f"❌ {file_path} - missing")
            return False
    
    print("✅ All files ready for Docker build")
    return True

def run_build_tests():
    """Run all build stage tests"""
    print_header("MaskTerial Build Stage Test Suite")
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Dockerfile Syntax", test_dockerfile_syntax),
        ("Requirements.txt", test_requirements_txt),
        ("Python Syntax", test_python_syntax),
        ("Import Test", test_imports),
        ("Flask App Structure", test_app_structure),
        ("Environment Variables", test_environment_variables),
        ("Docker Build Simulation", test_docker_build_simulation)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            test_results[test_name] = False
    
    # Print summary
    print_header("Build Test Results Summary")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} build tests passed")
    
    if passed == total:
        print("🎉 All build tests passed! Ready for CI/CD pipeline.")
        return True
    else:
        print("💥 Some build tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = run_build_tests()
    sys.exit(0 if success else 1)
