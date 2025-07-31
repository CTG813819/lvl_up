# PowerShell script to copy deployment script to EC2
Write-Host "Copying deployment script to EC2 instance..." -ForegroundColor Green
Write-Host ""

# Configuration
$PemFile = "C:\projects\lvl_up\New.pem"
$Ec2Hostname = "ec2-34-202-215-209.compute-1.amazonaws.com"
$RemoteUser = "ubuntu"
$RemotePath = "/home/ubuntu/"

Write-Host "PEM File: $PemFile" -ForegroundColor Yellow
Write-Host "EC2 Hostname: $Ec2Hostname" -ForegroundColor Yellow
Write-Host "Remote User: $RemoteUser" -ForegroundColor Yellow
Write-Host "Remote Path: $RemotePath" -ForegroundColor Yellow
Write-Host ""

# Test SSH connection first
Write-Host "Testing SSH connection..." -ForegroundColor Cyan
try {
    $sshTest = ssh -i $PemFile "${RemoteUser}@${Ec2Hostname}" "echo 'SSH connection successful'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH connection successful!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: SSH connection failed" -ForegroundColor Red
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "1. The PEM file exists and has correct permissions" -ForegroundColor Yellow
        Write-Host "2. The EC2 hostname is correct" -ForegroundColor Yellow
        Write-Host "3. The EC2 instance is running" -ForegroundColor Yellow
        Write-Host "4. Your security group allows SSH access" -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
        exit 1
    }
} catch {
    Write-Host "ERROR: SSH connection failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""

# Copy the deployment script
Write-Host "Copying deploy_to_ec2.sh to EC2..." -ForegroundColor Cyan
try {
    $scpResult = scp -i $PemFile "deploy_to_ec2.sh" "${RemoteUser}@${Ec2Hostname}:${RemotePath}" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Deployment script copied to EC2!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: SCP copy failed" -ForegroundColor Red
        Write-Host $scpResult -ForegroundColor Red
        Read-Host "Press Enter to continue"
        exit 1
    }
} catch {
    Write-Host "ERROR: SCP copy failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. SSH to your EC2 instance: ssh -i `"$PemFile`" ${RemoteUser}@${Ec2Hostname}" -ForegroundColor Yellow
Write-Host "2. Navigate to backend: cd /home/ubuntu/ai-backend-python" -ForegroundColor Yellow
Write-Host "3. Run deployment: bash /home/ubuntu/deploy_to_ec2.sh" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue" 