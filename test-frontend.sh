#!/bin/bash

# Test script for frontend startup
set -e

echo "🧪 Testing frontend startup..."

# We're already in the dashboard directory, so let's go to parent and then back
cd ..
mkdir -p logs

# Go to dashboard directory
if [ -d "dashboard" ]; then
    cd dashboard
else
    echo "❌ Dashboard directory not found. Make sure you're running from the project root."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start Vite dev server
echo "🚀 Starting Vite dev server..."
npm run dev -- --port 3001 --host 0.0.0.0 > ../logs/frontend-test.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend-test.pid

echo "Frontend PID: $FRONTEND_PID"

# Wait a bit for server to start
sleep 3

# Test if server is responding
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ Frontend server is responding on port 3001"
    echo "🌐 Access at: http://localhost:3001"
else
    echo "❌ Frontend server is not responding"
fi

echo ""
echo "To stop the test server, run: kill $FRONTEND_PID"
echo "Log file: logs/frontend-test.log"