#!/bin/bash

# IROA Quick Start Script
# One-command setup and start for new deployments

set -e

echo "⚡ IROA Quick Start"
echo "=================="
echo "This will build and start the entire IROA system"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[DONE]${NC} $1"
}

# Step 1: Make scripts executable
print_status "Making scripts executable..."
chmod +x *.sh
print_success "Scripts are now executable"

# Step 2: Build containers
print_status "Building Docker containers..."
./build.sh --clean
print_success "Containers built"

# Step 3: Start system
print_status "Starting IROA system..."
./start.sh
print_success "System started"

echo ""
echo "🎉 IROA is now running!"
echo "======================"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:8001"
echo ""
echo "Use './status.sh' to check system status"
echo "Use './stop.sh' to stop the system"
