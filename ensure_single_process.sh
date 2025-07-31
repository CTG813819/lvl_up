#!/bin/bash

echo "🔧 Ensuring single process operation..."

# Function to kill all uvicorn processes
kill_all_uvicorn() {
    echo "🔪 Killing all uvicorn processes..."
    
    # Find all uvicorn processes
    uvicorn_pids=$(pgrep -f uvicorn)
    
    if [ ! -z "$uvicorn_pids" ]; then
        echo "Found uvicorn processes: $uvicorn_pids"
        
        # Kill them gracefully first
        for pid in $uvicorn_pids; do
            echo "Killing process $pid gracefully..."
            kill $pid 2>/dev/null || true
        done
        
        # Wait a moment
        sleep 2
        
        # Force kill any remaining processes
        uvicorn_pids=$(pgrep -f uvicorn)
        if [ ! -z "$uvicorn_pids" ]; then
            echo "Force killing remaining processes: $uvicorn_pids"
            for pid in $uvicorn_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
        
        # Wait for processes to fully terminate
        sleep 3
    else
        echo "No uvicorn processes found"
    fi
}

# Function to check if port is free
check_port() {
    local port=$1
    if /usr/bin/lsof -i :$port > /dev/null 2>&1; then
        echo "❌ Port $port is still in use"
        return 1
    else
        echo "✅ Port $port is free"
        return 0
    fi
}

# Kill all uvicorn processes
kill_all_uvicorn

# Check if port 8000 is free
if ! check_port 8000; then
    echo "🔪 Force killing processes on port 8000..."
    /usr/bin/fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
    
    if ! check_port 8000; then
        echo "❌ Port 8000 is still in use after force kill"
        exit 1
    fi
fi

echo "✅ Single process environment ready" 