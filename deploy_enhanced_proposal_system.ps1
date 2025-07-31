# Enhanced Proposal System Deployment Script (PowerShell)
# Deploys all enhanced proposal system files to EC2 instance

$EC2_HOST = "34.202.215.209"
$PEM_FILE = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "~/ai-backend-python"

Write-Host "🚀 Deploying Enhanced Proposal System to EC2..." -ForegroundColor Green

# Create a temporary directory for the files
$TEMP_DIR = ".\temp_deploy"
if (Test-Path $TEMP_DIR) {
    Remove-Item $TEMP_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copy all the enhanced proposal system files
Write-Host "📁 Copying enhanced proposal system files..." -ForegroundColor Yellow

# Backend files
Copy-Item "ai-backend-python\app\models\proposal.py" $TEMP_DIR\
Copy-Item "ai-backend-python\app\models\sql_models.py" $TEMP_DIR\
Copy-Item "ai-backend-python\app\services\enhanced_proposal_description_service.py" $TEMP_DIR\
Copy-Item "ai-backend-python\app\routers\proposals.py" $TEMP_DIR\
Copy-Item "ai-backend-python\add_enhanced_proposal_fields_migration.py" $TEMP_DIR\

# Frontend files
New-Item -ItemType Directory -Path "$TEMP_DIR\lib\models" -Force | Out-Null
New-Item -ItemType Directory -Path "$TEMP_DIR\lib\screens" -Force | Out-Null
Copy-Item "lib\models\ai_proposal.dart" "$TEMP_DIR\lib\models\"
Copy-Item "lib\screens\proposal_approval_screen.dart" "$TEMP_DIR\lib\screens\"

# Documentation
Copy-Item "ENHANCED_PROPOSAL_SYSTEM_SUMMARY.md" $TEMP_DIR\

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "enhanced_proposal_system_$timestamp.tar.gz"

# Use tar command if available (Git Bash, WSL, or Windows 10+)
try {
    tar -czf $packageName -C $TEMP_DIR .
    Write-Host "✅ Package created: $packageName" -ForegroundColor Green
} catch {
    Write-Host "❌ tar command not available. Please install Git Bash or WSL." -ForegroundColor Red
    Write-Host "Alternatively, you can manually copy the files from $TEMP_DIR" -ForegroundColor Yellow
    exit 1
}

# Deploy to EC2
Write-Host "☁️ Deploying to EC2 instance..." -ForegroundColor Yellow
scp -i $PEM_FILE $packageName "ubuntu@${EC2_HOST}:~/"

# Extract and install on EC2
Write-Host "🔧 Installing on EC2..." -ForegroundColor Yellow
$sshCommand = @"
    cd ~/ai-backend-python
    
    # Backup existing files
    echo "💾 Backing up existing files..."
    mkdir -p backup_\$(date +%Y%m%d_%H%M%S)
    cp app/models/proposal.py backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    cp app/models/sql_models.py backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    cp app/routers/proposals.py backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    
    # Extract new files
    echo "📂 Extracting new files..."
    tar -xzf ~/$packageName
    
    # Install missing dependencies
    echo "📦 Installing missing dependencies..."
    pip install schedule
    
    # Run database migration
    echo "🗄️ Running database migration..."
    python add_enhanced_proposal_fields_migration.py
    
    # Restart the application
    echo "🔄 Restarting application..."
    sudo systemctl restart ai-backend-python || true
    
    # Clean up
    rm ~/$packageName
    
    echo "✅ Enhanced proposal system deployment completed!"
"@

ssh -i $PEM_FILE "ubuntu@${EC2_HOST}" $sshCommand

# Clean up local files
Write-Host "🧹 Cleaning up local files..." -ForegroundColor Yellow
Remove-Item $TEMP_DIR -Recurse -Force
Remove-Item $packageName -Force

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "📋 Summary of deployed files:" -ForegroundColor Cyan
Write-Host "   - Enhanced proposal models (proposal.py, sql_models.py)" -ForegroundColor White
Write-Host "   - Enhanced proposal description service" -ForegroundColor White
Write-Host "   - Updated proposals router with response functionality" -ForegroundColor White
Write-Host "   - Database migration script" -ForegroundColor White
Write-Host "   - Enhanced frontend models and screens" -ForegroundColor White
Write-Host "   - Documentation" -ForegroundColor White
Write-Host ""
Write-Host "🔗 EC2 Instance: $EC2_HOST" -ForegroundColor Cyan
Write-Host "📁 Remote Directory: $REMOTE_DIR" -ForegroundColor Cyan 