#!/bin/bash

# Deploy Token Usage Limits to EC2 Instance
# This script updates the token usage system to enforce strict limits

set -e

# Configuration
REMOTE_HOST="ubuntu@your-ec2-instance.com"
REMOTE_DIR="/home/ubuntu/ai-backend-python"
BACKUP_DIR="/home/ubuntu/backups/token_limits_$(date +%Y%m%d_%H%M%S)"

echo "🚀 Deploying Token Usage Limits to EC2 Instance"
echo "================================================"

# Step 1: Create backup
echo "📦 Creating backup..."
ssh $REMOTE_HOST "mkdir -p $BACKUP_DIR"
ssh $REMOTE_HOST "cp -r $REMOTE_DIR/app/services/token_usage_service.py $BACKUP_DIR/"
ssh $REMOTE_HOST "cp -r $REMOTE_DIR/app/services/anthropic_service.py $BACKUP_DIR/"
echo "✅ Backup created at $BACKUP_DIR"

# Step 2: Deploy updated token usage service
echo "📤 Deploying updated token usage service..."
scp ai-backend-python/app/services/token_usage_service.py $REMOTE_HOST:$REMOTE_DIR/app/services/
scp ai-backend-python/app/services/anthropic_service.py $REMOTE_HOST:$REMOTE_DIR/app/services/
echo "✅ Token usage service deployed"

# Step 3: Deploy monitoring scripts
echo "📤 Deploying monitoring scripts..."
scp ai-backend-python/monitor_token_usage.py $REMOTE_HOST:$REMOTE_DIR/
scp ai-backend-python/reset_token_usage.py $REMOTE_HOST:$REMOTE_DIR/
scp ai-backend-python/TOKEN_USAGE_LIMITS.md $REMOTE_HOST:$REMOTE_DIR/
echo "✅ Monitoring scripts deployed"

# Step 4: Make scripts executable
echo "🔧 Making scripts executable..."
ssh $REMOTE_HOST "chmod +x $REMOTE_DIR/monitor_token_usage.py"
ssh $REMOTE_HOST "chmod +x $REMOTE_DIR/reset_token_usage.py"
echo "✅ Scripts made executable"

# Step 5: Restart backend service
echo "🔄 Restarting backend service..."
ssh $REMOTE_HOST "sudo systemctl restart ai-backend-python"
echo "✅ Backend service restarted"

# Step 6: Initialize token usage tracking
echo "🔧 Initializing token usage tracking..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python -c \"import asyncio; from app.services.token_usage_service import token_usage_service; from app.core.database import init_database; asyncio.run(init_database()); asyncio.run(token_usage_service._setup_monthly_tracking()); print('Token tracking initialized')\""
echo "✅ Token usage tracking initialized"

# Step 7: Show current status
echo "📊 Current token usage status..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python reset_token_usage.py"

# Step 8: Start monitoring (optional)
echo ""
echo "🎯 Token Usage Limits Deployed Successfully!"
echo "============================================="
echo ""
echo "📊 To monitor usage in real-time:"
echo "   ssh $REMOTE_HOST"
echo "   cd $REMOTE_DIR"
echo "   python monitor_token_usage.py"
echo ""
echo "📋 To check current usage:"
echo "   ssh $REMOTE_HOST"
echo "   cd $REMOTE_DIR"
echo "   python reset_token_usage.py"
echo ""
echo "🔄 To reset usage (for testing):"
echo "   ssh $REMOTE_HOST"
echo "   cd $REMOTE_DIR"
echo "   python reset_token_usage.py reset"
echo ""
echo "📖 Documentation: TOKEN_USAGE_LIMITS.md"
echo ""
echo "🚨 The system will now enforce strict token limits:"
echo "   - Monthly limit: 140,000 tokens (70% of 200,000)"
echo "   - Warning at 80% (112,000 tokens)"
echo "   - Critical at 95% (133,000 tokens)"
echo "   - Emergency shutdown at 98% (137,200 tokens)"
echo ""
echo "✅ Deployment complete!" 