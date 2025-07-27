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
    
    local stopped=false
    
    # First try to stop using PID file
    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_status "Stopping frontend server (PID: $PID)..."
            kill $PID 2>/dev/null || true
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    print_success "Frontend server stopped gracefully (PID: $PID)"
                    stopped=true
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ! $stopped && ps -p $PID > /dev/null 2>&1; then
                print_warning "Force killing frontend server (PID: $PID)..."
                kill -9 $PID 2>/dev/null || true
                sleep 2
                if ! ps -p $PID > /dev/null 2>&1; then
                    print_success "Frontend server force stopped (PID: $PID)"
                    stopped=true
                fi
            fi
        else
            print_warning "Frontend server PID file exists but process not running"
        fi
        rm -f frontend.pid
    else
        print_warning "No frontend PID file found"
    fi
    
    # Try to find and kill any remaining HTTP servers on port 3000
    PIDS=$(lsof -ti:3000 2>/dev/null || true)
    if [ ! -z "$PIDS" ]; then
        print_status "Found processes on port 3000: $PIDS"
        for pid in $PIDS; do
            if ps -p $pid > /dev/null 2>&1; then
                print_status "Stopping process $pid on port 3000..."
                kill $pid 2>/dev/null || true
                sleep 2
                
                # Force kill if still running
                if ps -p $pid > /dev/null 2>&1; then
                    print_warning "Force killing process $pid..."
                    kill -9 $pid 2>/dev/null || true
                    sleep 1
                fi
                
                if ! ps -p $pid > /dev/null 2>&1; then
                    print_success "Stopped process $pid on port 3000"
                    stopped=true
                fi
            fi
        done
    fi
    
    # Verify port 3000 is free
    if ! lsof -ti:3000 > /dev/null 2>&1; then
        if $stopped; then
            print_success "Frontend server stopped successfully"
        else
            print_success "Port 3000 is free"
        fi
    else
        print_error "Failed to stop all processes on port 3000"
        return 1
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
    print_status "Force stopping all IROA processes..."
    
    # Stop processes on known ports
    for port in 3000 8001 9090; do
        PIDS=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PIDS" ]; then
            print_status "Force stopping processes on port $port: $PIDS"
            for pid in $PIDS; do
                if ps -p $pid > /dev/null 2>&1; then
                    # Try graceful kill first
                    kill $pid 2>/dev/null || true
                    sleep 2
                    
                    # Force kill if still running
                    if ps -p $pid > /dev/null 2>&1; then
                        print_warning "Force killing process $pid on port $port..."
                        kill -9 $pid 2>/dev/null || true
                        sleep 1
                    fi
                    
                    if ! ps -p $pid > /dev/null 2>&1; then
                        print_success "Stopped process $pid on port $port"
                    else
                        print_error "Failed to stop process $pid on port $port"
                    fi
                fi
            done
        else
            print_status "No processes found on port $port"
        fi
    done
    
    # Also look for common IROA process names
    print_status "Checking for IROA-related processes..."
    IROA_PIDS=$(pgrep -f "iroa\|http-server\|python.*http.server" 2>/dev/null || true)
    if [ ! -z "$IROA_PIDS" ]; then
        print_status "Found IROA-related processes: $IROA_PIDS"
        for pid in $IROA_PIDS; do
            if ps -p $pid > /dev/null 2>&1; then
                PROCESS_INFO=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
                print_status "Stopping IROA process $pid ($PROCESS_INFO)..."
                kill $pid 2>/dev/null || true
                sleep 2
                
                if ps -p $pid > /dev/null 2>&1; then
                    print_warning "Force killing IROA process $pid..."
                    kill -9 $pid 2>/dev/null || true
                    sleep 1
                fi
                
                if ! ps -p $pid > /dev/null 2>&1; then
                    print_success "Stopped IROA process $pid"
                fi
            fi
        done
    fi
}

# Clean up log files
cleanup_logs() {
    if [[ "$1" == "--clean" ]] || [[ "$1" == "-c" ]]; then
        print_status "Cleaning up log files..."
        rm -f logs/frontend.log
        print_success "Log files cleaned"
    fi
}

# Verify system is stopped
verify_shutdown() {
    print_status "Verifying system shutdown..."
    
    local all_stopped=true
    
    # Check ports
    for port in 3000 8001 9090; do
        if lsof -ti:$port > /dev/null 2>&1; then
            print_warning "Port $port is still in use"
            all_stopped=false
        fi
    done
    
    # Check Docker containers
    if docker ps --format "table {{.Names}}" | grep -E "iroa-api|iroa-prometheus" > /dev/null 2>&1; then
        print_warning "Some Docker containers are still running"
        all_stopped=false
    fi
    
    if $all_stopped; then
        print_success "All IROA services have been stopped"
        return 0
    else
        print_error "Some services may still be running"
        return 1
    fi
}

# Main execution
main() {
    echo "🔧 IROA System Shutdown"
    echo "======================="
    
    # Stop services in order
    stop_frontend
    stop_docker_services "$1"
    
    if [[ "$1" == "--force" ]] || [[ "$1" == "-f" ]]; then
        stop_all_processes
    fi
    
    cleanup_logs "$1"
    
    # Verify shutdown
    echo ""
    if verify_shutdown; then
        echo "✅ IROA System Stopped Successfully!"
        echo "===================================="
        echo ""
        echo "🚀 To start the system again, run: ./start.sh"
        echo ""
    else
        echo "⚠️  IROA System Shutdown Completed with Warnings"
        echo "==============================================="
        echo ""
        echo "Some processes may still be running. Use --force flag to force stop all processes."
        echo "Run: $0 --force"
        echo ""
    fi
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
