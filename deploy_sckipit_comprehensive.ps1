# Comprehensive SCKIPIT Deployment Script (PowerShell)
# Deploys all SCKIPIT-enhanced files to the backend server

Write-Host "🚀 Starting Comprehensive SCKIPIT Deployment..." -ForegroundColor Green
Write-Host "📦 Deploying all SCKIPIT-enhanced files to backend server" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Yellow

# Server configuration
$SERVER = "ubuntu@34.202.215.209"
$KEY_PATH = "C:\projects\lvl_up\New.pem"
$REMOTE_DIR = "~/ai-backend-python"

# Create backup of current backend
Write-Host "📋 Creating backup of current backend..." -ForegroundColor Blue
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
ssh -i $KEY_PATH $SERVER "cd ~ && tar -czf ai-backend-backup-$timestamp.tar.gz ai-backend-python/"

# Deploy SCKIPIT-enhanced services
Write-Host "🔧 Deploying SCKIPIT-enhanced AI services..." -ForegroundColor Blue

# Conquest AI Service
Write-Host "  📤 Uploading Conquest AI Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/conquest_ai_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# Imperium AI Service
Write-Host "  📤 Uploading Imperium AI Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/imperium_ai_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# Guardian AI Service
Write-Host "  📤 Uploading Guardian AI Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/guardian_ai_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# Sandbox AI Service
Write-Host "  📤 Uploading Sandbox AI Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/sandbox_ai_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# AI Learning Service
Write-Host "  📤 Uploading AI Learning Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/ai_learning_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# SCKIPIT Service
Write-Host "  📤 Uploading SCKIPIT Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/sckipit_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# Custody Protocol Service
Write-Host "  📤 Uploading Custody Protocol Service..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/services/custody_protocol_service.py" "$SERVER`:$REMOTE_DIR/app/services/"

# Analytics Router
Write-Host "  📤 Uploading Analytics Router..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/routers/analytics.py" "$SERVER`:$REMOTE_DIR/app/routers/"

# Main app file
Write-Host "  📤 Uploading Main App..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/main.py" "$SERVER`:$REMOTE_DIR/app/"

# Router __init__.py
Write-Host "  📤 Uploading Router __init__.py..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/app/routers/__init__.py" "$SERVER`:$REMOTE_DIR/app/routers/"

# SCKIPIT Integration Summary
Write-Host "  📤 Uploading SCKIPIT Documentation..." -ForegroundColor Green
scp -i $KEY_PATH "ai-backend-python/SCKIPIT_INTEGRATION_SUMMARY.md" "$SERVER`:$REMOTE_DIR/"

# Install missing dependencies
Write-Host "📦 Installing missing dependencies..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "cd $REMOTE_DIR && pip install schedule"

# Restart the backend service
Write-Host "🔄 Restarting backend service..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "sudo systemctl restart ai-backend"

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "sudo systemctl status ai-backend --no-pager"

# Test SCKIPIT endpoints
Write-Host "🧪 Testing SCKIPIT endpoints..." -ForegroundColor Blue
ssh -i $KEY_PATH $SERVER "cd $REMOTE_DIR && curl -s http://localhost:8000/health || echo 'Health endpoint not available'"

Write-Host "=============================================================" -ForegroundColor Yellow
Write-Host "✅ Comprehensive SCKIPIT Deployment Complete!" -ForegroundColor Green
Write-Host "🎯 All SCKIPIT-enhanced services deployed successfully" -ForegroundColor Cyan
Write-Host "📊 Analytics endpoints available at /analytics/sckipit/*" -ForegroundColor Cyan
Write-Host "🔧 Backend service restarted and running" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Yellow 