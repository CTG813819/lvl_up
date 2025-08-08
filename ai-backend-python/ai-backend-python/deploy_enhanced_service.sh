#!/bin/bash
echo "🔧 Deploying enhanced automatic custodes service..."

# Stop the old service if running
echo "🛑 Stopping old automatic custodes service..."
sudo systemctl stop automatic-custodes 2>/dev/null || true
sudo pkill -f "run_automatic_custodes_simple.py" 2>/dev/null || true

# Make the new service executable
chmod +x /home/ubuntu/ai-backend-python/enhanced_automatic_custodes_service.py

# Create systemd service file
sudo tee /etc/systemd/system/enhanced-automatic-custodes.service > /dev/null <<EOF
[Unit]
Description=Enhanced Automatic Custodes Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
ExecStart=/usr/bin/python3 /home/ubuntu/ai-backend-python/enhanced_automatic_custodes_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable enhanced-automatic-custodes
sudo systemctl start enhanced-automatic-custodes

# Check service status
echo "📊 Service status:"
sudo systemctl status enhanced-automatic-custodes --no-pager

echo "✅ Enhanced automatic custodes service deployed and started!"
echo "📋 Service will now test ALL AIs (imperium, guardian, conquest, sandbox) every hour"
echo "📋 Logs available at: /home/ubuntu/ai-backend-python/enhanced_custodes_service.log" 