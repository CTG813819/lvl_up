#!/bin/bash

# Stop All AI Backend Services Script

echo "🛑 Stopping AI Backend Services..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Function to stop process by PID file
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🔄 Stopping $service_name (PID: $pid)..."
        kill $pid 2>/dev/null || true
        rm -f "$pid_file"
        echo "✅ $service_name stopped"
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Stop main backend
stop_process "main_backend.pid" "Main Backend"

# Stop training ground server
stop_process "training_ground_server.pid" "Training Ground Server"

# Kill any remaining processes
echo "🔄 Killing any remaining processes..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "training_ground_server.py" 2>/dev/null || true
pkill -f "standalone_enhanced_adversarial_testing" 2>/dev/null || true

# Wait for processes to stop
sleep 2

echo "✅ All AI Backend services stopped" 