#!/bin/bash

# Deploy Enhanced Adversarial Testing Service
# This script sets up the enhanced adversarial testing service on port 8001

echo "🚀 Deploying Enhanced Adversarial Testing Service..."
echo "=================================================="

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Stop any existing enhanced adversarial testing service
echo "🔄 Stopping existing enhanced adversarial testing service..."
sudo systemctl stop enhanced-adversarial-testing 2>/dev/null || true
pkill -f "standalone_enhanced_adversarial_testing.py" 2>/dev/null || true

# Copy the systemd service file
echo "📋 Installing systemd service..."
sudo cp enhanced-adversarial-testing.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "🔧 Enabling service to start on boot..."
sudo systemctl enable enhanced-adversarial-testing

# Start the service
echo "🚀 Starting enhanced adversarial testing service..."
sudo systemctl start enhanced-adversarial-testing

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Check service status
echo "📊 Checking service status..."
if sudo systemctl is-active --quiet enhanced-adversarial-testing; then
    echo "✅ Enhanced Adversarial Testing Service is running"
    
    # Test the health endpoint
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
        echo "🌐 Service URL: http://localhost:8001"
        echo "🔗 Health check: http://localhost:8001/health"
        echo "📊 Overview: http://localhost:8001/"
    else
        echo "⚠️  Health check failed - service may still be starting"
    fi
else
    echo "❌ Enhanced Adversarial Testing Service failed to start"
    echo "📋 Checking service logs..."
    sudo journalctl -u enhanced-adversarial-testing --no-pager -n 20
    exit 1
fi

echo ""
echo "🎉 Enhanced Adversarial Testing Service deployment complete!"
echo ""
echo "📝 Useful commands:"
echo "  Check status: sudo systemctl status enhanced-adversarial-testing"
echo "  View logs: sudo journalctl -u enhanced-adversarial-testing -f"
echo "  Restart: sudo systemctl restart enhanced-adversarial-testing"
echo "  Stop: sudo systemctl stop enhanced-adversarial-testing"
echo "" 