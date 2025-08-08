#!/bin/bash

# Diagnostic Script for Port Conflict Issue
# This script checks the current state of the AI backend service

echo "🔍 AI Backend Port Conflict Diagnosis"
echo "====================================="

echo ""
echo "📊 Systemd Service Status:"
sudo systemctl status ai-backend-python --no-pager

echo ""
echo "🔍 Port 8000 Usage:"
sudo lsof -i :8000 || echo "No process found using port 8000"

echo ""
echo "🔍 Port 4000 Usage:"
sudo lsof -i :4000 || echo "No process found using port 4000"

echo ""
echo "🔍 All uvicorn processes:"
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn processes found"

echo ""
echo "📋 Recent service logs:"
sudo journalctl -u ai-backend-python -n 20 --no-pager

echo ""
echo "🌐 Testing local connections:"
echo "Testing port 8000:"
curl -s --connect-timeout 5 http://localhost:8000/health 2>/dev/null && echo "✅ Port 8000 is responding" || echo "❌ Port 8000 is not responding"

echo "Testing port 4000:"
curl -s --connect-timeout 5 http://localhost:4000/health 2>/dev/null && echo "✅ Port 4000 is responding" || echo "❌ Port 4000 is not responding"

echo ""
echo "📝 Current Configuration:"
echo "Service file location: /etc/systemd/system/ai-backend-python.service"
if [ -f "/etc/systemd/system/ai-backend-python.service" ]; then
    echo "✅ Service file exists"
    echo "Current ExecStart command:"
    grep "ExecStart" /etc/systemd/system/ai-backend-python.service
else
    echo "❌ Service file not found"
fi

echo ""
echo "💡 Recommendations:"
echo "1. If port 8000 is in use, run: ./fix_port_conflict.sh"
echo "2. If service is not starting, check logs: sudo journalctl -u ai-backend-python -f"
echo "3. If you want to use port 8000, first stop any conflicting processes" 