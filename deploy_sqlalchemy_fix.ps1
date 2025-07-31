# Deploy SQLAlchemy Fix to EC2
# Fixes the _static_cache_key error by upgrading SQLAlchemy

Write-Host "🚀 Deploying SQLAlchemy fix to EC2..." -ForegroundColor Green

# Configuration
$EC2_HOST = "34.202.215.209"
$EC2_USER = "ubuntu"
$REMOTE_DIR = "/home/ubuntu/ai-backend-python"
$LOCAL_SCRIPT = "fix_sqlalchemy_static_cache_key.py"

Write-Host "📦 Copying SQLAlchemy fix script to EC2..." -ForegroundColor Yellow

# Copy the fix script to EC2
$scpCommand = "scp -o StrictHostKeyChecking=no $LOCAL_SCRIPT ${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/"
Write-Host "Executing: $scpCommand" -ForegroundColor Gray

$scpResult = Invoke-Expression $scpCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Script copied successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to copy script" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Running SQLAlchemy fix on EC2..." -ForegroundColor Yellow

# SSH into EC2 and run the fix
$sshCommands = @"
cd /home/ubuntu/ai-backend-python

echo "🔍 Checking current SQLAlchemy version..."
python3 -c "import sqlalchemy; print(f'Current: {sqlalchemy.__version__}')"

echo "📦 Upgrading SQLAlchemy..."
pip3 uninstall sqlalchemy -y --break-system-packages
pip3 install sqlalchemy==2.0.23 --break-system-packages

echo "🔄 Restarting backend service..."
sudo systemctl stop ultimate_start
sleep 3
sudo systemctl start ultimate_start

echo "⏳ Waiting for service to stabilize..."
sleep 10

echo "🔍 Checking service status..."
sudo systemctl status ultimate_start --no-pager

echo "🔍 Checking recent logs for _static_cache_key errors..."
sudo journalctl -u ultimate_start --since "2 minutes ago" --no-pager | grep -i "_static_cache_key" || echo "✅ No _static_cache_key errors found in recent logs"

echo "✅ SQLAlchemy fix completed!"
"@

$sshCommand = "ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '$sshCommands'"
Write-Host "Executing SSH fix..." -ForegroundColor Gray

$sshResult = Invoke-Expression $sshCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 SQLAlchemy fix deployed and executed successfully!" -ForegroundColor Green
    Write-Host "📊 The _static_cache_key error should now be resolved" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to execute SQLAlchemy fix on EC2" -ForegroundColor Red
    exit 1
}

Write-Host "📄 Check the EC2 logs for any remaining issues" -ForegroundColor Yellow
Write-Host "🔗 You can monitor the service with: ssh ${EC2_USER}@${EC2_HOST} 'sudo journalctl -u ultimate_start -f'" -ForegroundColor Cyan 