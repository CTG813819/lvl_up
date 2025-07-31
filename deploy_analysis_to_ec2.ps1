# Deploy Comprehensive System Analysis to EC2
# PowerShell script to transfer the analysis script to EC2 and run it

# Configuration
$PEM_FILE = "C:\projects\lvl_up\New.pem"
$EC2_HOST = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
$REMOTE_DIR = "/home/ubuntu/ai-backend-python"
$LOCAL_SCRIPT = "comprehensive_system_analysis.py"
$REMOTE_SCRIPT = "comprehensive_system_analysis.py"

Write-Host "🚀 Deploying Comprehensive System Analysis to EC2..." -ForegroundColor Green
Write-Host "📁 PEM File: $PEM_FILE" -ForegroundColor Cyan
Write-Host "🌐 EC2 Host: $EC2_HOST" -ForegroundColor Cyan
Write-Host "📂 Remote Directory: $REMOTE_DIR" -ForegroundColor Cyan

# Check if PEM file exists
if (-not (Test-Path $PEM_FILE)) {
    Write-Host "❌ Error: PEM file not found at $PEM_FILE" -ForegroundColor Red
    exit 1
}

# Check if local script exists
if (-not (Test-Path $LOCAL_SCRIPT)) {
    Write-Host "❌ Error: Analysis script not found: $LOCAL_SCRIPT" -ForegroundColor Red
    exit 1
}

Write-Host "📤 Transferring analysis script to EC2..." -ForegroundColor Yellow

# Transfer the analysis script to EC2
try {
    $scpCommand = "scp -i `"$PEM_FILE`" `"$LOCAL_SCRIPT`" `"$EC2_HOST`":$REMOTE_DIR/"
    Write-Host "Executing: $scpCommand" -ForegroundColor Gray
    Invoke-Expression $scpCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Script transferred successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to transfer script" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error during transfer: $_" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Setting up environment on EC2..." -ForegroundColor Yellow

# SSH into EC2 and run the analysis
$sshCommands = @'
cd /home/ubuntu/ai-backend-python

echo "📋 Current directory: $(pwd)"
echo "📁 Directory contents:"
ls -la

echo "🐍 Checking Python version..."
python3 --version

echo "📦 Installing required packages..."
pip3 install ast pathlib typing datetime importlib inspect

echo "🔍 Running comprehensive system analysis..."
python3 comprehensive_system_analysis.py

echo "📄 Analysis complete! Checking for report file..."
ls -la *.json

echo "📊 Analysis results:"
if [ -f "comprehensive_system_analysis_report.json" ]; then
    echo "✅ Report generated successfully"
    echo "📋 Report size: $(du -h comprehensive_system_analysis_report.json | cut -f1)"
    echo "📄 First 500 characters of report:"
    head -c 500 comprehensive_system_analysis_report.json
    echo ""
else
    echo "❌ Report file not found"
fi
'@

try {
    $sshCommand = "ssh -i `"$PEM_FILE`" `"$EC2_HOST`" `"$sshCommands`""
    Write-Host "Executing SSH commands..." -ForegroundColor Gray
    Invoke-Expression $sshCommand
} catch {
    Write-Host "❌ Error during SSH execution: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment and analysis completed!" -ForegroundColor Green
Write-Host "📋 Check the EC2 instance for the analysis report" -ForegroundColor Cyan 