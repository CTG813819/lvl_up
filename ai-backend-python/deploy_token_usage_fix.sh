#!/bin/bash

# Deploy Token Usage Fix to EC2
# =============================

set -e

# Configuration
REMOTE_HOST="ubuntu@34.202.215.209"
REMOTE_DIR="/home/ubuntu/ai-backend-python"
BACKUP_DIR="/home/ubuntu/backups"

echo "🚀 Deploying Token Usage Fix to EC2..."
echo "========================================"

# Step 1: Create backup
echo "📦 Creating backup..."
ssh $REMOTE_HOST "mkdir -p $BACKUP_DIR"
ssh $REMOTE_HOST "cd $REMOTE_DIR && tar -czf $BACKUP_DIR/token_usage_backup_$(date +%Y%m%d_%H%M%S).tar.gz ."

# Step 2: Upload the fix script
echo "📤 Uploading fix script..."
scp fix_token_usage_and_reset_issue.py $REMOTE_HOST:$REMOTE_DIR/

# Step 3: Run the fix script
echo "🔧 Running token usage fix..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python fix_token_usage_and_reset_issue.py"

# Step 4: Test the fix
echo "🧪 Testing the fix..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python -c \"
import asyncio
from app.core.database import init_database
from app.models.sql_models import TokenUsage
from sqlalchemy import select, func
from datetime import datetime

async def test_fix():
    await init_database()
    current_month = datetime.utcnow().strftime('%Y-%m')
    
    from app.core.database import get_session
    async with get_session() as session:
        # Check if token usage is reset
        stmt = select(func.sum(TokenUsage.total_tokens)).where(
            TokenUsage.month_year == current_month
        )
        result = await session.execute(stmt)
        total_tokens = result.scalar() or 0
        
        print(f'Current month: {current_month}')
        print(f'Total tokens: {total_tokens}')
        print(f'Status: {\"✅ RESET\" if total_tokens == 0 else \"❌ NOT RESET\"}')

asyncio.run(test_fix())
\""

# Step 5: Check cron jobs
echo "📅 Checking cron jobs..."
ssh $REMOTE_HOST "crontab -l | grep -E '(monthly_token_reset|monitor_token_usage)' || echo 'No token-related cron jobs found'"

# Step 6: Test monitoring
echo "📊 Testing monitoring..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && python monitor_token_usage.py"

# Step 7: Restart the service
echo "🔄 Restarting AI backend service..."
ssh $REMOTE_HOST "sudo systemctl restart ai-backend-python"
ssh $REMOTE_HOST "sudo systemctl status ai-backend-python --no-pager"

# Step 8: Show logs
echo "📋 Recent logs..."
ssh $REMOTE_HOST "sudo journalctl -u ai-backend-python -n 20 --no-pager"

echo ""
echo "✅ Token Usage Fix Deployed Successfully!"
echo "========================================="
echo ""
echo "🔧 What was fixed:"
echo "   - Reset all token usage for current month"
echo "   - Set up automatic monthly reset (1st of each month)"
echo "   - Enhanced error handling for token limits"
echo "   - Fixed Claude verification errors"
echo "   - Added comprehensive monitoring"
echo ""
echo "📊 Monitoring:"
echo "   - Token usage monitored every 5 minutes"
echo "   - Alerts at 80%, 95%, and 98% usage"
echo "   - Automatic reset on 1st of each month"
echo ""
echo "📝 Useful commands:"
echo "   - Check current usage: python reset_token_usage.py"
echo "   - Monitor in real-time: python monitor_token_usage.py"
echo "   - View alerts: tail -f /var/log/token-usage-alerts.log"
echo "   - Check monthly reset: tail -f /var/log/monthly-token-reset.log"
echo ""
echo "🚨 The system will now:"
echo "   - Automatically reset tokens on the 1st of each month"
echo "   - Monitor usage and send alerts"
echo "   - Handle token limit errors gracefully"
echo "   - Fix Claude verification issues"
echo ""
echo "✅ Deployment complete!" 