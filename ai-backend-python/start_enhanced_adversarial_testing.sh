#!/bin/bash

# Enhanced Adversarial Testing Service Startup Script
# This script prevents multiple instances and ensures proper startup

echo "🚀 Starting Enhanced Adversarial Testing Service..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require

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
    echo "🔄 Stopping existing enhanced adversarial testing processes..."
    
    # Kill existing process using PID file
    if [ -f enhanced_adversarial_testing.pid ]; then
        local pid=$(cat enhanced_adversarial_testing.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "Killing existing process with PID: $pid"
            kill $pid
            sleep 2
        fi
        rm -f enhanced_adversarial_testing.pid
    fi
    
    # Kill any processes using port 8001
    pkill -f "standalone_enhanced_adversarial_testing.py" 2>/dev/null || true
    
    # Kill any processes using port 8001
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
        echo "Killing processes using port 8001..."
        lsof -Pi :8001 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    fi
    
    # Wait for processes to stop
    sleep 3
    
    # Double-check port is free
    if check_port 8001; then
        echo "✅ Port 8001 is now available"
    else
        echo "❌ Port 8001 is still in use"
        return 1
    fi
}

# Function to start enhanced adversarial testing service
start_enhanced_adversarial_testing() {
    echo "🚀 Starting Enhanced Adversarial Testing Service on port 8001..."
    
    # Check if port 8001 is available
    if ! check_port 8001; then
        echo "❌ Port 8001 is already in use. Stopping existing process..."
        kill_existing_processes
    fi
    
    # Start enhanced adversarial testing service
    python standalone_enhanced_adversarial_testing.py &
    local pid=$!
    echo $pid > enhanced_adversarial_testing.pid
    
    echo "✅ Enhanced Adversarial Testing Service started with PID: $pid"
    
    # Wait for enhanced adversarial testing service to start
    echo "⏳ Waiting for enhanced adversarial testing service to start..."
    for i in {1..60}; do
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
    echo "📊 Enhanced Adversarial Testing Service Status:"
    echo "=============================================="
    
    # Check if PID file exists and process is running
    if [ -f enhanced_adversarial_testing.pid ]; then
        local pid=$(cat enhanced_adversarial_testing.pid)
        if kill -0 $pid 2>/dev/null; then
            echo "✅ Process running with PID: $pid"
        else
            echo "❌ PID file exists but process is not running"
        fi
    else
        echo "❌ No PID file found"
    fi
    
    # Check port
    if check_port 8001; then
        echo "✅ Port 8001 is available"
    else
        echo "❌ Port 8001 is in use"
    fi
    
    # Check health endpoint
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Health endpoint responding"
        local health_response=$(curl -s http://localhost:8001/health)
        echo "📊 Health response: $health_response"
    else
        echo "❌ Health endpoint not responding"
    fi
    
    echo ""
    echo "🔗 Service URL: http://localhost:8001"
    echo ""
}

# Function to stop service
stop_service() {
    echo "🛑 Stopping Enhanced Adversarial Testing Service..."
    kill_existing_processes
    echo "✅ Service stopped"
}

# Main execution
main() {
    case "${1:-start}" in
        start)
            echo "🔧 Enhanced Adversarial Testing Service Manager"
            echo "=============================================="
            
            # Kill existing processes
            kill_existing_processes
            
            # Start service
            if start_enhanced_adversarial_testing; then
                show_status
                echo "🎉 Enhanced Adversarial Testing Service started successfully!"
            else
                echo "❌ Failed to start Enhanced Adversarial Testing Service"
                exit 1
            fi
            ;;
        stop)
            stop_service
            ;;
        restart)
            stop_service
            sleep 2
            main start
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status}"
            echo "  start   - Start the service"
            echo "  stop    - Stop the service"
            echo "  restart - Restart the service"
            echo "  status  - Show service status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 