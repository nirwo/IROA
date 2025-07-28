#!/bin/bash

# IROA Dashboard Stop Script

echo "🛑 Stopping IROA Dashboard server..."

# Kill server process
pkill -f "node server.js" || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Wait and verify
sleep 2
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Server may still be running on port 3000"
else
    echo "✅ Server stopped successfully"
fi