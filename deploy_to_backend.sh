#!/bin/bash

# Deploy updated files to backend server
# This script copies all the updated files to the backend server

echo "🚀 Deploying updated files to backend server..."

# Server details
SERVER_IP="34.202.215.209"
SERVER_USER="ubuntu"
PEM_FILE="New.pem"
BACKEND_PATH="~/ai-backend-python"

# Files to copy
FILES=(
    "ai-backend-python/app/services/custody_protocol_service.py"
    "ai-backend-python/app/services/imperium_extension_service.py"
    "ai-backend-python/app/routers/imperium_extensions.py"
    "ai-backend-python/app/main.py"
    "lib/screens/custody_protocol_screen.dart"
    "lib/widgets/ai_growth_analytics_dashboard.dart"
    "lib/side_menu.dart"
    "ai-backend-python/run_enhanced_autonomous_learning.py"
    "CUSTODY_PROTOCOL_SYSTEM.md"
)

# Create directories on server if they don't exist
echo "📁 Creating directories on server..."
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/app/services"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/app/routers"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/lib/screens"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "mkdir -p $BACKEND_PATH/lib/widgets"

# Copy files to server
echo "📤 Copying files to server..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Copying $file..."
        scp -i "$PEM_FILE" "$file" "$SERVER_USER@$SERVER_IP:$BACKEND_PATH/$(dirname "$file")/"
    else
        echo "⚠️  Warning: File $file not found"
    fi
done

# Install required Python packages
echo "📦 Installing required Python packages..."
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH && pip install schedule"

# Restart the backend service
echo "🔄 Restarting backend service..."
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH && pkill -f 'python.*main.py' || true"
ssh -i "$PEM_FILE" "$SERVER_USER@$SERVER_IP" "cd $BACKEND_PATH && nohup python main.py > backend.log 2>&1 &"

echo "✅ Deployment complete!"
echo "📊 Backend service restarted"
echo "🔗 API endpoints available at: http://$SERVER_IP:8000"
echo "📋 New endpoints:"
echo "   - /api/imperium-extensions/* (Imperium Extension management)"
echo "   - /api/custody/* (Custody Protocol - updated pass rates)"
echo "🎮 Frontend updates:"
echo "   - Custody Protocol button changed to weapon icon"
echo "   - Side menu updated with Black Library access" 