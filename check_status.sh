#!/bin/bash

# Check AI Backend Services Status Script

echo "📊 AI Backend Services Status"
echo "============================="

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Function to check service status
check_service() {
    local port=$1
    local service_name=$2
    local pid_file=$3
    
    echo -n "🔍 Checking $service_name (port $port)... "
    
    # Check if process is running
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo -n "✅ Process running (PID: $pid) "
        else
            echo -n "❌ Process not running "
        fi
    else
        echo -n "⚠️  No PID file "
    fi
    
    # Check if port is responding
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Port $port responding"
    else
        echo "❌ Port $port not responding"
    fi
}

# Check each service
check_service "8000" "Main Backend" "main_backend.pid"
check_service "8002" "Training Ground Server" "training_ground_server.pid"
check_service "8001" "Adversarial Testing Service" "adversarial_testing.pid"

echo ""
echo "🔗 Service URLs:"
echo "Main Backend: http://localhost:8000"
echo "Training Ground: http://localhost:8002"
echo "Adversarial Testing: http://localhost:8001"

echo ""
echo "📝 Quick Health Checks:"
echo "======================="

# Quick health checks
for port in 8000 8001 8002; do
    echo -n "Port $port: "
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
    fi
done 