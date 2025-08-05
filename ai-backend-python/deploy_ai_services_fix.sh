#!/bin/bash

# Deploy AI Services Fix to Backend
# This script fixes all AI services and ensures they work properly

echo "🚀 Deploying AI Services Fix to Backend..."
echo "=========================================="

# Server configuration
SERVER="ubuntu@34.202.215.209"
KEY_PATH="C:/projects/lvl_up/New.pem"
REMOTE_DIR="~/ai-backend-python"

# Create backup of current backend
echo "📋 Creating backup of current backend..."
ssh -i "$KEY_PATH" "$SERVER" "cd ~ && tar -czf ai-backend-backup-$(date +%Y%m%d_%H%M%S).tar.gz ai-backend-python/"

# Upload the comprehensive fix script
echo "📤 Uploading comprehensive fix script..."
scp -i "$KEY_PATH" "fix_ai_services_comprehensive.py" "$SERVER:$REMOTE_DIR/"

# Run the comprehensive fix on the server
echo "🔧 Running comprehensive AI services fix..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && python3 fix_ai_services_comprehensive.py"

# Upload the generated service files and scripts
echo "📤 Uploading generated service files..."
scp -i "$KEY_PATH" "imperium-ai.service" "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" "sandbox-ai.service" "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" "custodes-ai.service" "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" "guardian-ai.service" "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" "deploy_comprehensive_fix.sh" "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" "monitor_ai_services.sh" "$SERVER:$REMOTE_DIR/"

# Execute the deployment script on the server
echo "🚀 Executing deployment script on server..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && chmod +x deploy_comprehensive_fix.sh && ./deploy_comprehensive_fix.sh"

# Check the status of all services
echo "📊 Checking service status..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && chmod +x monitor_ai_services.sh && ./monitor_ai_services.sh"

echo ""
echo "✅ AI Services Fix deployment completed!"
echo ""
echo "📋 Summary of fixes applied:"
echo "• Fixed Guardian sudo handling with fallback"
echo "• Added proper Python paths and virtual environment usage"
echo "• Enhanced error handling and logging"
echo "• Added service dependencies and startup order"
echo "• Implemented resource monitoring and health checks"
echo ""
echo "🔍 Monitor services with:"
echo "ssh -i $KEY_PATH $SERVER 'cd $REMOTE_DIR && ./monitor_ai_services.sh'"
echo ""
echo "📝 View individual service logs:"
echo "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u imperium-ai.service -f'"
echo "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u sandbox-ai.service -f'"
echo "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u custodes-ai.service -f'"
echo "ssh -i $KEY_PATH $SERVER 'sudo journalctl -u guardian-ai.service -f'" 