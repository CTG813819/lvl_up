#!/bin/bash

# Training Ground Server Startup Script
# This script starts the training ground server on port 8002

echo "🚀 Starting Training Ground Server on port 8002..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export TRAINING_GROUND_PORT=8002
export TRAINING_GROUND_HOST=0.0.0.0
export ENVIRONMENT=production

# Start the training ground server
echo "Starting training ground server..."
python training_ground_server.py &

# Save the process ID
echo $! > training_ground_server.pid

echo "✅ Training Ground Server started on port 8002"
echo "PID: $(cat training_ground_server.pid)"

# Wait a moment for the server to start
sleep 3

# Check if the server is running
if curl -s http://localhost:8002/health > /dev/null; then
    echo "✅ Training Ground Server is healthy and running"
else
    echo "❌ Training Ground Server failed to start properly"
    exit 1
fi 