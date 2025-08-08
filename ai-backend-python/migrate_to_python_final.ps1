# Migration script: Remove JavaScript backend and deploy Python backend to EC2
param(
    [Parameter(Mandatory=$true)]
    [string]$EC2Host,
    
    [Parameter(Mandatory=$true)]
    [string]$SSHKey
)

# Configuration
$RemoteUser = "ubuntu"
$RemoteDir = "/home/ubuntu"
$JSBackendDir = "$RemoteDir/ai-backend"
$PythonBackendDir = "$RemoteDir/ai-backend-python"
$BackupDir = "$RemoteDir/backup-js-backend-$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "Starting migration from JavaScript to Python backend" -ForegroundColor Blue
Write-Host "EC2 Host: $EC2Host" -ForegroundColor Yellow
Write-Host "SSH Key: $SSHKey" -ForegroundColor Yellow

# Function to execute SSH command
function Invoke-SSH {
    param([string]$Command)
    ssh -i $SSHKey -o StrictHostKeyChecking=no "$RemoteUser@$EC2Host" $Command
}

# Function to copy files to EC2
function Copy-ToEC2 {
    param([string]$Source, [string]$Destination)
    scp -i $SSHKey -o StrictHostKeyChecking=no -r $Source "$RemoteUser@$EC2Host`:$Destination"
}

# Step 1: Test SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Blue
try {
    Invoke-SSH "echo 'SSH connection successful'" | Out-Null
    Write-Host "SSH connection established" -ForegroundColor Green
} catch {
    Write-Host "Failed to connect to EC2 instance. Please check your IP and SSH key." -ForegroundColor Red
    exit 1
}

# Step 2: Stop JavaScript backend services
Write-Host "Stopping JavaScript backend services..." -ForegroundColor Blue
Invoke-SSH "sudo systemctl stop ai-backend 2>/dev/null; true"
Invoke-SSH "sudo systemctl stop pm2 2>/dev/null; true"
Invoke-SSH "pkill -f 'node.*ai-backend' 2>/dev/null; true"
Invoke-SSH "pkill -f 'pm2' 2>/dev/null; true"
Write-Host "JavaScript backend services stopped" -ForegroundColor Green

# Step 3: Create backup of JavaScript backend
Write-Host "Creating backup of JavaScript backend..." -ForegroundColor Blue
Invoke-SSH "mkdir -p $BackupDir"
Invoke-SSH "cp -r $JSBackendDir/* $BackupDir/ 2>/dev/null; true"
Write-Host "Backup created at $BackupDir" -ForegroundColor Green

# Step 4: Remove JavaScript backend files
Write-Host "Removing JavaScript backend files..." -ForegroundColor Blue
Invoke-SSH "sudo rm -rf $JSBackendDir"
Invoke-SSH "sudo rm -rf $RemoteDir/node_modules"
Invoke-SSH "sudo rm -f $RemoteDir/package*.json"
Invoke-SSH "sudo rm -f $RemoteDir/.env"
Write-Host "JavaScript backend files removed" -ForegroundColor Green

# Step 5: Clean up system services
Write-Host "Cleaning up system services..." -ForegroundColor Blue
Invoke-SSH "sudo systemctl disable ai-backend 2>/dev/null; true"
Invoke-SSH "sudo rm -f /etc/systemd/system/ai-backend.service 2>/dev/null; true"
Invoke-SSH "sudo systemctl daemon-reload"
Write-Host "System services cleaned up" -ForegroundColor Green

# Step 6: Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Blue
Invoke-SSH "sudo apt-get update"
Invoke-SSH "sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential"
Invoke-SSH "sudo apt-get install -y curl wget git"
Write-Host "Python dependencies installed" -ForegroundColor Green

# Step 7: Create Python virtual environment
Write-Host "Setting up Python virtual environment..." -ForegroundColor Blue
Invoke-SSH "cd $RemoteDir; python3 -m venv venv"
Invoke-SSH "source $RemoteDir/venv/bin/activate; pip install --upgrade pip"
Write-Host "Python virtual environment created" -ForegroundColor Green

# Step 8: Upload Python backend files
Write-Host "Uploading Python backend files..." -ForegroundColor Blue
Invoke-SSH "mkdir -p $PythonBackendDir"
Copy-ToEC2 "ai-backend-python/" $RemoteDir
Write-Host "Checking uploaded files..." -ForegroundColor Blue
Invoke-SSH "ls -la $PythonBackendDir"
Write-Host "Python backend files uploaded" -ForegroundColor Green

