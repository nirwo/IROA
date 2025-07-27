#!/bin/bash

# IROA System Status Script
# This script checks the status of all IROA services

echo "📊 IROA System Status"
echo "====================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_running() {
    echo -e "${GREEN}✅ RUNNING${NC} $1"
}

print_stopped() {
    echo -e "${RED}❌ STOPPED${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO${NC} $1"
}

# Check Docker containers
echo ""
echo "🐳 Docker Containers:"
echo "--------------------"

if docker ps | grep -q iroa-api; then
    print_running "IROA API (port 8001)"
else
    print_stopped "IROA API"
fi

if docker ps | grep -q iroa-prometheus; then
    print_running "Prometheus (port 9090)"
else
    print_stopped "Prometheus"
fi

# Check frontend
echo ""
echo "🌐 Frontend Server:"
echo "------------------"

if [ -f "frontend.pid" ]; then
    PID=$(cat frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        print_running "Frontend Server (PID: $PID, port 3000)"
    else
        print_warning "Frontend Server (cleaning stale PID file)"
        rm -f frontend.pid
        # Check if something else is running on port 3000
        if lsof -ti:3000 > /dev/null 2>&1; then
            PID=$(lsof -ti:3000)
            print_running "Frontend Server (PID: $PID, port 3000)"
        else
            print_stopped "Frontend Server"
        fi
    fi
elif lsof -ti:3000 > /dev/null 2>&1; then
    PID=$(lsof -ti:3000)
    print_running "Frontend Server (PID: $PID, port 3000)"
else
    print_stopped "Frontend Server"
fi

# Check service connectivity
echo ""
echo "🔗 Service Connectivity:"
echo "------------------------"

# Check API
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    print_running "API Health Check"
else
    print_stopped "API Health Check"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_running "Frontend Accessibility"
else
    print_stopped "Frontend Accessibility"
fi

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_running "Prometheus Health Check"
else
    print_stopped "Prometheus Health Check"
fi

# Show URLs
echo ""
echo "🌍 Access URLs:"
echo "--------------"
# Get host IP - handle both Linux and macOS
if command -v hostname >/dev/null 2>&1; then
    # Try Linux style first
    HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || hostname -i 2>/dev/null | awk '{print $1}' || ifconfig | grep 'inet ' | grep -v '127.0.0.1' | head -1 | awk '{print $2}' | sed 's/addr://' || echo "localhost")
else
    # Fallback for systems without hostname
    HOST_IP=$(ifconfig | grep 'inet ' | grep -v '127.0.0.1' | head -1 | awk '{print $2}' | sed 's/addr://' || echo "localhost")
fi

# If HOST_IP is empty or just whitespace, use localhost
if [ -z "$HOST_IP" ] || [ "$HOST_IP" = " " ]; then
    HOST_IP="localhost"
fi
echo "📊 Dashboard: http://$HOST_IP:3000 (or http://localhost:3000)"
echo "🔧 API: http://$HOST_IP:8001 (or http://localhost:8001)"
echo "📈 Prometheus: http://$HOST_IP:9090 (or http://localhost:9090)"

# Show logs location
echo ""
echo "📝 Logs:"
echo "--------"
echo "Frontend: logs/frontend.log"
echo "API: docker logs iroa-api"
echo "Prometheus: docker logs iroa-prometheus"

echo ""
