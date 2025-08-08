#!/bin/bash

# Fix Conquest agent async context manager error
echo "🔧 Fixing Conquest agent async context manager error..."

# Set variables - UPDATE THESE WITH YOUR ACTUAL EC2 DETAILS
EC2_HOST="34.202.215.209"  # Replace with your actual EC2 IP
EC2_USER="ubuntu"
BACKEND_DIR="/home/ubuntu/ai-backend-python"
SSH_KEY_PATH="~/.ssh/New.pem"  # Replace with your actual key path

echo "📦 Deploying updated Conquest agent code..."
# Deploy the updated AI agent service with async context manager fixes
scp -i $SSH_KEY_PATH ai-backend-python/app/services/ai_agent_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/
scp -i $SSH_KEY_PATH ai-backend-python/app/services/conquest_ai_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

echo "🔧 Installing git on EC2 instance (if not already installed)..."
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

echo "🧪 Testing the fixes..."
# Test the fixes
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && python -c \"import subprocess; import shutil; print('Git available:', bool(shutil.which('git')))\""

echo "📋 Checking backend logs for errors..."
# Check recent logs for errors
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 30 logs/app.log | grep -E '(Error updating deployment status|Error pushing changes|AsyncGeneratorContextManager)' || echo 'No recent errors found'"

echo "🎉 Fix completed!"
echo "📋 Summary of fixes:"
echo "   - Fixed async context manager usage in Conquest agent"
echo "   - Updated all session handling to use 'async with get_session() as session'"
echo "   - Installed git on EC2 instance"
echo "   - Added proper error handling for git commands"
echo "   - Restarted backend services" 