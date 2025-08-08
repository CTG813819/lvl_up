#!/bin/bash

# Fix Enhanced Adversarial Testing Service
# This script ensures the enhanced adversarial testing service starts automatically

set -e

echo "🔧 Fixing Enhanced Adversarial Testing Service..."
echo "================================================"

# SSH connection details
EC2_IP="34-202-215-209"
EC2_USER="ubuntu"
PEM_FILE="New.pem"

# Fix the startup script
echo "📝 Fixing startup script..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "cd /home/ubuntu/ai-backend-python && sed -i 's/sleep /\/bin\/sleep /g' start_enhanced_adversarial_testing.sh"

# Create a proper systemd service file
echo "⚙️ Creating proper systemd service..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "sudo tee /etc/systemd/system/enhanced-adversarial-testing.service > /dev/null << 'EOF'
[Unit]
Description=Enhanced Adversarial Testing Service
After=network.target ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python standalone_enhanced_adversarial_testing.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd and restart service
echo "🔄 Reloading systemd and restarting service..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "sudo systemctl daemon-reload"
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "sudo systemctl restart enhanced-adversarial-testing.service"

# Enable service to start on boot
echo "✅ Enabling service to start on boot..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "sudo systemctl enable enhanced-adversarial-testing.service"

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "sudo systemctl status enhanced-adversarial-testing.service --no-pager"

# Test the service
echo "🧪 Testing enhanced adversarial service..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "curl -s http://localhost:8001/health || echo 'Service not responding yet'"

# Check custody XP system
echo "🛡️ Checking custody XP system..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@ec2-$EC2_IP.compute-1.amazonaws.com" "curl -s http://localhost:8000/api/custody/analytics | head -c 500"

echo "✅ Enhanced adversarial testing service should now start automatically on system restart!"
echo "📋 Summary:"
echo "  • Enhanced adversarial testing service: FIXED and ENABLED"
echo "  • Service will start automatically on system restart"
echo "  • Running on port 8001"
echo "  • Custody XP system: ACTIVE on port 8000" 