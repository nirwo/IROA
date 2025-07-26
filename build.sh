#!/bin/bash

# IROA Docker Build Script
# This script builds all Docker containers for the IROA system

set -e  # Exit on any error

echo "🏗️  Building IROA Docker Containers..."
echo "======================================"

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

# Create Dockerfile for API if it doesn't exist
create_api_dockerfile() {
    if [ ! -f "Dockerfile.api" ]; then
        print_status "Creating API Dockerfile..."
        cat > Dockerfile.api << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY monitoring/ ./monitoring/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
EOF
        print_success "API Dockerfile created"
    fi
}

# Create requirements.txt if it doesn't exist
create_requirements() {
    if [ ! -f "requirements.txt" ]; then
        print_status "Creating requirements.txt..."
        cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
psutil==5.9.6
requests==2.31.0
python-multipart==0.0.6
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
prometheus-client==0.19.0
pyVmomi==8.0.2.0.1
pyzabbix==1.3.0
EOF
        print_success "requirements.txt created"
    fi
}

# Build API container
build_api_container() {
    print_status "Building IROA API container..."
    
    create_api_dockerfile
    create_requirements
    
    docker build -t iroa-api -f Dockerfile.api . || {
        print_error "Failed to build API container"
        exit 1
    }
    
    print_success "IROA API container built successfully"
}

# Create Prometheus Dockerfile
create_prometheus_dockerfile() {
    mkdir -p monitoring
    if [ ! -f "monitoring/Dockerfile.prometheus" ]; then
        print_status "Creating Prometheus Dockerfile..."
        cat > monitoring/Dockerfile.prometheus << 'EOF'
FROM prom/prometheus:latest

# Copy custom configuration
COPY prometheus.yml /etc/prometheus/prometheus.yml

# Expose port
EXPOSE 9090

# Start Prometheus
CMD ["--config.file=/etc/prometheus/prometheus.yml", \
     "--storage.tsdb.path=/prometheus", \
     "--web.console.libraries=/etc/prometheus/console_libraries", \
     "--web.console.templates=/etc/prometheus/consoles", \
     "--web.enable-lifecycle"]
EOF
        print_success "Prometheus Dockerfile created"
    fi
}

# Build Prometheus container
build_prometheus_container() {
    print_status "Building Prometheus container..."
    
    create_prometheus_dockerfile
    
    if [ -f "monitoring/prometheus.yml" ]; then
        docker build -t iroa-prometheus -f monitoring/Dockerfile.prometheus monitoring/ || {
            print_warning "Failed to build Prometheus container (optional)"
            return 0
        }
        print_success "Prometheus container built successfully"
    else
        print_warning "prometheus.yml not found, skipping Prometheus build"
    fi
}

# Clean old images if requested
clean_old_images() {
    if [[ "$1" == "--clean" ]] || [[ "$1" == "-c" ]]; then
        print_status "Cleaning old Docker images..."
        
        # Remove old IROA images
        docker rmi iroa-api iroa-prometheus 2>/dev/null || true
        
        # Clean up dangling images
        docker image prune -f
        
        print_success "Old images cleaned"
    fi
}

# Show build summary
show_summary() {
    echo ""
    echo "📋 Build Summary"
    echo "================"
    
    # Check API image
    if docker images | grep -q iroa-api; then
        API_SIZE=$(docker images iroa-api --format "table {{.Size}}" | tail -n 1)
        echo "✅ IROA API: $API_SIZE"
    else
        echo "❌ IROA API: Failed to build"
    fi
    
    # Check Prometheus image
    if docker images | grep -q iroa-prometheus; then
        PROM_SIZE=$(docker images iroa-prometheus --format "table {{.Size}}" | tail -n 1)
        echo "✅ Prometheus: $PROM_SIZE"
    else
        echo "⚠️  Prometheus: Not built"
    fi
    
    echo ""
    echo "🚀 To start the system: ./start.sh"
    echo "🔧 To build and start: ./start.sh --build"
}

# Main execution
main() {
    echo "🐳 IROA Docker Build Process"
    echo "============================"
    
    check_docker
    clean_old_images "$1"
    build_api_container
    build_prometheus_container
    show_summary
    
    echo ""
    echo "🎉 Build Complete!"
    echo "=================="
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "IROA Docker Build Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --clean, -c    Clean old images before building"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              Build containers"
        echo "  $0 --clean      Clean old images and build"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
