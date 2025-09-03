#!/bin/bash
# Test runner script for MaskTerial service
# Can be used in both local and CI/CD environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("python3")
    else
        print_success "Python3 found: $(python3 --version)"
    fi
    
    # Check Docker (for local testing)
    if ! command_exists docker; then
        print_warning "Docker not found - some tests will be skipped"
    else
        print_success "Docker found: $(docker --version)"
    fi
    
    # Check pip
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    else
        print_success "pip3 found"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_warning "requirements.txt not found"
    fi
}

# Function to run environment tests
run_environment_tests() {
    print_status "Running environment tests..."
    
    if python3 test/test_environment.py; then
        print_success "Environment tests passed"
        return 0
    else
        print_error "Environment tests failed"
        return 1
    fi
}

# Function to run Docker build test
run_docker_build_test() {
    if ! command_exists docker; then
        print_warning "Docker not available - skipping Docker build test"
        return 0
    fi
    
    print_status "Running Docker build test..."
    
    # Build test image
    if docker build -t maskterial-test .; then
        print_success "Docker build successful"
        
        # Test the image
        if docker run --rm maskterial-test python verify_models.py; then
            print_success "Docker image verification passed"
            
            # Cleanup
            docker rmi maskterial-test
            return 0
        else
            print_error "Docker image verification failed"
            docker rmi maskterial-test
            return 1
        fi
    else
        print_error "Docker build failed"
        return 1
    fi
}

# Function to run local full test suite
run_local_tests() {
    print_status "Running local test suite..."
    
    if python3 test/build_and_test.py --mode local; then
        print_success "Local test suite passed"
        return 0
    else
        print_error "Local test suite failed"
        return 1
    fi
}

# Function to run cloud tests
run_cloud_tests() {
    print_status "Running cloud test suite..."
    
    if python3 test/build_and_test.py --mode cloud; then
        print_success "Cloud test suite passed"
        return 0
    else
        print_error "Cloud test suite failed"
        return 1
    fi
}

# Function to run API tests
run_api_tests() {
    local base_url=${1:-"http://localhost:5000"}
    print_status "Running API tests against $base_url..."
    
    if python3 test/test_api.py "$base_url"; then
        print_success "API tests passed"
        return 0
    else
        print_error "API tests failed"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [MODE]"
    echo ""
    echo "Modes:"
    echo "  local     - Run complete local test suite (default)"
    echo "  cloud     - Run cloud deployment tests"
    echo "  env       - Run environment tests only"
    echo "  build     - Run Docker build test only"
    echo "  api       - Run API tests only"
    echo ""
    echo "Options:"
    echo "  --api-url URL    - Base URL for API tests (default: http://localhost:5000)"
    echo "  --no-deps        - Skip dependency installation"
    echo "  --help           - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run local tests"
    echo "  $0 cloud              # Run cloud tests"
    echo "  $0 api --api-url http://my-service:5000  # Test remote service"
}

# Main function
main() {
    local mode="local"
    local api_url="http://localhost:5000"
    local skip_deps=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            local|cloud|env|build|api)
                mode="$1"
                shift
                ;;
            --api-url)
                api_url="$2"
                shift 2
                ;;
            --no-deps)
                skip_deps=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_status "Starting MaskTerial test suite in $mode mode"
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Install dependencies (unless skipped)
    if [ "$skip_deps" = false ]; then
        install_dependencies
    fi
    
    # Run tests based on mode
    case $mode in
        local)
            run_local_tests
            ;;
        cloud)
            run_cloud_tests
            ;;
        env)
            run_environment_tests
            ;;
        build)
            run_docker_build_test
            ;;
        api)
            run_api_tests "$api_url"
            ;;
        *)
            print_error "Unknown mode: $mode"
            show_usage
            exit 1
            ;;
    esac
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed!"
    fi
    
    exit $exit_code
}

# Run main function with all arguments
main "$@"
