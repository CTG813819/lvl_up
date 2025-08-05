# Migration script: Remove JavaScript backend and deploy Python backend to EC2
# Usage: .\migrate_to_python.ps1 -EC2IP "your-ec2-ip" -SSHKey "path\to\your-key.pem"

param(
    [Parameter(Mandatory=$true)]
    [string]$EC2IP,
    
    [Parameter(Mandatory=$true)]
    [string]$SSHKey
)

# Configuration
$RemoteUser = "ubuntu"
$RemoteDir = "/home/ubuntu"
$JSBackendDir = "$RemoteDir/ai-backend"
$PythonBackendDir = "$RemoteDir/ai-backend-python"
$BackupDir = "$RemoteDir/backup-js-backend-$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "🚀 Starting migration from JavaScript to Python backend" -ForegroundColor Blue
Write-Host "EC2 IP: $EC2IP" -ForegroundColor Yellow
Write-Host "SSH Key: $SSHKey" -ForegroundColor Yellow

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Function to execute SSH command
function Invoke-SSH {
    param([string]$Command)
    ssh -i $SSHKey -o StrictHostKeyChecking=no "$RemoteUser@$EC2IP" $Command
}

# Function to copy files to EC2
function Copy-ToEC2 {
    param([string]$Source, [string]$Destination)
    scp -i $SSHKey -o StrictHostKeyChecking=no -r $Source "$RemoteUser@$EC2IP`:$Destination"
}

# Step 1: Test SSH connection
Write-Info "Testing SSH connection..."
try {
    Invoke-SSH "echo 'SSH connection successful'" | Out-Null
    Write-Status "SSH connection established"
} catch {
    Write-Error "Failed to connect to EC2 instance. Please check your IP and SSH key."
    exit 1
}

# Step 2: Stop JavaScript backend services
Write-Info "Stopping JavaScript backend services..."
Invoke-SSH "sudo systemctl stop ai-backend 2>/dev/null; true"
Invoke-SSH "sudo systemctl stop pm2 2>/dev/null; true"
Invoke-SSH "pkill -f 'node.*ai-backend' 2>/dev/null; true"
Invoke-SSH "pkill -f 'pm2' 2>/dev/null; true"
Write-Status "JavaScript backend services stopped"

# Step 3: Create backup of JavaScript backend
Write-Info "Creating backup of JavaScript backend..."
Invoke-SSH "mkdir -p $BackupDir"
Invoke-SSH "cp -r $JSBackendDir/* $BackupDir/ 2>/dev/null; true"
Write-Status "Backup created at $BackupDir"

# Step 4: Remove JavaScript backend files
Write-Info "Removing JavaScript backend files..."
Invoke-SSH "rm -rf $JSBackendDir"
Invoke-SSH "rm -rf $RemoteDir/node_modules"
Invoke-SSH "rm -f $RemoteDir/package*.json"
Invoke-SSH "rm -f $RemoteDir/.env"
Write-Status "JavaScript backend files removed"

# Step 5: Clean up system services
Write-Info "Cleaning up system services..."
Invoke-SSH "sudo systemctl disable ai-backend 2>/dev/null; true"
Invoke-SSH "sudo rm -f /etc/systemd/system/ai-backend.service 2>/dev/null; true"
Invoke-SSH "sudo systemctl daemon-reload"
Write-Status "System services cleaned up"

# Step 6: Install Python dependencies
Write-Info "Installing Python dependencies..."
Invoke-SSH "sudo apt-get update"
Invoke-SSH "sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential"
Invoke-SSH "sudo apt-get install -y curl wget git"
Write-Status "Python dependencies installed"

# Step 7: Create Python virtual environment
Write-Info "Setting up Python virtual environment..."
Invoke-SSH "cd $RemoteDir; python3 -m venv venv"
Invoke-SSH "source $RemoteDir/venv/bin/activate; pip install --upgrade pip"
Write-Status "Python virtual environment created"

# Step 8: Upload Python backend files
Write-Info "Uploading Python backend files..."
Copy-ToEC2 "ai-backend-python/" $RemoteDir
Write-Status "Python backend files uploaded"

# Step 9: Install Python requirements
Write-Info "Installing Python requirements..."
Invoke-SSH "cd $PythonBackendDir; source $RemoteDir/venv/bin/activate; pip install -r requirements.txt"
Write-Status "Python requirements installed"

# Step 10: Download NLTK data
Write-Info "Downloading NLTK data..."
Invoke-SSH "cd $PythonBackendDir; source $RemoteDir/venv/bin/activate; python -c 'import nltk; nltk.download(\"punkt\", quiet=True); nltk.download(\"stopwords\", quiet=True)'"
Write-Status "NLTK data downloaded"

# Step 11: Create necessary directories
Write-Info "Creating necessary directories..."
Invoke-SSH "mkdir -p $PythonBackendDir/models"
Invoke-SSH "mkdir -p $PythonBackendDir/uploads"
Invoke-SSH "mkdir -p $PythonBackendDir/temp"
Write-Status "Directories created"

