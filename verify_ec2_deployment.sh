#!/bin/bash

# Verify EC2 Deployment Status
# Run this on your local machine to check what's deployed on EC2

echo "🔍 Verifying EC2 Deployment Status..."

# Test SSH connection and list files
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@34.202.215.209 << 'EOF'
echo "📁 Files in ai-backend-python directory:"
ls -la ~/ai-backend-python/ | grep -E "(autonomous|enhanced|migration|EC2_)"

echo ""
echo "📁 Files in app/services directory:"
ls -la ~/ai-backend-python/app/services/ | grep enhanced

echo ""
echo "📁 Files in app/models directory:"
ls -la ~/ai-backend-python/app/models/ | grep -E "(sql_models|training_data|oath_paper)"

echo ""
echo "📁 Files in app/routers directory:"
ls -la ~/ai-backend-python/app/routers/ | grep -E "(oath_papers|training_data)"

echo ""
echo "🔧 Setup script available:"
ls -la ~/ai-backend-python/setup_autonomous_learning_ec2.sh

echo ""
echo "📋 Next steps:"
echo "1. SSH to EC2: ssh -i 'C:\projects\lvl_up\New.pem' ubuntu@34.202.215.209"
echo "2. Run setup: cd ~/ai-backend-python && chmod +x setup_autonomous_learning_ec2.sh && ./setup_autonomous_learning_ec2.sh"
echo "3. Update API keys in ~/.bashrc"
echo "4. Monitor: sudo systemctl status autonomous-learning.service"
EOF 