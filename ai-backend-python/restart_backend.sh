#!/bin/bash

echo "🔄 Restarting AI Backend Python service..."

# Stop the service
sudo systemctl stop ai-backend-python

# Wait a moment
sleep 2

# Start the service
sudo systemctl start ai-backend-python

# Check status
echo "📊 Service status:"
sudo systemctl status ai-backend-python --no-pager

echo "✅ Backend restart completed!" 