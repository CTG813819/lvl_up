Write-Host "Deploying comprehensive fixes to EC2..." -ForegroundColor Green

$EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
$EC2_USER = "ubuntu"
$KEY_FILE = "C:\projects\lvl_up\New.pem"

if (-not (Test-Path $KEY_FILE)) {
    Write-Host "SSH key file not found: $KEY_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "Transferring files to EC2..." -ForegroundColor Green

$files = @("diverse_test_generator.py", "improved_scoring_system.py", "app/services/custody_protocol_service.py")

foreach ($file in $files) {
    if (Test-Path $file) {
        $scpCmd = "scp -i `"$KEY_FILE`" -o StrictHostKeyChecking=no $file $EC2_USER@$EC2_HOST`:/home/ubuntu/ai-backend-python/"
        Write-Host "Transferring $file..." -ForegroundColor Gray
        Invoke-Expression $scpCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$file transferred successfully" -ForegroundColor Green
        } else {
            Write-Host "Failed to transfer $file" -ForegroundColor Red
        }
    } else {
        Write-Host "File not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "Restarting backend service..." -ForegroundColor Green

$sshCmd = "ssh -i `"$KEY_FILE`" -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST"

Write-Host "Stopping backend service..." -ForegroundColor Yellow
$stopCmd = "$sshCmd 'sudo systemctl stop ai-backend-python'"
Invoke-Expression $stopCmd

Start-Sleep -Seconds 5

Write-Host "Starting backend service..." -ForegroundColor Yellow
$startCmd = "$sshCmd 'sudo systemctl start ai-backend-python'"
Invoke-Expression $startCmd

Start-Sleep -Seconds 10

Write-Host "Checking service status..." -ForegroundColor Yellow
$statusCmd = "$sshCmd 'sudo systemctl status ai-backend-python --no-pager'"
Invoke-Expression $statusCmd

Write-Host "Recent logs:" -ForegroundColor Yellow
$logsCmd = "$sshCmd 'sudo journalctl -u ai-backend-python -n 20 --no-pager'"
Invoke-Expression $logsCmd

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Monitor logs for diverse test generation" -ForegroundColor White
Write-Host "2. Verify XP display is correct" -ForegroundColor White
Write-Host "3. Check for varied test scores" -ForegroundColor White 