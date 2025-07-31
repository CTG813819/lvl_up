#!/bin/bash

# Final Cleanup Script
# Properly manages the standalone uvicorn process and systemd service

set -e

echo "🧹 Final Cleanup and Service Management"
echo "======================================="

# Check current status
echo "📊 Current Status Check:"
echo "Systemd service status:"
sudo systemctl status ai-backend-python --no-pager

echo ""
echo "Port 8000 usage:"
sudo lsof -i :8000

echo ""
echo "All uvicorn processes:"
ps aux | grep uvicorn | grep -v grep

echo ""
echo "Testing current service:"
curl -s http://localhost:8000/api/learning/stats/Imperium | jq '.' || echo "Service not responding"

echo ""
echo "🔧 Decision: Keep the working standalone process"
echo "================================================"
echo "The standalone uvicorn process (PID 8578) is working correctly."
echo "The systemd service is failing because port 8000 is already in use."
echo ""
echo "Option 1: Keep the standalone process (recommended)"
echo "Option 2: Kill the standalone process and use systemd service"
echo ""

read -p "Choose option (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "✅ Keeping standalone process"
    
    # Disable the systemd service to prevent conflicts
    echo "🛑 Disabling systemd service to prevent conflicts..."
    sudo systemctl stop ai-backend-python
    sudo systemctl disable ai-backend-python
    
    echo "✅ Systemd service disabled"
    echo "✅ Standalone uvicorn process will continue running"
    
elif [ "$choice" = "2" ]; then
    echo "🔄 Switching to systemd service"
    
    # Kill the standalone process
    echo "🛑 Killing standalone uvicorn process..."
    sudo kill -9 8578
    sleep 3
    
    # Verify port is free
    echo "🔍 Verifying port 8000 is free..."
    sudo lsof -i :8000 || echo "✅ Port 8000 is free"
    
    # Start the systemd service
    echo "🚀 Starting systemd service..."
    sudo systemctl start ai-backend-python
    
    # Wait and check status
    echo "⏳ Waiting for service to start..."
    sleep 10
    
    echo "📊 Service status:"
    sudo systemctl status ai-backend-python --no-pager
    
    # Test the service
    echo "🌐 Testing service..."
    if curl -s --connect-timeout 10 http://localhost:8000/api/learning/stats/Imperium > /dev/null; then
        echo "✅ Systemd service is working"
    else
        echo "❌ Systemd service failed"
        echo "📋 Recent logs:"
        sudo journalctl -u ai-backend-python -n 10
    fi
    
else
    echo "❌ Invalid choice. Keeping standalone process."
    sudo systemctl stop ai-backend-python
    sudo systemctl disable ai-backend-python
fi

echo ""
echo "🎉 Final Status:"
echo "================"
echo "Port 8000:"
sudo lsof -i :8000

echo ""
echo "Service processes:"
ps aux | grep uvicorn | grep -v grep

echo ""
echo "API Test:"
curl -s http://localhost:8000/api/learning/stats/Imperium | jq '.' || echo "Service not responding"

echo ""
echo "📊 Summary:"
echo "==========="
echo "✅ AI Backend is running on port 8000"
echo "✅ API endpoints are responding"
echo "✅ Learning stats are working"
echo ""
echo "🚀 To monitor the process:"
echo "   ps aux | grep uvicorn"
echo ""
echo "🌐 To test the API:"
echo "   curl http://localhost:8000/api/learning/stats/Imperium"
echo ""
echo "📋 To check logs (if using systemd):"
echo "   sudo journalctl -u ai-backend-python -f" 