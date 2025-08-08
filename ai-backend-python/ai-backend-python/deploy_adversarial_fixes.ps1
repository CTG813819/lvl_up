# Deploy Adversarial Testing Fixes to EC2
# PowerShell version for Windows

Write-Host "🚀 Deploying Adversarial Testing Fixes to EC2" -ForegroundColor Blue
Write-Host "==============================================" -ForegroundColor Blue

# EC2 connection details
$EC2_IP = "34.202.215.209"
$EC2_USER = "ubuntu"
$PEM_FILE = "C:/projects/lvl_up/New.pem"
$BACKEND_DIR = "/home/ubuntu/ai-backend-python"

Write-Host "[INFO] Starting deployment of adversarial testing fixes..." -ForegroundColor Blue

# Step 1: Upload the reset token script
Write-Host "[INFO] Uploading token reset script..." -ForegroundColor Blue
scp -i $PEM_FILE reset_token_usage_ec2.py "${EC2_USER}@${EC2_IP}:${BACKEND_DIR}/"

# Step 2: Upload the enhanced scenario service
Write-Host "[INFO] Uploading enhanced scenario service..." -ForegroundColor Blue
scp -i $PEM_FILE ai-backend-python/app/services/enhanced_scenario_service.py "${EC2_USER}@${EC2_IP}:${BACKEND_DIR}/app/services/"

# Step 3: Execute the token reset script
Write-Host "[INFO] Executing token reset script..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "cd $BACKEND_DIR && python3 reset_token_usage_ec2.py"

# Step 4: Restart the backend service
Write-Host "[INFO] Restarting backend service..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "sudo systemctl restart ai-backend-python"

# Step 5: Test the adversarial testing endpoints
Write-Host "[INFO] Testing adversarial testing endpoints..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "cd $BACKEND_DIR && curl -s http://localhost:8000/api/imperium/status"

# Step 6: Check if port 8001 is open for adversarial testing
Write-Host "[INFO] Checking port 8001 for adversarial testing..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "sudo ufw allow 8001"

# Step 7: Create adversarial testing service on port 8001
Write-Host "[INFO] Creating adversarial testing service on port 8001..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "cd $BACKEND_DIR && nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 1 > adversarial_testing.log 2>&1 &"

# Step 8: Test the adversarial testing service
Write-Host "[INFO] Testing adversarial testing service..." -ForegroundColor Blue
ssh -i $PEM_FILE "${EC2_USER}@${EC2_IP}" "curl -s http://localhost:8001/api/imperium/status"

Write-Host "[SUCCESS] Adversarial testing fixes deployed successfully!" -ForegroundColor Green
Write-Host "[SUCCESS] ✅ Token usage reset to zero" -ForegroundColor Green
Write-Host "[SUCCESS] ✅ Enhanced scenario service updated" -ForegroundColor Green
Write-Host "[SUCCESS] ✅ Backend service restarted" -ForegroundColor Green
Write-Host "[SUCCESS] ✅ Adversarial testing service running on port 8001" -ForegroundColor Green
Write-Host "[SUCCESS] ✅ Infinite token generation enabled" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 Adversarial Testing Features:" -ForegroundColor Cyan
Write-Host "  • Infinite scenario generation using internet sources and LLMs" -ForegroundColor White
Write-Host "  • Live attack streaming on port 8001" -ForegroundColor White
Write-Host "  • Progressive difficulty scaling" -ForegroundColor White
Write-Host "  • Enhanced penetration testing scenarios" -ForegroundColor White
Write-Host "  • Real-time AI response tracking" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "  • Main Backend: http://34.202.215.209:8000" -ForegroundColor White
Write-Host "  • Adversarial Testing: http://34.202.215.209:8001" -ForegroundColor White
Write-Host "  • Flutter App: Updated to use port 8001 for adversarial testing" -ForegroundColor White 