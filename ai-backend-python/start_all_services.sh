#!/bin/bash

# Comprehensive AI Backend Startup Script
# This script starts both the main backend (port 8000) and training ground server (port 8002)

echo "🚀 Starting AI Backend Services..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export ENVIRONMENT=production
export RUN_BACKGROUND_JOBS=1
export TRAINING_GROUND_PORT=8002
export TRAINING_GROUND_HOST=0.0.0.0

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $port is already in use"
        return 1
    else
        echo "Port $port is available"
        return 0
    fi
}

# Function to kill existing processes
kill_existing_processes() {
    echo "🔄 Stopping existing processes..."
    
    # Kill existing main backend process
    if [ -f main_backend.pid ]; then
        kill $(cat main_backend.pid) 2>/dev/null || true
        rm -f main_backend.pid
    fi
    
    # Kill existing training ground server process
    if [ -f training_ground_server.pid ]; then
        kill $(cat training_ground_server.pid) 2>/dev/null || true
        rm -f training_ground_server.pid
    fi
    
    # Kill existing enhanced adversarial testing service process
    if [ -f enhanced_adversarial_testing.pid ]; then
        kill $(cat enhanced_adversarial_testing.pid) 2>/dev/null || true
        rm -f enhanced_adversarial_testing.pid
    fi
    
    # Kill any processes using our ports
    pkill -f "main.py" 2>/dev/null || true
    pkill -f "training_ground_server.py" 2>/dev/null || true
    pkill -f "standalone_enhanced_adversarial_testing.py" 2>/dev/null || true
    
    # Wait for processes to stop
    sleep 2
}

# Function to start main backend
start_main_backend() {
    echo "🚀 Starting Main Backend on port 8000..."
    
    # Check if port 8000 is available
    if ! check_port 8000; then
        echo "❌ Port 8000 is already in use. Stopping existing process..."
        pkill -f "main.py" 2>/dev/null || true
        sleep 2
    fi
    
    # Start main backend
    python main.py &
    echo $! > main_backend.pid
    
    echo "✅ Main Backend started with PID: $(cat main_backend.pid)"
    
    # Wait for main backend to start
    echo "⏳ Waiting for main backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Main Backend is healthy and running on port 8000"
            return 0
        fi
        sleep 1
    done
    
    echo "❌ Main Backend failed to start properly"
    return 1
}

# Function to start training ground server
start_training_ground() {
    echo "🚀 Starting Training Ground Server on port 8002..."
    
    # Check if port 8002 is available
    if ! check_port 8002; then
        echo "❌ Port 8002 is already in use. Stopping existing process..."
        pkill -f "training_ground_server.py" 2>/dev/null || true
        sleep 2
    fi
    
    # Start training ground server
    python training_ground_server.py &
    echo $! > training_ground_server.pid
    
    echo "✅ Training Ground Server started with PID: $(cat training_ground_server.pid)"
    
    # Wait for training ground server to start
    echo "⏳ Waiting for training ground server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8002/health > /dev/null 2>&1; then
            echo "✅ Training Ground Server is healthy and running on port 8002"
            return 0
        fi
        sleep 1
    done
    
    echo "❌ Training Ground Server failed to start properly"
    return 1
}

# Function to start enhanced adversarial testing service
start_enhanced_adversarial_testing() {
    echo "🚀 Starting Enhanced Adversarial Testing Service on port 8001..."
    
    # Check if port 8001 is available
    if ! check_port 8001; then
        echo "❌ Port 8001 is already in use. Stopping existing process..."
        pkill -f "standalone_enhanced_adversarial_testing.py" 2>/dev/null || true
        sleep 2
    fi
    
    # Start enhanced adversarial testing service
    python standalone_enhanced_adversarial_testing.py &
    echo $! > enhanced_adversarial_testing.pid
    
    echo "✅ Enhanced Adversarial Testing Service started with PID: $(cat enhanced_adversarial_testing.pid)"
    
    # Wait for enhanced adversarial testing service to start
    echo "⏳ Waiting for enhanced adversarial testing service to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "✅ Enhanced Adversarial Testing Service is healthy and running on port 8001"
            return 0
        fi
        sleep 1
    done
    
    echo "❌ Enhanced Adversarial Testing Service failed to start properly"
    return 1
}

# Function to display status
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    
    # Check main backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Main Backend (port 8000): RUNNING"
    else
        echo "❌ Main Backend (port 8000): NOT RUNNING"
    fi
    
    # Check training ground server
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "✅ Training Ground Server (port 8002): RUNNING"
    else
        echo "❌ Training Ground Server (port 8002): NOT RUNNING"
    fi
    
    # Check enhanced adversarial testing service
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Enhanced Adversarial Testing Service (port 8001): RUNNING"
    else
        echo "❌ Enhanced Adversarial Testing Service (port 8001): NOT RUNNING"
    fi
    
    echo ""
    echo "🔗 Service URLs:"
    echo "Main Backend: http://localhost:8000"
    echo "Training Ground: http://localhost:8002"
    echo "Enhanced Adversarial Testing: http://localhost:8001"
    echo ""
}

# Main execution
main() {
    echo "🔧 AI Backend Service Manager"
    echo "============================="
    
    # Kill existing processes
    kill_existing_processes
    
    # Start main backend
    if start_main_backend; then
        echo "✅ Main Backend started successfully"
    else
        echo "❌ Failed to start Main Backend"
        exit 1
    fi
    
    # Start training ground server
    if start_training_ground; then
        echo "✅ Training Ground Server started successfully"
    else
        echo "❌ Failed to start Training Ground Server"
        exit 1
    fi
    
    # Start enhanced adversarial testing service
    if start_enhanced_adversarial_testing; then
        echo "✅ Enhanced Adversarial Testing Service started successfully"
    else
        echo "❌ Failed to start Enhanced Adversarial Testing Service"
        exit 1
    fi
    
    # Show final status
    show_status
    
    echo "🎉 All services started successfully!"
    echo ""
    echo "📝 To stop all services, run: ./stop_all_services.sh"
    echo "📝 To check status, run: ./check_status.sh"
}

# Run main function
main "$@" 