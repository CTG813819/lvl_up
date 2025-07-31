#!/bin/bash

echo "🚀 Deploying Enhanced Autonomous AI Learning System"
echo "=================================================="

# Set variables
EC2_IP="34.202.215.209"
KEY_PATH="C:/projects/lvl_up/New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

echo "📋 Step 1: Copying enhanced files to EC2..."

# Copy enhanced service
scp -i "$KEY_PATH" autonomous_subject_learning_service_enhanced.py ubuntu@$EC2_IP:$REMOTE_DIR/

# Copy monitoring script
scp -i "$KEY_PATH" monitor_enhanced_learning_comprehensive.py ubuntu@$EC2_IP:$REMOTE_DIR/

# Copy test script
scp -i "$KEY_PATH" test_enhanced_system.py ubuntu@$EC2_IP:$REMOTE_DIR/

# Copy service file
scp -i "$KEY_PATH" autonomous-learning-enhanced.service ubuntu@$EC2_IP:/tmp/

echo "✅ Files copied successfully!"

echo "📋 Step 2: Setting up enhanced service on EC2..."

# Update service and restart
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    echo "🔄 Stopping current service..."
    sudo systemctl stop autonomous-learning.service
    
    echo "📁 Updating service file..."
    sudo mv /tmp/autonomous-learning-enhanced.service /etc/systemd/system/autonomous-learning.service
    
    echo "🔄 Reloading systemd..."
    sudo systemctl daemon-reload
    
    echo "✅ Enabling enhanced service..."
    sudo systemctl enable autonomous-learning.service
    
    echo "🚀 Starting enhanced service..."
    sudo systemctl start autonomous-learning.service
    
    echo "📊 Checking service status..."
    sudo systemctl status autonomous-learning.service --no-pager
    
    echo "📋 Service setup complete!"
EOF

echo "✅ Enhanced service deployed!"

echo "📋 Step 3: Testing enhanced system..."

# Run test script
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    cd ~/ai-backend-python
    echo "🧪 Running enhanced system tests..."
    python test_enhanced_system.py
EOF

echo "📋 Step 4: Running comprehensive monitoring..."

# Run monitoring
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    cd ~/ai-backend-python
    echo "🔍 Running comprehensive monitoring..."
    python monitor_enhanced_learning_comprehensive.py
EOF

echo "📋 Step 5: Final verification..."

# Check service logs
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    echo "📋 Recent service logs:"
    sudo journalctl -u autonomous-learning.service --no-pager -n 20
    
    echo ""
    echo "📊 Service status:"
    sudo systemctl status autonomous-learning.service --no-pager
    
    echo ""
    echo "🎯 Enhanced system is now running!"
    echo "⏰ Learning cycles: Every hour"
    echo "📋 Proposals: Every 2 hours"
    echo "📁 File analysis: Every 4 hours"
    echo "🧠 AI subject addition: Every 6 hours"
    echo "🔄 Cross-AI sharing: Active"
    echo "📈 Enhanced growth: Active"
EOF

echo ""
echo "🎉 Enhanced Autonomous AI Learning System Deployment Complete!"
echo "=============================================================="
echo ""
echo "🚀 Your EC2 instance now runs a comprehensive autonomous AI system that:"
echo "   • Learns 5 subjects every hour"
echo "   • Generates proposals every 2 hours"
echo "   • Analyzes files every 4 hours"
echo "   • Adds new subjects every 6 hours"
echo "   • Shares knowledge between all AIs"
echo "   • Continuously improves backend and frontend"
echo "   • Grows intuitively with enhanced XP and prestige"
echo ""
echo "📊 Monitor the system with:"
echo "   ssh -i \"$KEY_PATH\" ubuntu@$EC2_IP \"cd ~/ai-backend-python && python monitor_enhanced_learning_comprehensive.py\""
echo ""
echo "🔍 Check service status with:"
echo "   ssh -i \"$KEY_PATH\" ubuntu@$EC2_IP \"sudo systemctl status autonomous-learning.service\""
echo ""
echo "📋 View real-time logs with:"
echo "   ssh -i \"$KEY_PATH\" ubuntu@$EC2_IP \"sudo journalctl -u autonomous-learning.service -f\""
echo ""
echo "🎯 The AIs will now continuously learn, grow, and improve your entire system!" 