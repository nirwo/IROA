#!/bin/bash

# IROA Dashboard Update Script
# Run this script after git pull to ensure all updates are applied

echo "🔄 Updating IROA Dashboard..."

# Navigate to dashboard directory
cd "$(dirname "$0")"

# Rebuild Tailwind CSS
echo "🎨 Rebuilding CSS..."
npx tailwindcss -i ./styles/input.css -o ./styles/output.css --watch=false

# Kill existing server process if running
echo "🛑 Stopping existing server..."
pkill -f "node server.js" || true

# Also try to kill by port (more aggressive)
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Wait a moment for process to stop
echo "⏳ Waiting for server to stop..."
sleep 5

# Check if port is still in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is still in use. Please manually stop the process or use a different port."
    echo "💡 Try: lsof -ti:3000 | xargs kill -9"
    exit 1
fi

# Start the server
echo "🚀 Starting server..."
nohup node server.js > server.log 2>&1 &

# Wait a moment and check if server started
sleep 2
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Update complete! Dashboard should be available at http://localhost:3000"
    echo "💡 If you still see old content, try hard refresh (Ctrl+F5 or Cmd+Shift+R)"
    echo "📝 Server logs: tail -f server.log"
else
    echo "❌ Server failed to start. Check server.log for details."
    exit 1
fi