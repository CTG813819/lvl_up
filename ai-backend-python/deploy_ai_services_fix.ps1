# Deploy AI Services Fix to Backend (PowerShell)
# This script fixes all AI services and ensures they work properly

Write-Host "Deploying AI Services Fix to Backend..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Yellow

# Server configuration
$SERVER = "ubuntu@34.202.215.209"
$KEY_PATH = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "~/ai-backend-python"

# Create backup of current backend
Write-Host "Creating backup of current backend..." -ForegroundColor Blue
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh -i $KEY_PATH $SERVER "cd ~; tar -czf ai-backend-backup-$timestamp.tar.gz ai-backend-python/"

# Upload the comprehensive fix script
Write-Host "Uploading comprehensive fix script..." -ForegroundColor Green
scp -i $KEY_PATH "fix_ai_services_comprehensive.py" "$SERVER`:$REMOTE_DIR/"

# Run the comprehensive fix on the server
Write-Host "Running comprehensive AI services fix..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "cd $REMOTE_DIR; python3 fix_ai_services_comprehensive.py"

# Upload the generated service files and scripts
Write-Host "Uploading generated service files..." -ForegroundColor Green
scp -i $KEY_PATH "imperium-ai.service" "$SERVER`:$REMOTE_DIR/"
scp -i $KEY_PATH "sandbox-ai.service" "$SERVER`:$REMOTE_DIR/"
scp -i $KEY_PATH "custodes-ai.service" "$SERVER`:$REMOTE_DIR/"
scp -i $KEY_PATH "guardian-ai.service" "$SERVER`:$REMOTE_DIR/"
scp -i $KEY_PATH "deploy_comprehensive_fix.sh" "$SERVER`:$REMOTE_DIR/"
scp -i $KEY_PATH "monitor_ai_services.sh" "$SERVER`:$REMOTE_DIR/"

# Execute the deployment script on the server
Write-Host "Executing deployment script on server..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "cd $REMOTE_DIR; chmod +x deploy_comprehensive_fix.sh; ./deploy_comprehensive_fix.sh"

# Check the status of all services
Write-Host "Checking service status..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "cd $REMOTE_DIR; chmod +x monitor_ai_services.sh; ./monitor_ai_services.sh"

Write-Host ""
Write-Host "AI Services Fix deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary of fixes applied:" -ForegroundColor Cyan
Write-Host "• Fixed Guardian sudo handling with fallback" -ForegroundColor White
Write-Host "• Added proper Python paths and virtual environment usage" -ForegroundColor White
Write-Host "• Enhanced error handling and logging" -ForegroundColor White
Write-Host "• Added service dependencies and startup order" -ForegroundColor White
Write-Host "• Implemented resource monitoring and health checks" -ForegroundColor White
Write-Host ""
Write-Host "Monitor services with:" -ForegroundColor Cyan
Write-Host "ssh -i $KEY_PATH $SERVER 'cd $REMOTE_DIR; ./monitor_ai_services.sh'" -ForegroundColor White
Write-Host ""
Write-Host "View individual service logs:" -ForegroundColor Cyan
Write-Host "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u imperium-ai.service -f'" -ForegroundColor White
Write-Host "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u sandbox-ai.service -f'" -ForegroundColor White
Write-Host "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u custodes-ai.service -f'" -ForegroundColor White
Write-Host "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u guardian-ai.service -f'" -ForegroundColor White 