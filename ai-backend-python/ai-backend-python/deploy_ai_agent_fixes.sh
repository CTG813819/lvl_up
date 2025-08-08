#!/bin/bash

# Deploy AI Agent Fixes to EC2 Instance
# This script copies the fixed AI agent service files to the EC2 instance

set -e

# Configuration
EC2_HOST="ec2-54-147-131-102.compute-1.amazonaws.com"
EC2_USER="ubuntu"
EC2_KEY="~/.ssh/lvl_up_key.pem"
REMOTE_DIR="/home/ubuntu/lvl_up/ai-backend-python"
LOCAL_DIR="./ai-backend-python"

echo "🚀 Deploying AI Agent Fixes to EC2 Instance"
echo "=============================================="
echo "EC2 Host: $EC2_HOST"
echo "Remote Directory: $REMOTE_DIR"
echo ""

# Check if key file exists
if [ ! -f "${EC2_KEY/#\~/$HOME}" ]; then
    echo "❌ SSH key file not found: $EC2_KEY"
    exit 1
fi

# Copy the fixed AI agent service file
echo "📁 Copying fixed AI agent service file..."
scp -i "${EC2_KEY/#\~/$HOME}" \
    "$LOCAL_DIR/app/services/ai_agent_service.py" \
    "$EC2_USER@$EC2_HOST:$REMOTE_DIR/app/services/"

echo "✅ AI agent service file copied"

# Copy the test script
echo "📁 Copying test script..."
scp -i "${EC2_KEY/#\~/$HOME}" \
    "$LOCAL_DIR/patch_for_meaningful_proposals.py" \
    "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

echo "✅ Test script copied"

# Copy the comprehensive test script
echo "📁 Copying comprehensive test script..."
scp -i "${EC2_KEY/#\~/$HOME}" \
    "$LOCAL_DIR/test_force_meaningful_proposals.py" \
    "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

echo "✅ Comprehensive test script copied"

# Restart the backend service
echo "🔄 Restarting backend service..."
ssh -i "${EC2_KEY/#\~/$HOME}" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/lvl_up/ai-backend-python
    sudo systemctl restart lvl_up_backend
    echo "✅ Backend service restarted"
    
    # Wait a moment for the service to start
    sleep 5
    
    # Check service status
    sudo systemctl status lvl_up_backend --no-pager -l
EOF

echo ""
echo "🎯 Deployment completed!"
echo ""
echo "Next steps:"
echo "1. SSH into the EC2 instance:"
echo "   ssh -i $EC2_KEY $EC2_USER@$EC2_HOST"
echo ""
echo "2. Run the test script to verify fixes:"
echo "   cd $REMOTE_DIR"
echo "   python3 patch_for_meaningful_proposals.py"
echo ""
echo "3. Check the logs for AI agent activity:"
echo "   sudo journalctl -u lvl_up_backend -f"
echo ""
echo "4. Monitor the database for new proposals:"
echo "   python3 -c \"from app.core.database import get_session; from app.models.sql_models import Proposal; from sqlalchemy import select; import asyncio; async def check(): async with get_session() as session: result = await session.execute(select(Proposal).order_by(Proposal.created_at.desc()).limit(5)); proposals = result.scalars().all(); print(f'Recent proposals: {len(proposals)}'); asyncio.run(check())\"" 