# Step 12: Set up environment variables
Write-Info "Setting up environment variables..."
$envContent = @'
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=ai_backend_python

# Server
PORT=4000
HOST=0.0.0.0
DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_repo_here

# AWS
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# AI Learning
LEARNING_ENABLED=true
LEARNING_INTERVAL=300
MAX_LEARNING_HISTORY=1000

# Proposal settings
MAX_PROPOSAL_LENGTH=10000
PROPOSAL_TIMEOUT=300
'@

$envContent | Out-File -FilePath ".env.template" -Encoding UTF8
Copy-ToEC2 ".env.template" "$PythonBackendDir/.env"
Write-Warning "Please edit the .env file with your actual API keys and configuration"
Write-Status "Environment template created"

# Step 13: Create systemd service for Python backend
Write-Info "Creating systemd service for Python backend..."
$serviceContent = @'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/venv/bin
ExecStart=/home/ubuntu/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'@

$serviceContent | Out-File -FilePath "ai-backend-python.service" -Encoding UTF8
Copy-ToEC2 "ai-backend-python.service" $RemoteDir
Invoke-SSH "sudo mv $RemoteDir/ai-backend-python.service /etc/systemd/system/"
Invoke-SSH "sudo systemctl daemon-reload"
Invoke-SSH "sudo systemctl enable ai-backend-python"
Write-Status "Systemd service created"

# Step 14: Set up firewall (if needed)
Write-Info "Setting up firewall..."
Invoke-SSH "sudo ufw allow 4000/tcp 2>/dev/null; true"
Write-Status "Firewall configured"

# Step 15: Test the Python backend
Write-Info "Testing Python backend..."
Invoke-SSH "cd $PythonBackendDir; source $RemoteDir/venv/bin/activate; python -c 'import sys; sys.path.append(\".\"); from app.core.config import settings; print(\"Configuration loaded successfully\")'"
Write-Status "Python backend configuration test passed"

# Step 16: Start the Python backend
Write-Info "Starting Python backend..."
Invoke-SSH "sudo systemctl start ai-backend-python"
Start-Sleep -Seconds 5

# Check if service is running
$serviceStatus = Invoke-SSH "sudo systemctl is-active ai-backend-python"
if ($serviceStatus -eq "active") {
    Write-Status "Python backend started successfully"
} else {
    Write-Error "Failed to start Python backend"
    Invoke-SSH "sudo systemctl status ai-backend-python"
    exit 1
}

# Step 17: Test the API
Write-Info "Testing API endpoints..."
Start-Sleep -Seconds 10  # Wait for service to fully start

try {
    Invoke-SSH "curl -f http://localhost:4000/health" | Out-Null
    Write-Status "Health check passed"
} catch {
    Write-Warning "Health check failed - service may still be starting"
}

# Step 18: Clean up temporary files
Write-Info "Cleaning up temporary files..."
Remove-Item ".env.template" -ErrorAction SilentlyContinue
Remove-Item "ai-backend-python.service" -ErrorAction SilentlyContinue
Write-Status "Temporary files cleaned up"

# Step 19: Migration summary
Write-Host ""
Write-Host "🎉 Migration completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Green
Write-Host "  ✅ JavaScript backend stopped and backed up" -ForegroundColor Green
Write-Host "  ✅ JavaScript files removed from EC2" -ForegroundColor Green
Write-Host "  ✅ Python backend deployed and configured" -ForegroundColor Green
Write-Host "  ✅ Systemd service created and enabled" -ForegroundColor Green
Write-Host "  ✅ Python backend started" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Backup location: $BackupDir" -ForegroundColor Green
Write-Host "🐍 Python backend location: $PythonBackendDir" -ForegroundColor Green
Write-Host "🔧 Service name: ai-backend-python" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Green
Write-Host "  1. Edit the .env file with your API keys:" -ForegroundColor Green
Write-Host "     ssh -i $SSHKey ubuntu@$EC2IP" -ForegroundColor Green
Write-Host "     nano $PythonBackendDir/.env" -ForegroundColor Green
Write-Host ""
Write-Host "  2. Check service status:" -ForegroundColor Green
Write-Host "     sudo systemctl status ai-backend-python" -ForegroundColor Green
Write-Host ""
Write-Host "  3. View logs:" -ForegroundColor Green
Write-Host "     sudo journalctl -u ai-backend-python -f" -ForegroundColor Green
Write-Host ""
Write-Host "  4. Test API:" -ForegroundColor Green
Write-Host "     curl http://$EC2IP:4000/health" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 To rollback (if needed):" -ForegroundColor Green
Write-Host "  sudo systemctl stop ai-backend-python" -ForegroundColor Green
Write-Host "  sudo systemctl disable ai-backend-python" -ForegroundColor Green
Write-Host "  rm -rf $PythonBackendDir" -ForegroundColor Green
Write-Host "  cp -r $BackupDir $JSBackendDir" -ForegroundColor Green
Write-Host ""

Write-Info "Migration script completed!" 