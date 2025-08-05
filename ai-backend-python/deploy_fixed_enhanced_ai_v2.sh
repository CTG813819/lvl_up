#!/bin/bash
# Fixed Enhanced AI System V2 Deployment Script
echo "🚀 Deploying Fixed Enhanced AI System V2..."

# Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable old services
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Copy fixed service files
echo "📋 Installing fixed systemd services..."
sudo cp imperium-ai-fixed.service /etc/systemd/system/imperium-ai.service
sudo cp sandbox-ai-fixed.service /etc/systemd/system/sandbox-ai.service
sudo cp custodes-ai-fixed.service /etc/systemd/system/custodes-ai.service
sudo cp guardian-ai-fixed.service /etc/systemd/system/guardian-ai.service

# Reload systemd
sudo systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
sudo systemctl enable imperium-ai.service
sudo systemctl enable sandbox-ai.service
sudo systemctl enable custodes-ai.service
sudo systemctl enable guardian-ai.service

# Start services
echo "🚀 Starting services..."
sudo systemctl start imperium-ai.service
sudo systemctl start sandbox-ai.service
sudo systemctl start custodes-ai.service
sudo systemctl start guardian-ai.service

# Check status
echo "📊 Service Status:"
sudo systemctl status imperium-ai.service --no-pager -l
sudo systemctl status sandbox-ai.service --no-pager -l
sudo systemctl status custodes-ai.service --no-pager -l
sudo systemctl status guardian-ai.service --no-pager -l

echo "✅ Fixed Enhanced AI System V2 deployed successfully!"
echo ""
echo "📋 Configuration Summary:"
echo "• Imperium: 92% testing threshold, every 45 minutes"
echo "• Sandbox: 85% quality threshold, new code only, every 45 minutes"
echo "• Custodes: Comprehensive testing every 90 minutes, regular every 45 minutes"
echo "• Guardian: Self-healing every 60 minutes with sudo approval"
echo "• Autonomous Learning: 40+ AI-specific sources with daily additions"
echo ""
echo "🔍 Monitor logs with:"
echo "sudo journalctl -u imperium-ai.service -f"
echo "sudo journalctl -u sandbox-ai.service -f"
echo "sudo journalctl -u custodes-ai.service -f"
echo "sudo journalctl -u guardian-ai.service -f"
