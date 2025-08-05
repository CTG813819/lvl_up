#!/bin/bash
# Deploy Optimized AI Backend
echo "🚀 Deploying Optimized AI Backend..."

# Stop old services
echo "🛑 Stopping old services..."
sudo systemctl stop ai-backend-integrated.service 2>/dev/null || true
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable old services
sudo systemctl disable ai-backend-integrated.service 2>/dev/null || true
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
sudo rm -f /etc/systemd/system/ai-backend-integrated.service
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Install optimized backend service
echo "📋 Installing optimized backend service..."
sudo cp ai-backend-optimized.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start optimized service
echo "✅ Starting optimized backend..."
sudo systemctl enable ai-backend-optimized.service
sudo systemctl start ai-backend-optimized.service

# Check status
echo "📊 Service Status:"
sudo systemctl status ai-backend-optimized.service --no-pager -l

echo "✅ Optimized AI Backend deployed successfully!"
echo ""
echo "📋 Performance Optimizations Applied:"
echo "• Imperium: Every 3 hours (was 45 minutes)"
echo "• Sandbox: Every 4 hours (was 45 minutes)"
echo "• Custodes: Every 3 hours (was 45 minutes)"
echo "• Guardian: Every 8 hours (was 60 minutes)"
echo "• Resource monitoring: CPU/Memory limits"
echo "• Manual trigger: Available for immediate runs"
echo ""
echo "🔍 API Endpoints:"
echo "• GET  /ai-agents/status - Check status with resource metrics"
echo "• POST /ai-agents/start - Start optimized agents"
echo "• POST /ai-agents/stop - Stop agents"
echo "• POST /ai-agents/manual-run/{agent} - Manual trigger"
echo ""
echo "📊 Monitor with:"
echo "sudo journalctl -u ai-backend-optimized.service -f"
