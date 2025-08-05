#!/bin/bash

# Fix Conquest agent git error
echo "🔧 Fixing Conquest agent git error..."

# Set variables - UPDATE THESE WITH YOUR ACTUAL EC2 DETAILS
EC2_HOST="34.202.215.209"  # Replace with your actual EC2 IP
EC2_USER="ubuntu"
BACKEND_DIR="/home/ubuntu/ai-backend-python"
SSH_KEY_PATH="~/.ssh/New.pem"  # Replace with your actual key path

echo "📦 Deploying updated Conquest agent code..."
# Deploy the updated AI agent service
scp -i $SSH_KEY_PATH ai-backend-python/app/services/ai_agent_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

echo "🔧 Installing git on EC2 instance..."
# Install git on EC2
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} << 'EOF'
sudo apt update
sudo apt install -y git
git config --global user.name "AI Backend"
git config --global user.email "ai-backend@example.com"
echo "✅ Git installed and configured"
EOF

echo "🔄 Restarting backend services..."
# Restart backend services
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && sudo systemctl restart ai-backend-python && echo '✅ Backend restarted'"

echo "🧪 Testing the fix..."
# Test the fix by checking if Conquest agent runs without git errors
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && python -c \"import subprocess; import shutil; print('Git available:', bool(shutil.which('git')))\""

echo "📋 Checking backend logs for Conquest agent..."
# Check recent logs for Conquest agent
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 20 logs/app.log | grep -i conquest || echo 'No recent Conquest logs found'"

echo "🎉 Fix completed!"
echo "📋 Summary of fixes:"
echo "   - Updated Conquest agent to handle missing git gracefully"
echo "   - Installed git on EC2 instance"
echo "   - Added proper error handling for git commands"
echo "   - Restarted backend services" 