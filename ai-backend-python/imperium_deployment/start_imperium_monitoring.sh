#!/bin/bash
# Enhanced Imperium Monitoring System Startup Script

cd /home/ubuntu/lvl_up/ai-backend-python

echo "🚀 Starting Imperium Monitoring System..."

# Install required packages
pip3 install psutil requests

# Create log directory
mkdir -p logs

# Start monitoring system in background with proper logging
nohup python3 -m app.services.imperium_monitoring > logs/imperium_monitoring.log 2>&1 &

# Save PID
echo $! > imperium_monitoring.pid

echo "✅ Imperium Monitoring System started with PID: $(cat imperium_monitoring.pid)"
echo "📊 Logs available at: logs/imperium_monitoring.log"
echo "🔍 Monitor with: tail -f logs/imperium_monitoring.log"
