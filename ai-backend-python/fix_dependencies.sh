#!/bin/bash

# Quick fix for missing dependencies on EC2
echo "🔧 Installing missing dependencies..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Install missing dependencies
echo "📦 Installing openai, anthropic, transformers, torch..."
pip install openai anthropic transformers torch

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Restart the service
echo "🔄 Restarting ai-backend-python service..."
sudo systemctl restart ai-backend-python

# Check service status
echo "✅ Checking service status..."
sudo systemctl status ai-backend-python --no-pager

echo ""
echo "🎉 Fix completed! The backend should now be running with AI code generation capabilities."
echo ""
echo "📊 Monitor logs with: sudo journalctl -u ai-backend-python -f" 