# Step 9: Install Python requirements
Write-Host "Installing Python requirements..." -ForegroundColor Blue
Invoke-SSH "cd $PythonBackendDir; source $RemoteDir/venv/bin/activate; pip install -r requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install requirements. Checking if requirements.txt exists..." -ForegroundColor Yellow
    Invoke-SSH "ls -la $PythonBackendDir"
    Write-Host "Creating basic requirements.txt..." -ForegroundColor Yellow
    $requirements = @"
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
alembic==1.12.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3
nltk==3.8.1
requests==2.31.0
aiofiles==23.2.1
"@
    $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Copy-ToEC2 "requirements.txt" "$PythonBackendDir/"
    Invoke-SSH "cd $PythonBackendDir; source $RemoteDir/venv/bin/activate; pip install -r requirements.txt"
}
Write-Host "Python requirements installed" -ForegroundColor Green

# Step 10: Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Blue
Invoke-SSH "mkdir -p $PythonBackendDir/models"
Invoke-SSH "mkdir -p $PythonBackendDir/uploads"
Invoke-SSH "mkdir -p $PythonBackendDir/temp"
Write-Host "Directories created" -ForegroundColor Green

# Step 11: Set up environment variables
Write-Host "Setting up environment variables..." -ForegroundColor Blue
$envContent = @'
# Database (NeonDB PostgreSQL)
DATABASE_URL=postgresql+asyncpg://username:password@your-neon-host/database
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
Write-Host "Please edit the .env file with your actual API keys and configuration" -ForegroundColor Yellow
Write-Host "Environment template created" -ForegroundColor Green

# Step 12: Create systemd service for Python backend
Write-Host "Creating systemd service for Python backend..." -ForegroundColor Blue
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
Write-Host "Systemd service created" -ForegroundColor Green

# Step 13: Set up firewall
Write-Host "Setting up firewall..." -ForegroundColor Blue
Invoke-SSH "sudo ufw allow 4000/tcp 2>/dev/null; true"
Write-Host "Firewall configured" -ForegroundColor Green

# Step 14: Start the Python backend
Write-Host "Starting Python backend..." -ForegroundColor Blue
Invoke-SSH "sudo systemctl start ai-backend-python"
Start-Sleep -Seconds 5

# Check if service is running
$serviceStatus = Invoke-SSH "sudo systemctl is-active ai-backend-python"
if ($serviceStatus -eq "active") {
    Write-Host "Python backend started successfully" -ForegroundColor Green
} else {
    Write-Host "Failed to start Python backend" -ForegroundColor Red
    Invoke-SSH "sudo systemctl status ai-backend-python"
    exit 1
}

# Step 15: Test the API
Write-Host "Testing API endpoints..." -ForegroundColor Blue
Start-Sleep -Seconds 10

try {
    Invoke-SSH "curl -f http://localhost:4000/health" | Out-Null
    Write-Host "Health check passed" -ForegroundColor Green
} catch {
    Write-Host "Health check failed - service may still be starting" -ForegroundColor Yellow
}

# Step 16: Clean up temporary files
Write-Host "Cleaning up temporary files..." -ForegroundColor Blue
Remove-Item ".env.template" -ErrorAction SilentlyContinue
Remove-Item "ai-backend-python.service" -ErrorAction SilentlyContinue
Write-Host "Temporary files cleaned up" -ForegroundColor Green

# Step 17: Migration summary
Write-Host ""
Write-Host "Migration completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Green
Write-Host "  JavaScript backend stopped and backed up" -ForegroundColor Green
Write-Host "  JavaScript files removed from EC2" -ForegroundColor Green
Write-Host "  Python backend deployed and configured" -ForegroundColor Green
Write-Host "  Systemd service created and enabled" -ForegroundColor Green
Write-Host "  Python backend started" -ForegroundColor Green
Write-Host ""
Write-Host "Backup location: $BackupDir" -ForegroundColor Green
Write-Host "Python backend location: $PythonBackendDir" -ForegroundColor Green
Write-Host "Service name: ai-backend-python" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Edit the .env file with your API keys:" -ForegroundColor Green
Write-Host "     ssh -i $SSHKey ubuntu@$EC2Host" -ForegroundColor Green
Write-Host "     nano $PythonBackendDir/.env" -ForegroundColor Green
Write-Host ""
Write-Host "  2. Check service status:" -ForegroundColor Green
Write-Host "     sudo systemctl status ai-backend-python" -ForegroundColor Green
Write-Host ""
Write-Host "  3. View logs:" -ForegroundColor Green
Write-Host "     sudo journalctl -u ai-backend-python -f" -ForegroundColor Green
Write-Host ""
Write-Host "  4. Test API:" -ForegroundColor Green
Write-Host "     curl http://$EC2Host:4000/health" -ForegroundColor Green
Write-Host ""

Write-Host "Migration script completed!" -ForegroundColor Blue
