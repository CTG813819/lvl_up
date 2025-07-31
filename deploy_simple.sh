#!/bin/bash

echo "Deploying AI Services Fix to EC2..."

# Server details
SERVER="ubuntu@34.202.215.209"
KEY_PATH="C:/projects/lvl_up/New.pem"
REMOTE_DIR="~/ai-backend-python"

# Upload service files
echo "Uploading service files..."
scp -i "$KEY_PATH" imperium-ai.service "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" sandbox-ai.service "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" custodes-ai.service "$SERVER:$REMOTE_DIR/"
scp -i "$KEY_PATH" guardian-ai.service "$SERVER:$REMOTE_DIR/"

# Upload deployment script
echo "Uploading deployment script..."
scp -i "$KEY_PATH" deploy_comprehensive_fix.sh "$SERVER:$REMOTE_DIR/"

# Execute deployment on server
echo "Executing deployment on server..."
ssh -i "$KEY_PATH" "$SERVER" "cd $REMOTE_DIR && chmod +x deploy_comprehensive_fix.sh && ./deploy_comprehensive_fix.sh"

echo "Deployment completed!" 