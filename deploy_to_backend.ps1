# Deploy updated files to backend server
# This script copies all the updated files to the backend server

Write-Host "🚀 Deploying updated files to backend server..." -ForegroundColor Green

# Server details
$SERVER_IP = "34.202.215.209"
$SERVER_USER = "ubuntu"
$PEM_FILE = "New.pem"
$BACKEND_PATH = "~/ai-backend-python"

# Files to copy
$FILES = @(
    "ai-backend-python/app/services/custody_protocol_service.py",
    "ai-backend-python/app/services/imperium_extension_service.py",
    "ai-backend-python/app/routers/imperium_extensions.py",
    "ai-backend-python/app/main.py",
    "lib/screens/custody_protocol_screen.dart",
    "lib/widgets/ai_growth_analytics_dashboard.dart",
    "lib/screens/black_library_screen.dart",
    "lib/side_menu.dart",
    "ai-backend-python/run_enhanced_autonomous_learning.py",
    "CUSTODY_PROTOCOL_SYSTEM.md"
)

# Create directories on server if they don't exist
Write-Host "📁 Creating directories on server..." -ForegroundColor Yellow
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/app/services"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/app/routers"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/lib/screens"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/lib/widgets"

# Copy files to server
Write-Host "📤 Copying files to server..." -ForegroundColor Yellow
foreach ($file in $FILES) {
    if (Test-Path $file) {
        Write-Host "Copying $file..." -ForegroundColor Cyan
        $remoteDir = Split-Path $file -Parent
        scp -i "$PEM_FILE" "$file" "$SERVER_USER@$SERVER_IP`:$BACKEND_PATH/$remoteDir/"
    } else {
        Write-Host "⚠️  Warning: File $file not found" -ForegroundColor Yellow
    }
}

# Install required Python packages
Write-Host "📦 Installing required Python packages..." -ForegroundColor Yellow
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH; pip install schedule"

# Restart the backend service
Write-Host "🔄 Restarting backend service..." -ForegroundColor Yellow
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH; pkill -f 'python.*main.py' 2>/dev/null || true"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH; nohup python main.py > backend.log 2>&1 &"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📊 Backend service restarted" -ForegroundColor Green
Write-Host "🔗 API endpoints available at: http://$SERVER_IP:8000" -ForegroundColor Green
Write-Host "📋 New endpoints:" -ForegroundColor Cyan
Write-Host "   - /api/imperium-extensions/* (Imperium Extension management)" -ForegroundColor White
Write-Host "   - /api/custody/* (Custody Protocol - updated pass rates)" -ForegroundColor White
Write-Host "🎮 Frontend updates:" -ForegroundColor Cyan
Write-Host "   - Custody Protocol button changed to weapon icon" -ForegroundColor White
Write-Host "   - Black Library skill tree screen added" -ForegroundColor White
Write-Host "   - Side menu updated with Black Library access" -ForegroundColor White 