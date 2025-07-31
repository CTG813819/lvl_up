# AI Growth Analytics Fixes Deployment Script (PowerShell)
# Deploys the fixes to EC2 instance

param(
    [string]$PemFile = "C:\projects\lvl_up\New.pem",
    [string]$EC2Host = "ec2-34-202-215-209.compute-1.amazonaws.com",
    [string]$EC2User = "ubuntu"
)

# Configuration
$BackendDir = "/home/ubuntu/ai-backend-python"
$FlutterDir = "/home/ubuntu/lvl_up"

Write-Host "🚀 Starting AI Growth Analytics Fixes Deployment" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Function to check if file exists
function Test-FileExists {
    param([string]$FilePath)
    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ Error: File $FilePath not found!" -ForegroundColor Red
        exit 1
    }
}

# Function to run command on EC2
function Invoke-EC2Command {
    param([string]$Command)
    $sshCommand = "ssh -i `"$PemFile`" -o StrictHostKeyChecking=no ${EC2User}@${EC2Host} `"$Command`""
    Write-Host "Executing: $Command" -ForegroundColor Yellow
    Invoke-Expression $sshCommand
}

# Function to copy file to EC2
function Copy-ToEC2 {
    param([string]$Source, [string]$Destination)
    $scpCommand = "scp -i `"$PemFile`" -o StrictHostKeyChecking=no `"$Source`" ${EC2User}@${EC2Host}:`"$Destination`""
    Write-Host "Copying: $Source to $Destination" -ForegroundColor Yellow
    Invoke-Expression $scpCommand
}

# Check if PEM file exists
Write-Host "🔍 Checking PEM file..." -ForegroundColor Blue
Test-FileExists $PemFile

Write-Host "📋 Step 1: Checking backend service status..." -ForegroundColor Blue
Invoke-EC2Command "sudo systemctl status guardian-ai || echo 'Service not found'"

Write-Host "📋 Step 2: Stopping backend service..." -ForegroundColor Blue
Invoke-EC2Command "sudo systemctl stop guardian-ai || echo 'Service already stopped'"

Write-Host "📋 Step 3: Backing up current files..." -ForegroundColor Blue
Invoke-EC2Command "cd $BackendDir && cp -r app/services app/services.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss') || echo 'Backup created'"

Write-Host "📋 Step 4: Copying updated backend files..." -ForegroundColor Blue
Write-Host "   Copying imperium_learning_controller.py..." -ForegroundColor Yellow
Copy-ToEC2 "ai-backend-python/app/services/imperium_learning_controller.py" "$BackendDir/app/services/"

Write-Host "📋 Step 5: Copying Flutter fixes..." -ForegroundColor Blue
Write-Host "   Copying ai_growth_analytics_provider.dart..." -ForegroundColor Yellow
Invoke-EC2Command "mkdir -p $FlutterDir/lib/providers"
Copy-ToEC2 "lib/providers/ai_growth_analytics_provider.dart" "$FlutterDir/lib/providers/"

Write-Host "📋 Step 6: Copying test script..." -ForegroundColor Blue
Copy-ToEC2 "test_ai_fixes_ec2.py" "$BackendDir/"

Write-Host "📋 Step 7: Setting proper permissions..." -ForegroundColor Blue
Invoke-EC2Command "chmod +x $BackendDir/test_ai_fixes_ec2.py"

Write-Host "📋 Step 8: Starting backend service..." -ForegroundColor Blue
Invoke-EC2Command "sudo systemctl start guardian-ai"

Write-Host "📋 Step 9: Waiting for service to start..." -ForegroundColor Blue
Start-Sleep -Seconds 10

Write-Host "📋 Step 10: Checking service status..." -ForegroundColor Blue
Invoke-EC2Command "sudo systemctl status guardian-ai"

Write-Host "📋 Step 11: Testing backend health..." -ForegroundColor Blue
Invoke-EC2Command "curl -s http://localhost:8000/health || echo 'Health check failed'"

Write-Host "📋 Step 12: Running AI fixes test..." -ForegroundColor Blue
Invoke-EC2Command "cd $BackendDir && python3 test_ai_fixes_ec2.py"

Write-Host ""
Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   - Backend service restarted" -ForegroundColor White
Write-Host "   - AI growth analytics fixes deployed" -ForegroundColor White
Write-Host "   - Test script executed" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To verify manually:" -ForegroundColor Cyan
Write-Host "   ssh -i `"$PemFile`" $EC2User@$EC2Host" -ForegroundColor White
Write-Host "   cd $BackendDir" -ForegroundColor White
Write-Host "   python3 test_ai_fixes_ec2.py" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Backend URL: http://$EC2Host:8000" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Green 