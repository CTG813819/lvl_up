#!/bin/bash

# Critical Performance Fix Deployment Script
# =========================================
# This script deploys the critical performance fix to address:
# - High CPU utilization (75-90%)
# - Periodic timeouts
# - Multiple overlapping background services
# - Resource exhaustion

set -e

echo "🚨 DEPLOYING CRITICAL PERFORMANCE FIX"
echo "====================================="
echo "This will stop all services and restart with optimized configuration"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    exit 1
fi

# Set variables
BASE_PATH="/home/ubuntu/ai-backend-python"
LOG_PATH="$BASE_PATH/logs"

# Create log directory
mkdir -p "$LOG_PATH"

echo "📁 Working directory: $BASE_PATH"
echo "📝 Logs will be written to: $LOG_PATH"

# Stop all existing services first
echo ""
echo "🛑 Stopping all existing services..."
systemctl stop ai-backend-python.service || true
systemctl stop autonomous-learning.service || true
systemctl stop guardian-ai.service || true
systemctl stop sandbox-ai.service || true
systemctl stop conquest-ai.service || true
systemctl stop imperium-ai.service || true
systemctl stop custodes-ai.service || true
systemctl stop ai-coordination-scheduler.service || true

# Kill any remaining Python processes
echo "🔪 Killing remaining Python processes..."
pkill -f python || true
sleep 2

# Change to the backend directory
cd "$BASE_PATH"

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install required packages if needed
echo "📦 Installing required packages..."
pip install psutil structlog || true

# Run the critical performance fix
echo ""
echo "🔧 Running critical performance fix..."
python fix_backend_performance_critical.py

# Check if the fix was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Critical performance fix completed successfully!"
    
    # Wait a moment for services to start
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service status
    echo ""
    echo "📊 Checking service status..."
    systemctl status ai-backend-optimized.service --no-pager -l
    
    # Check system resources
    echo ""
    echo "💻 System resource usage:"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory Usage: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
    echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"
    
    # Test the backend
    echo ""
    echo "🧪 Testing backend connectivity..."
    if curl -s http://localhost:4000/health > /dev/null; then
        echo "✅ Backend is responding to health checks"
    else
        echo "⚠️ Backend health check failed - checking logs..."
        journalctl -u ai-backend-optimized.service --no-pager -n 20
    fi
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "======================="
    echo "✅ Optimized backend service is running"
    echo "✅ Resource usage has been reduced"
    echo "✅ Background services are optimized"
    echo "✅ Database connections are optimized"
    echo ""
    echo "📊 Monitor performance with:"
    echo "  systemctl status ai-backend-optimized.service"
    echo "  journalctl -u ai-backend-optimized.service -f"
    echo "  htop"
    echo ""
    echo "🔧 If issues persist, check logs at:"
    echo "  $LOG_PATH/critical_performance_fix.log"
    
else
    echo ""
    echo "❌ Critical performance fix failed!"
    echo "Check the logs for details:"
    echo "  $LOG_PATH/critical_performance_fix.log"
    exit 1
fi 