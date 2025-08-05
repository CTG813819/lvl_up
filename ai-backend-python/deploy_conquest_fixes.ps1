# PowerShell script to deploy Conquest AI fixes to EC2 instance
Write-Host "🚀 Deploying Conquest AI fixes to EC2 instance..." -ForegroundColor Green

# Set variables - UPDATE THESE WITH YOUR ACTUAL EC2 DETAILS
$EC2_HOST = "your-ec2-instance-ip"  # Replace with your actual EC2 IP
$EC2_USER = "ubuntu"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"
$FRONTEND_DIR = "/home/ubuntu/lvl_up"
$SSH_KEY_PATH = "~/.ssh/your-key.pem"  # Replace with your actual key path

Write-Host "📦 Deploying backend fixes..." -ForegroundColor Yellow
# Deploy backend fixes
scp -i $SSH_KEY_PATH ai-backend-python/app/services/conquest_ai_service.py ${EC2_USER}@${EC2_HOST}:${BACKEND_DIR}/app/services/

Write-Host "📱 Deploying frontend fixes..." -ForegroundColor Yellow
# Deploy frontend fixes
scp -i $SSH_KEY_PATH lib/screens/conquest_apps_screen.dart ${EC2_USER}@${EC2_HOST}:${FRONTEND_DIR}/lib/screens/
scp -i $SSH_KEY_PATH lib/mission_provider.dart ${EC2_USER}@${EC2_HOST}:${FRONTEND_DIR}/lib/
scp -i $SSH_KEY_PATH lib/services/conquest_ai_service.dart ${EC2_USER}@${EC2_HOST}:${FRONTEND_DIR}/lib/services/

Write-Host "🔄 Restarting backend services..." -ForegroundColor Yellow
# Restart backend services
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $BACKEND_DIR && sudo systemctl restart ai-backend-python && echo '✅ Backend restarted'"

Write-Host "🔨 Building frontend..." -ForegroundColor Yellow
# Build and deploy frontend
ssh -i $SSH_KEY_PATH ${EC2_USER}@${EC2_HOST} "cd $FRONTEND_DIR && flutter clean && flutter pub get && flutter build apk --release && echo '✅ Frontend built'"

Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host "📋 Summary of fixes:" -ForegroundColor Cyan
Write-Host "   - Removed filter text from Conquest AI statistics" -ForegroundColor White
Write-Host "   - Fixed GitHub progress integration for app completion status" -ForegroundColor White
Write-Host "   - Reduced notification and refresh frequency to prevent spam" -ForegroundColor White
Write-Host "   - Fixed unused variable warning" -ForegroundColor White 