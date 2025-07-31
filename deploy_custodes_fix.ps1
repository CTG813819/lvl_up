# Deploy the fixed automatic custodes service to EC2

Write-Host "🚀 Deploying fixed automatic custodes service..." -ForegroundColor Green

# Configuration
$EC2_HOST = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
$KEY_PATH = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "/home/ubuntu/ai-backend-python"
$LOCAL_FILES = @(
    "run_automatic_custodes_simple.py"
    "ai-backend-python/test_custody_endpoints.py"
)

# Copy the fixed files to EC2
Write-Host "📁 Copying fixed files to EC2..." -ForegroundColor Yellow
foreach ($file in $LOCAL_FILES) {
    Write-Host "   Copying $file..." -ForegroundColor Cyan
    scp -i $KEY_PATH $file "$EC2_HOST`:$REMOTE_DIR/"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to copy $file" -ForegroundColor Red
        exit 1
    }
}

# SSH into EC2 and restart the automatic custodes service
Write-Host "🔧 Restarting automatic custodes service..." -ForegroundColor Yellow
$sshCommand = @"
cd /home/ubuntu/ai-backend-python

# Stop the current automatic custodes service
echo "Stopping current automatic custodes service..."
sudo systemctl stop automatic-custodes.service

# Test the custody endpoints first
echo "Testing custody endpoints..."
python3 test_custody_endpoints.py

# Start the fixed automatic custodes service
echo "Starting fixed automatic custodes service..."
sudo systemctl start automatic-custodes.service

# Check service status
echo "Checking service status..."
sudo systemctl status automatic-custodes.service

# Show recent logs
echo "Recent logs:"
sudo journalctl -u automatic-custodes.service -n 20 --no-pager
"@

ssh -i $KEY_PATH $EC2_HOST $sshCommand

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Monitor the automatic custodes service logs:" -ForegroundColor White
Write-Host "   ssh -i $KEY_PATH $EC2_HOST" -ForegroundColor Gray
Write-Host "   sudo journalctl -u automatic-custodes.service -f" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Check custody analytics:" -ForegroundColor White
Write-Host "   curl http://localhost:8000/api/custody/analytics" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Force test an AI manually:" -ForegroundColor White
Write-Host "   curl -X POST http://localhost:8000/api/custody/test/imperium/force" -ForegroundColor Gray 