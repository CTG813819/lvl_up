# Deploy AI Agent Fixes to EC2 Instance
# This script copies the fixed AI agent service files to the EC2 instance

# Configuration
$EC2_HOST = "ec2-54-147-131-102.compute-1.amazonaws.com"
$EC2_USER = "ubuntu"
$EC2_KEY = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "/home/ubuntu/lvl_up/ai-backend-python"
$LOCAL_DIR = "./ai-backend-python"

Write-Host "🚀 Deploying AI Agent Fixes to EC2 Instance" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host "EC2 Host: $EC2_HOST" -ForegroundColor Yellow
Write-Host "Remote Directory: $REMOTE_DIR" -ForegroundColor Yellow
Write-Host ""

# Check if key file exists
if (-not (Test-Path $EC2_KEY)) {
    Write-Host "❌ SSH key file not found: $EC2_KEY" -ForegroundColor Red
    exit 1
}

# Copy the fixed AI agent service file
Write-Host "📁 Copying fixed AI agent service file..." -ForegroundColor Cyan
scp -i $EC2_KEY `
    "$LOCAL_DIR/app/services/ai_agent_service.py" `
    "$EC2_USER@$EC2_HOST`:$REMOTE_DIR/app/services/"

Write-Host "✅ AI agent service file copied" -ForegroundColor Green

# Copy the test script
Write-Host "📁 Copying test script..." -ForegroundColor Cyan
scp -i $EC2_KEY `
    "$LOCAL_DIR/patch_for_meaningful_proposals.py" `
    "$EC2_USER@$EC2_HOST`:$REMOTE_DIR/"

Write-Host "✅ Test script copied" -ForegroundColor Green

# Copy the comprehensive test script
Write-Host "📁 Copying comprehensive test script..." -ForegroundColor Cyan
scp -i $EC2_KEY `
    "$LOCAL_DIR/test_force_meaningful_proposals.py" `
    "$EC2_USER@$EC2_HOST`:$REMOTE_DIR/"

Write-Host "✅ Comprehensive test script copied" -ForegroundColor Green

# Restart the backend service
Write-Host "🔄 Restarting backend service..." -ForegroundColor Cyan
$restartCommand = @"
cd /home/ubuntu/lvl_up/ai-backend-python
sudo systemctl restart lvl_up_backend
echo "✅ Backend service restarted"

# Wait a moment for the service to start
sleep 5

# Check service status
sudo systemctl status lvl_up_backend --no-pager -l
"@

ssh -i $EC2_KEY "$EC2_USER@$EC2_HOST" $restartCommand

Write-Host ""
Write-Host "🎯 Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. SSH into the EC2 instance:" -ForegroundColor White
Write-Host "   ssh -i $EC2_KEY $EC2_USER@$EC2_HOST" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run the test script to verify fixes:" -ForegroundColor White
Write-Host "   cd $REMOTE_DIR" -ForegroundColor Gray
Write-Host "   python3 patch_for_meaningful_proposals.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Check the logs for AI agent activity:" -ForegroundColor White
Write-Host "   sudo journalctl -u lvl_up_backend -f" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Monitor the database for new proposals:" -ForegroundColor White
Write-Host "   python3 -c `"from app.core.database import get_session; from app.models.sql_models import Proposal; from sqlalchemy import select; import asyncio; async def check(): async with get_session() as session: result = await session.execute(select(Proposal).order_by(Proposal.created_at.desc()).limit(5)); proposals = result.scalars().all(); print(f'Recent proposals: {len(proposals)}'); asyncio.run(check())`"" -ForegroundColor Gray 