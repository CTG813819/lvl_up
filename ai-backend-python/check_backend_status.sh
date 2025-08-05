#!/bin/bash

# Backend Status Check and Diagnosis Script

echo "🔍 Checking backend status and diagnosing connection issues..."

# Check if service is running
echo "📊 Service Status:"
sudo systemctl status ai-backend-python --no-pager

echo ""
echo "🌐 Checking port 4000:"
netstat -tlnp | grep :4000 || echo "Port 4000 not listening"

echo ""
echo "🔍 Checking uvicorn process:"
ps aux | grep uvicorn | grep -v grep

echo ""
echo "📋 Checking recent logs:"
sudo journalctl -u ai-backend-python -n 20 --no-pager

echo ""
echo "🌐 Testing local connection:"
curl -v http://localhost:4000/health 2>&1 || echo "Connection failed"

echo ""
echo "🔧 Checking if port is in use:"
sudo lsof -i :4000

echo ""
echo "📊 Memory and CPU usage:"
ps aux | grep uvicorn | grep -v grep | awk '{print "PID: " $2 ", CPU: " $3 "%, MEM: " $4 "%"}'

echo ""
echo "💡 Troubleshooting steps:"
echo "1. Check if the service is actually listening on port 4000"
echo "2. Verify the uvicorn command in the service file"
echo "3. Check for any import errors in the logs"
echo "4. Ensure the virtual environment is being used correctly"
echo ""
echo "🚀 To restart the service:"
echo "   sudo systemctl restart ai-backend-python"
echo ""
echo "📊 To monitor logs in real-time:"
echo "   sudo journalctl -u ai-backend-python -f" 