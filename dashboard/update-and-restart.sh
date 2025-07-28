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

# Wait a moment for process to stop
sleep 2

# Start the server
echo "🚀 Starting server..."
node server.js &

echo "✅ Update complete! Dashboard should be available at http://localhost:3000"
echo "💡 If you still see old content, try hard refresh (Ctrl+F5 or Cmd+Shift+R)"