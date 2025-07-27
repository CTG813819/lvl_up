#!/bin/bash

# Start Enhanced Adversarial Testing Service on Port 8001
# This script starts the enhanced adversarial testing service as a standalone service

set -e

echo "🚀 Starting Enhanced Adversarial Testing Service on Port 8001..."
echo "================================================================="

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Check if port 8001 is already in use
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use. Stopping existing service..."
    pkill -f "uvicorn.*8001" || true
    sleep 2
fi

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/home/ubuntu/ai-backend-python"
export DATABASE_URL="postgresql://neon_user:neon_password@ep-cool-forest-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Start the enhanced adversarial testing service
echo "🔧 Starting enhanced adversarial testing service..."
python standalone_enhanced_adversarial_testing.py &

# Wait a moment for the service to start
sleep 5

# Check if the service is running
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Enhanced Adversarial Testing Service is running on port 8001"
    echo "🌐 Health check: http://localhost:8001/health"
    echo "📊 Overview: http://localhost:8001/"
    echo "🔗 API endpoint: http://localhost:8001/generate-and-execute"
else
    echo "❌ Failed to start Enhanced Adversarial Testing Service"
    exit 1
fi

echo "================================================================="
echo "🎯 Service is ready for enhanced adversarial testing!"
echo "=================================================================" 