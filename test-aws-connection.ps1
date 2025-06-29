# Test AWS SSH Connection
Write-Host "Testing SSH connection to AWS server..." -ForegroundColor Yellow

try {
    $result = ssh -i "C:\Users\Canice\.ssh\github_actions_deploy" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@44.204.184.21 "echo 'SSH connection successful!' && whoami && pwd"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSH connection successful!" -ForegroundColor Green
        Write-Host "Response: $result" -ForegroundColor Cyan
    } else {
        Write-Host "❌ SSH connection failed!" -ForegroundColor Red
        Write-Host "Make sure you've added the public key to ~/.ssh/authorized_keys on your AWS server" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ SSH connection failed with error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "If connection fails, make sure:" -ForegroundColor Yellow
Write-Host "1. The public key is added to ~/.ssh/authorized_keys on AWS" -ForegroundColor White
Write-Host "2. The AWS server is running and accessible" -ForegroundColor White
Write-Host "3. Your AWS security group allows SSH (port 22)" -ForegroundColor White 