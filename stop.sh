#!/bin/bash

# IROA System Stop Script
# This script stops all IROA services (Docker containers and frontend)

set -e  # Exit on any error

echo "🛑 Stopping IROA System..."
echo "============================"

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

# Stop frontend server
stop_frontend() {
    print_status "Stopping frontend server..."
    
    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            print_success "Frontend server stopped (PID: $PID)"
        else
            print_warning "Frontend server was not running"
        fi
        rm -f frontend.pid
    else
        print_warning "No frontend PID file found"
        
        # Try to find and kill any HTTP servers on port 3000
        PIDS=$(lsof -ti:3000 2>/dev/null || true)
        if [ ! -z "$PIDS" ]; then
            echo $PIDS | xargs kill 2>/dev/null || true
            print_success "Stopped processes on port 3000"
        fi
    fi
}

# Stop Docker containers
stop_docker_services() {
    print_status "Stopping Docker services..."
    
    # Stop API container
    if docker ps | grep -q iroa-api; then
        print_status "Stopping IROA API container..."
        docker stop iroa-api
        print_success "IROA API container stopped"
    else
        print_warning "IROA API container was not running"
    fi
    
    # Stop Prometheus container
    if docker ps | grep -q iroa-prometheus; then
        print_status "Stopping Prometheus container..."
        docker stop iroa-prometheus
        print_success "Prometheus container stopped"
    else
        print_warning "Prometheus container was not running"
    fi
    
    # Remove containers if --clean flag is provided
    if [[ "$1" == "--clean" ]] || [[ "$1" == "-c" ]]; then
        print_status "Removing containers..."
        docker rm iroa-api iroa-prometheus 2>/dev/null || true
        print_success "Containers removed"
    fi
}

# Stop all processes
stop_all_processes() {
    print_status "Stopping all IROA processes..."
    
    # Stop processes on known ports
    for port in 3000 8001 9090; do
        PIDS=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PIDS" ]; then
            print_status "Stopping processes on port $port..."
            echo $PIDS | xargs kill 2>/dev/null || true
            print_success "Stopped processes on port $port"
        fi
    done
}

# Clean up log files
cleanup_logs() {
    if [[ "$1" == "--clean" ]] || [[ "$1" == "-c" ]]; then
        print_status "Cleaning up log files..."
        rm -f logs/frontend.log
        print_success "Log files cleaned"
    fi
}

# Main execution
main() {
    echo "🔧 IROA System Shutdown"
    echo "======================="
    
    stop_frontend
    stop_docker_services "$1"
    
    if [[ "$1" == "--force" ]] || [[ "$1" == "-f" ]]; then
        stop_all_processes
    fi
    
    cleanup_logs "$1"
    
    echo ""
    echo "✅ IROA System Stopped Successfully!"
    echo "===================================="
    echo ""
    echo "🚀 To start the system again, run: ./start.sh"
    echo ""
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "IROA System Stop Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --clean, -c    Remove containers and clean log files"
        echo "  --force, -f    Force stop all processes on IROA ports"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              Stop system normally"
        echo "  $0 --clean      Stop system and clean up containers/logs"
        echo "  $0 --force      Force stop all processes"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
