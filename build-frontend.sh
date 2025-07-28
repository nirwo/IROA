#!/bin/bash

# IROA Frontend Build Script
# Ensures consistent CSS compilation for all deployment methods

set -e

echo "🎨 Building IROA Frontend Assets"
echo "================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[BUILD]${NC} $1"
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

# Navigate to dashboard directory
cd dashboard

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    print_error "Node.js is required for building frontend assets"
    print_status "Please install Node.js and try again"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install || {
        print_error "Failed to install dependencies"
        exit 1
    }
    print_success "Dependencies installed"
fi

# Build Tailwind CSS
print_status "Building Tailwind CSS..."
npm run build-css || {
    print_error "CSS build failed"
    exit 1
}
print_success "CSS built successfully"

# Verify output files exist
if [ -f "styles/output.css" ]; then
    CSS_SIZE=$(du -h styles/output.css | cut -f1)
    print_success "CSS file generated (${CSS_SIZE})"
else
    print_error "CSS output file not found"
    exit 1
fi

# Verify main.js exists
if [ -f "main.js" ]; then
    JS_SIZE=$(du -h main.js | cut -f1)
    print_success "JavaScript file verified (${JS_SIZE})"
else
    print_error "JavaScript file not found"
    exit 1
fi

# Verify index.html exists
if [ -f "index.html" ]; then
    print_success "HTML file verified"
else
    print_error "HTML file not found"
    exit 1
fi

echo ""
print_success "Frontend build completed successfully!"
echo "✅ CSS: styles/output.css"
echo "✅ JS:  main.js"
echo "✅ HTML: index.html"
echo ""
echo "The dashboard is now ready for deployment with consistent styling."
