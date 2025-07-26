#!/bin/bash

# IROA System Startup Script
# This script builds Docker containers and starts the frontend

set -e  # Exit on any error

echo "🚀 Starting IROA System..."
echo "=================================="

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

# Check if Docker is running
check_docker() {
    print_status "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Build Docker containers
build_docker() {
    print_status "Building Docker containers..."
    
    # Build API container
    print_status "Building IROA API container..."
    docker build -t iroa-api -f Dockerfile.api . || {
        print_error "Failed to build API container"
        exit 1
    }
    
    # Build Prometheus container if needed
    if [ -f "monitoring/Dockerfile.prometheus" ]; then
        print_status "Building Prometheus container..."
        docker build -t iroa-prometheus -f monitoring/Dockerfile.prometheus monitoring/ || {
            print_warning "Failed to build Prometheus container (optional)"
        }
    fi
    
    print_success "Docker containers built successfully"
}

# Start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    
    # Stop any existing containers
    docker stop iroa-api iroa-prometheus 2>/dev/null || true
    docker rm iroa-api iroa-prometheus 2>/dev/null || true
    
    # Start API container
    print_status "Starting IROA API (port 8001)..."
    docker run -d \
        --name iroa-api \
        -p 8001:8001 \
        -v $(pwd)/config:/app/config \
        -v $(pwd)/data:/app/data \
        iroa-api || {
        print_error "Failed to start API container"
        exit 1
    }
    
    # Start Prometheus if available
    if docker images | grep -q iroa-prometheus; then
        print_status "Starting Prometheus (port 9090)..."
        docker run -d \
            --name iroa-prometheus \
            -p 9090:9090 \
            -v $(pwd)/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
            iroa-prometheus || {
            print_warning "Failed to start Prometheus container (optional)"
        }
    fi
    
    print_success "Docker services started"
}

# Start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Starting simple HTTP server..."
        
        # Use Python HTTP server as fallback
        if command -v python3 &> /dev/null; then
            print_status "Starting Python HTTP server on port 3000..."
            cd dashboard
            python3 -m http.server 3000 > ../logs/frontend.log 2>&1 &
            echo $! > ../frontend.pid
            cd ..
        elif command -v python &> /dev/null; then
            print_status "Starting Python HTTP server on port 3000..."
            cd dashboard
            python -m SimpleHTTPServer 3000 > ../logs/frontend.log 2>&1 &
            echo $! > ../frontend.pid
            cd ..
        else
            print_error "No suitable HTTP server found. Please install Node.js or Python."
            exit 1
        fi
    else
        # Use Node.js HTTP server
        print_status "Starting Node.js HTTP server on port 3000..."
        cd dashboard
        npx http-server -p 3000 -c-1 > ../logs/frontend.log 2>&1 &
        echo $! > ../frontend.pid
        cd ..
    fi
    
    print_success "Frontend server started on http://localhost:3000"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for API
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "API is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "API may not be ready yet"
        fi
        sleep 2
    done
    
    # Wait for frontend
    for i in {1..15}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        if [ $i -eq 15 ]; then
            print_warning "Frontend may not be ready yet"
        fi
        sleep 2
    done
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    mkdir -p logs config data
    print_success "Directories created"
}

# Main execution
main() {
    echo "🏗️  IROA System Deployment"
    echo "=========================="
    
    setup_directories
    check_docker
    
    # Check if --build flag is provided
    if [[ "$1" == "--build" ]] || [[ "$1" == "-b" ]]; then
        build_docker
    fi
    
    start_docker_services
    start_frontend
    wait_for_services
    
    echo ""
    echo "🎉 IROA System Started Successfully!"
    echo "===================================="
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔧 API: http://localhost:8001"
    echo "📈 Prometheus: http://localhost:9090 (if available)"
    echo ""
    echo "📝 Logs:"
    echo "   Frontend: logs/frontend.log"
    echo "   API: docker logs iroa-api"
    echo ""
    echo "🛑 To stop the system, run: ./stop.sh"
    echo ""
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "IROA System Startup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --build, -b    Build Docker containers before starting"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              Start system with existing containers"
        echo "  $0 --build      Build containers and start system"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
