#!/bin/bash

# Quick Diagnosis Script
# Check current state before deployment

echo "🔍 Quick System Diagnosis"
echo "========================="

echo ""
echo "📊 Current Port Usage:"
echo "Port 8000:"
sudo lsof -i :8000 2>/dev/null || echo "  Free"

echo "Port 4000:"
sudo lsof -i :4000 2>/dev/null || echo "  Free"

echo ""
echo "🔍 Running uvicorn processes:"
ps aux | grep uvicorn | grep -v grep || echo "  None found"

echo ""
echo "📋 AI Backend Service Status:"
sudo systemctl status ai-backend-python --no-pager -l

echo ""
echo "🌐 Quick connectivity test:"
echo "Port 8000:"
curl -s --connect-timeout 3 http://localhost:8000/health 2>/dev/null && echo "  ✅ Responding" || echo "  ❌ Not responding"

echo "Port 4000:"
curl -s --connect-timeout 3 http://localhost:4000/health 2>/dev/null && echo "  ✅ Responding" || echo "  ❌ Not responding"

echo ""
echo "💡 Ready to run deployment fix:"
echo "   ./deploy_to_ec2_fixed.sh" 