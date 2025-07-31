#!/bin/bash

# Deploy Proposal Validation Fix to EC2
# This script deploys the fixes for the "No meaningful changes detected" validation error

set -e

# Configuration
EC2_HOST="34.202.215.209"
EC2_USER="ubuntu"
REMOTE_PATH="/home/ubuntu/ai-backend"
LOCAL_PATH="ai-backend-python"
SSH_KEY="/home/ubuntu/ai-backend/New.pem"

echo "🚀 Deploying Proposal Validation Fix to EC2..."

# Check if we're in the right directory
if [ ! -d "$LOCAL_PATH" ]; then
    echo "❌ Error: $LOCAL_PATH directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "📁 Local path: $LOCAL_PATH"
echo "🌐 Remote host: $EC2_HOST"
echo "📂 Remote path: $REMOTE_PATH"

# Create backup of current deployment
echo "💾 Creating backup of current deployment..."
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "cd $REMOTE_PATH && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz ."

# Deploy the fixed files
echo "📤 Deploying fixed files..."

# Deploy the main AI agent service with fixes
scp -i "$SSH_KEY" "$LOCAL_PATH/app/services/ai_agent_service.py" "$EC2_USER@$EC2_HOST:$REMOTE_PATH/app/services/"

# Deploy test scripts
scp -i "$SSH_KEY" "$LOCAL_PATH/test_direct_code_analysis.py" "$EC2_USER@$EC2_HOST:$REMOTE_PATH/"
scp -i "$SSH_KEY" "$LOCAL_PATH/test_full_proposal_flow.py" "$EC2_USER@$EC2_HOST:$REMOTE_PATH/"

# Deploy the fix summary
scp -i "$SSH_KEY" "$LOCAL_PATH/PROPOSAL_VALIDATION_FIX_SUMMARY.md" "$EC2_USER@$EC2_HOST:$REMOTE_PATH/"

# Install missing dependency
echo "📦 Installing missing dependencies..."
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "cd $REMOTE_PATH && pip install beautifulsoup4"

# Restart the backend service
echo "🔄 Restarting backend service..."
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "sudo systemctl restart ai-backend"

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "sudo systemctl status ai-backend --no-pager"

# Test the deployment
echo "🧪 Testing deployment..."
ssh -i "$SSH_KEY" "$EC2_USER@$EC2_HOST" "cd $REMOTE_PATH && python test_direct_code_analysis.py"

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Summary:"
echo "  - Fixed AI agent proposal creation flow"
echo "  - Enhanced code analysis methods"
echo "  - Fixed validation service integration"
echo "  - Added test scripts for verification"
echo ""
echo "🔗 Backend URL: http://$EC2_HOST:8000"
echo "📋 Validation stats: http://$EC2_HOST:8000/api/proposals/validation/stats"
echo ""
echo "🎯 The proposal validation system should now work correctly!"
echo "   AI agents will generate meaningful code changes that pass validation." 