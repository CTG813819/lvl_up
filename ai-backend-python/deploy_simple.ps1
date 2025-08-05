# Simple deployment script for comprehensive fixes
Write-Host "🚀 Deploying comprehensive fixes to EC2..." -ForegroundColor Green

# EC2 instance details
$EC2_HOST = "ec2-54-147-131-199.compute-1.amazonaws.com"
$EC2_USER = "ubuntu"
$KEY_FILE = "lvl_up_key.pem"

# Check if key file exists
if (-not (Test-Path $KEY_FILE)) {
    Write-Host "❌ SSH key file not found: $KEY_FILE" -ForegroundColor Red
    Write-Host "📝 Please ensure the SSH key is in the current directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Transferring files to EC2..." -ForegroundColor Green

# Transfer files one by one
$files = @("diverse_test_generator.py", "improved_scoring_system.py", "app/services/custody_protocol_service.py")

foreach ($file in $files) {
    if (Test-Path $file) {
        $scpCmd = "scp -i `"$KEY_FILE`" -o StrictHostKeyChecking=no $file $EC2_USER@$EC2_HOST`:/home/ubuntu/ai-backend-python/"
        Write-Host "Transferring $file..." -ForegroundColor Gray
        Invoke-Expression $scpCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $file transferred successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to transfer $file" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️  File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "🔧 Restarting backend service..." -ForegroundColor Green

# Create a temporary script file for SSH commands
$sshScript = @"
cd /home/ubuntu/ai-backend-python
echo "🛑 Stopping backend service..."
sudo systemctl stop ai-backend-python
echo "⏳ Waiting for service to stop..."
sleep 5
echo "🚀 Starting backend service..."
sudo systemctl start ai-backend-python
echo "⏳ Waiting for service to start..."
sleep 10
echo "📊 Checking service status..."
sudo systemctl status ai-backend-python --no-pager
echo "📋 Recent logs:"
sudo journalctl -u ai-backend-python -n 20 --no-pager
"@

$sshScript | Out-File -FilePath "temp_ssh_commands.sh" -Encoding ASCII
$sshCmd = "ssh -i `"$KEY_FILE`" -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST `"bash -s` < temp_ssh_commands.sh"

Write-Host "Executing SSH commands..." -ForegroundColor Gray
Invoke-Expression $sshCmd

# Clean up
Remove-Item "temp_ssh_commands.sh" -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "📝 Monitoring deployment..." -ForegroundColor Yellow
    
    # Monitor logs
    Write-Host "📊 Monitoring recent logs..." -ForegroundColor Green
    $monitorScript = @"
echo "📋 Latest logs (last 30 seconds):"
sudo journalctl -u ai-backend-python --since "30 seconds ago" --no-pager
echo "🔍 Checking for diverse test generation..."
sudo journalctl -u ai-backend-python --no-pager | grep -i "diverse" | tail -5
echo "🔍 Checking for XP display fixes..."
sudo journalctl -u ai-backend-python --no-pager | grep -i "XP" | tail -5
"@
    
    $monitorScript | Out-File -FilePath "temp_monitor_commands.sh" -Encoding ASCII
    $monitorCmd = "ssh -i `"$KEY_FILE`" -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST `"bash -s` < temp_monitor_commands.sh"
    Invoke-Expression $monitorCmd
    Remove-Item "temp_monitor_commands.sh" -ErrorAction SilentlyContinue
    
    Write-Host "🎉 Deployment and monitoring completed!" -ForegroundColor Green
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Monitor logs for diverse test generation" -ForegroundColor White
    Write-Host "   2. Verify XP display is correct" -ForegroundColor White
    Write-Host "   3. Check for varied test scores (not 40.01)" -ForegroundColor White
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "📝 Please check the error messages above" -ForegroundColor Yellow
} 