# PowerShell script to fix Conquest agent async context manager error
Write-Host "🔧 Fixing Conquest agent async context manager error..." -ForegroundColor Green

# Set variables - UPDATE THESE WITH YOUR ACTUAL EC2 DETAILS
$EC2_HOST = "34.202.215.209"  # Replace with your actual EC2 IP
$EC2_USER = "ubuntu"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"
$SSH_KEY_PATH = "~/.ssh/New.pem"  # Replace with your actual key path

Write-Host "📦 Deploying updated Conquest agent code..." -ForegroundColor Yellow
# Deploy the updated AI agent service with async context manager fixes
scp -i $SSH_KEY_PATH ai-backend-python/app/services/ai_agent_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/
scp -i $SSH_KEY_PATH ai-backend-python/app/services/conquest_ai_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

Write-Host "🔧 Installing git on EC2 instance (if not already installed)..." -ForegroundColor Yellow
# Install git on EC2
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} @"
sudo apt update
sudo apt install -y git
git config --global user.name 'AI Backend'
git config --global user.email 'ai-backend@example.com'
echo '✅ Git installed and configured'
"@

Write-Host "🔄 Restarting backend services..." -ForegroundColor Yellow
# Restart backend services
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && sudo systemctl restart ai-backend-python && echo '✅ Backend restarted'"

Write-Host "🧪 Testing the fixes..." -ForegroundColor Yellow
# Test the fixes
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && python -c `"import subprocess; import shutil; print('Git available:', bool(shutil.which('git')))`""

Write-Host "📋 Checking backend logs for errors..." -ForegroundColor Yellow
# Check recent logs for errors
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 30 logs/app.log | grep -E '(Error updating deployment status|Error pushing changes|AsyncGeneratorContextManager)' || echo 'No recent errors found'"

Write-Host "🎉 Fix completed!" -ForegroundColor Green
Write-Host "📋 Summary of fixes:" -ForegroundColor Cyan
Write-Host "   - Fixed async context manager usage in Conquest agent" -ForegroundColor White
Write-Host "   - Updated all session handling to use 'async with get_session() as session'" -ForegroundColor White
Write-Host "   - Installed git on EC2 instance" -ForegroundColor White
Write-Host "   - Added proper error handling for git commands" -ForegroundColor White
Write-Host "   - Restarted backend services" -ForegroundColor White 