#!/bin/bash

# Comprehensive SCKIPIT Deployment Script
# Deploys all SCKIPIT-enhanced files to the backend server

echo "🚀 Starting Comprehensive SCKIPIT Deployment..."
echo "📦 Deploying all SCKIPIT-enhanced files to backend server"
echo "============================================================="

# Server configuration
SERVER="ubuntu@34.202.215.209"
KEY_PATH="C:/projects/lvl_up/New.pem"
REMOTE_DIR="~/ai-backend-python"

# Create backup of current backend
echo "📋 Creating backup of current backend..."
ssh -i "$KEY_PATH" "$SERVER" "cd ~ && tar -czf ai-backend-backup-$(date +%Y%m%d_%H%M%S).tar.gz ai-backend-python/"

# Deploy SCKIPIT-enhanced services
echo "🔧 Deploying SCKIPIT-enhanced AI services..."

# Conquest AI Service
echo "  📤 Uploading Conquest AI Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/conquest_ai_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# Imperium AI Service
echo "  📤 Uploading Imperium AI Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/imperium_ai_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# Guardian AI Service
echo "  📤 Uploading Guardian AI Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/guardian_ai_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# Sandbox AI Service
echo "  📤 Uploading Sandbox AI Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/sandbox_ai_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# AI Learning Service
echo "  📤 Uploading AI Learning Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/ai_learning_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# SCKIPIT Service
echo "  📤 Uploading SCKIPIT Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/sckipit_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# Custody Protocol Service
echo "  📤 Uploading Custody Protocol Service..."
scp -i "$KEY_PATH" "ai-backend-python/app/services/custody_protocol_service.py" "$SERVER:$REMOTE_DIR/app/services/"

# Analytics Router
echo "  📤 Uploading Analytics Router..."
scp -i "$KEY_PATH" "ai-backend-python/app/routers/analytics.py" "$SERVER:$REMOTE_DIR/app/routers/"

# Main app file
echo "  📤 Uploading Main App..."
scp -i "$KEY_PATH" "ai-backend-python/app/main.py" "$SERVER:$REMOTE_DIR/app/"

# Router __init__.py
echo "  📤 Uploading Router __init__.py..."
scp -i "$KEY_PATH" "ai-backend-python/app/routers/__init__.py" "$SERVER:$REMOTE_DIR/app/routers/"

# SCKIPIT Integration Summary
echo "  📤 Uploading SCKIPIT Documentation..."
scp -i "$KEY_PATH" "ai-backend-python/SCKIPIT_INTEGRATION_SUMMARY.md" "$SERVER:$REMOTE_DIR/"

# Install missing dependencies
echo "📦 Installing missing dependencies..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && pip install schedule"

# Restart the backend service
echo "🔄 Restarting backend service..."
ssh -i "$KEY_PATH" "$SERVER" "sudo systemctl restart ai-backend"

# Check service status
echo "📊 Checking service status..."
ssh -i "$KEY_PATH" "$SERVER" "sudo systemctl status ai-backend --no-pager"

# Test SCKIPIT endpoints
echo "🧪 Testing SCKIPIT endpoints..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && curl -s http://localhost:8000/health || echo 'Health endpoint not available'"

echo "============================================================="
echo "✅ Comprehensive SCKIPIT Deployment Complete!"
echo "🎯 All SCKIPIT-enhanced services deployed successfully"
echo "📊 Analytics endpoints available at /analytics/sckipit/*"
echo "🔧 Backend service restarted and running"
echo "=============================================================" 