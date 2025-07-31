#!/bin/bash
# Comprehensive AI Services Fix Deployment Script
echo "Deploying Comprehensive AI Services Fix..."

# Create log directories
echo "Creating log directories..."
mkdir -p /home/ubuntu/ai-backend-python/logs
mkdir -p /home/ubuntu/ai-backend-python/logs/imperium
mkdir -p /home/ubuntu/ai-backend-python/logs/sandbox
mkdir -p /home/ubuntu/ai-backend-python/logs/custodes
mkdir -p /home/ubuntu/ai-backend-python/logs/guardian

# Stop existing services
echo "Stopping existing services..."
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable services
echo "Disabling services..."
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
echo "Removing old service files..."
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Copy new service files
echo "Installing new systemd services..."
sudo cp imperium-ai.service /etc/systemd/system/
sudo cp sandbox-ai.service /etc/systemd/system/
sudo cp custodes-ai.service /etc/systemd/system/
sudo cp guardian-ai.service /etc/systemd/system/

# Set proper permissions
sudo chmod 644 /etc/systemd/system/imperium-ai.service
sudo chmod 644 /etc/systemd/system/sandbox-ai.service
sudo chmod 644 /etc/systemd/system/custodes-ai.service
sudo chmod 644 /etc/systemd/system/guardian-ai.service

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable services
echo "Enabling services..."
sudo systemctl enable imperium-ai.service
sudo systemctl enable sandbox-ai.service
sudo systemctl enable custodes-ai.service
sudo systemctl enable guardian-ai.service

# Start services
echo "Starting services..."
sudo systemctl start imperium-ai.service
sleep 5
sudo systemctl start sandbox-ai.service
sleep 5
sudo systemctl start custodes-ai.service
sleep 5
sudo systemctl start guardian-ai.service

# Check status
echo "Service Status:"
echo "==============="
echo "Imperium AI Service:"
sudo systemctl status imperium-ai.service --no-pager -l
echo ""
echo "Sandbox AI Service:"
sudo systemctl status sandbox-ai.service --no-pager -l
echo ""
echo "Custodes AI Service:"
sudo systemctl status custodes-ai.service --no-pager -l
echo ""
echo "Guardian AI Service:"
sudo systemctl status guardian-ai.service --no-pager -l

echo ""
echo "Comprehensive AI Services Fix deployed successfully!"
echo ""
echo "Configuration Summary:"
echo "• Imperium: Optimization every 45 minutes"
echo "• Sandbox: Experimentation every 45 minutes"
echo "• Custodes: Testing every 45 minutes (alternating comprehensive/regular)"
echo "• Guardian: Self-healing every 60 minutes (with sudo fallback)"
echo ""
echo "Monitor logs with:"
echo "sudo journalctl -u imperium-ai.service -f"
echo "sudo journalctl -u sandbox-ai.service -f"
echo "sudo journalctl -u custodes-ai.service -f"
echo "sudo journalctl -u guardian-ai.service -f"
echo ""
echo "Service logs also available at:"
echo "/home/ubuntu/ai-backend-python/logs/"
