#!/bin/bash

# EC2 Custodes Protocol Fix Script
# This script forces Custodes tests for all AIs to enable proposal creation

echo "🛡️ Starting Custodes Protocol Fix on EC2..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Check if the backend is running
echo "📊 Checking backend status..."
if curl -s http://localhost:8000/api/imperium/status > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Starting it..."
    # Start the backend if it's not running
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    sleep 10
fi

# Check current custody status
echo "📈 Checking current custody status..."
curl -s http://localhost:8000/api/custody/ | jq '.analytics.ai_specific_metrics' 2>/dev/null || echo "No custody data available"

# Force tests for each AI type
echo "🧪 Forcing Custodes tests for all AIs..."

AI_TYPES=("imperium" "guardian" "sandbox" "conquest")

for ai_type in "${AI_TYPES[@]}"; do
    echo "Testing $ai_type AI..."
    
    # Try the force test endpoint
    response=$(curl -s -X POST http://localhost:8000/api/custody/test/$ai_type/force)
    echo "Response for $ai_type: $response"
    
    # Wait a moment between tests
    sleep 5
done

# Try batch test endpoint
echo "🔄 Attempting batch test..."
batch_response=$(curl -s -X POST http://localhost:8000/api/custody/batch-test)
echo "Batch test response: $batch_response"

# Wait for tests to complete
echo "⏳ Waiting for tests to complete..."
sleep 15

# Check status again
echo "📊 Checking status after tests..."
curl -s http://localhost:8000/api/custody/ | jq '.analytics.ai_specific_metrics' 2>/dev/null || echo "No custody data available"

echo "✅ Custodes Protocol Fix completed!"

# Show recent logs
echo "📋 Recent backend logs:"
tail -20 backend.log 2>/dev/null || echo "No backend logs available" 