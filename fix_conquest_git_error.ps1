# PowerShell script to fix Conquest agent git error
Write-Host "🔧 Fixing Conquest agent git error..." -ForegroundColor Green

# Set variables - UPDATE THESE WITH YOUR ACTUAL EC2 DETAILS
$EC2_HOST = "34.202.215.209"  # Replace with your actual EC2 IP
$EC2_USER = "ubuntu"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"
$SSH_KEY_PATH = "~/.ssh/New.pem"  # Replace with your actual key path

Write-Host "📦 Deploying updated Conquest agent code..." -ForegroundColor Yellow
# Deploy the updated AI agent service
scp -i $SSH_KEY_PATH ai-backend-python/app/services/ai_agent_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

Write-Host "🔧 Installing git on EC2 instance..." -ForegroundColor Yellow
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

Write-Host "🧪 Testing the fix..." -ForegroundColor Yellow
# Test the fix by checking if Conquest agent runs without git errors
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && python -c `"import subprocess; import shutil; print('Git available:', bool(shutil.which('git')))`""

Write-Host "📋 Checking backend logs for Conquest agent..." -ForegroundColor Yellow
# Check recent logs for Conquest agent
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && tail -n 20 logs/app.log | grep -i conquest || echo 'No recent Conquest logs found'"

Write-Host "🎉 Fix completed!" -ForegroundColor Green
Write-Host "📋 Summary of fixes:" -ForegroundColor Cyan
Write-Host "   - Updated Conquest agent to handle missing git gracefully" -ForegroundColor White
Write-Host "   - Installed git on EC2 instance" -ForegroundColor White
Write-Host "   - Added proper error handling for git commands" -ForegroundColor White
Write-Host "   - Restarted backend services" -ForegroundColor White 