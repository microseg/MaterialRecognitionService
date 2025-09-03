#!/usr/bin/env python3
"""
Main build and test script for MaskTerial service
Orchestrates the entire testing process for both local and cloud environments
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*80}")
    print(f"🚀 {title}")
    print(f"{'='*80}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print(f"{'-'*50}")

def run_command(command, description, check=True, timeout=300):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def setup_environment():
    """Setup the testing environment"""
    print_section("Setting up Environment")
    
    # Set environment variables for testing
    os.environ['MODEL_PATH'] = '/opt/maskterial/models'
    os.environ['S3_BUCKET_NAME'] = 'test-bucket'
    os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    print("✅ Environment variables set for testing")
    return True

def run_environment_tests():
    """Run environment tests"""
    print_section("Running Environment Tests")
    
    return run_command(
        "python test/test_environment.py",
        "Environment tests"
    )

def build_docker_image(tag="maskterial-test"):
    """Build Docker image"""
    print_section("Building Docker Image")
    
    # Build the image
    build_success = run_command(
        f"docker build -t {tag} .",
        f"Docker build with tag: {tag}",
        timeout=600  # 10 minutes for build
    )
    
    if not build_success:
        return False
    
    # Test the image
    test_success = run_command(
        f"docker run --rm {tag} python verify_models.py",
        "Docker image verification test"
    )
    
    return test_success

def start_test_service(tag="maskterial-test", port=5001):
    """Start the service in Docker for testing"""
    print_section("Starting Test Service")
    
    # Stop any existing container
    run_command(
        f"docker stop maskterial-test-service 2>/dev/null || true",
        "Stopping existing test service",
        check=False
    )
    
    # Start the service
    start_success = run_command(
        f"docker run -d --name maskterial-test-service -p {port}:5000 {tag}",
        f"Starting test service on port {port}",
        timeout=30
    )
    
    if not start_success:
        return False
    
    # Wait for service to start
    print("⏳ Waiting for service to start...")
    time.sleep(10)
    
    return True

def run_api_tests(port=5001):
    """Run API tests against the running service"""
    print_section("Running API Tests")
    
    base_url = f"http://localhost:{port}"
    
    return run_command(
        f"python test/test_api.py {base_url}",
        f"API tests against {base_url}"
    )

def stop_test_service():
    """Stop the test service"""
    print_section("Stopping Test Service")
    
    run_command(
        "docker stop maskterial-test-service",
        "Stopping test service",
        check=False
    )
    
    run_command(
        "docker rm maskterial-test-service",
        "Removing test service container",
        check=False
    )

def cleanup():
    """Cleanup test resources"""
    print_section("Cleanup")
    
    # Stop and remove test service
    stop_test_service()
    
    # Remove test image
    run_command(
        "docker rmi maskterial-test",
        "Removing test image",
        check=False
    )
    
    print("✅ Cleanup completed")

def run_local_tests():
    """Run all tests locally"""
    print_header("Running Local Tests")
    
    success = True
    
    # Setup environment
    if not setup_environment():
        success = False
    
    # Run environment tests
    if not run_environment_tests():
        print("⚠️  Environment tests failed, but continuing...")
    
    # Build Docker image
    if not build_docker_image():
        success = False
    
    # Start test service
    if not start_test_service():
        success = False
    
    # Run API tests
    if not run_api_tests():
        success = False
    
    # Cleanup
    cleanup()
    
    return success

def run_cloud_tests():
    """Run tests for cloud deployment"""
    print_header("Running Cloud Tests")
    
    success = True
    
    # Setup environment
    if not setup_environment():
        success = False
    
    # Run environment tests (without Docker)
    if not run_environment_tests():
        success = False
    
    # Test Docker build only
    if not build_docker_image():
        success = False
    
    # Cleanup
    cleanup()
    
    return success

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MaskTerial Build and Test Suite")
    parser.add_argument(
        '--mode',
        choices=['local', 'cloud', 'environment', 'api', 'build'],
        default='local',
        help='Test mode (default: local)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Port for test service (default: 5001)'
    )
    parser.add_argument(
        '--tag',
        default='maskterial-test',
        help='Docker image tag (default: maskterial-test)'
    )
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='Skip cleanup after tests'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'local':
            success = run_local_tests()
        elif args.mode == 'cloud':
            success = run_cloud_tests()
        elif args.mode == 'environment':
            success = run_environment_tests()
        elif args.mode == 'api':
            success = run_api_tests(args.port)
        elif args.mode == 'build':
            success = build_docker_image(args.tag)
        
        if not args.no_cleanup and args.mode in ['local', 'cloud']:
            cleanup()
        
        if success:
            print_header("🎉 All Tests Passed!")
            print("✅ The MaskTerial service is ready for deployment.")
            sys.exit(0)
        else:
            print_header("💥 Tests Failed")
            print("❌ Please fix the issues above before deploying.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        if not args.no_cleanup:
            cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if not args.no_cleanup:
            cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
