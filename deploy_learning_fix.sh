#!/bin/bash

# Deploy Learning Model Fix to EC2
# This script deploys the fix for the 'context' keyword argument error in the Learning model

echo "🚀 Deploying Learning Model Fix to EC2..."

# Configuration
PEM_FILE="C:/projects/lvl_up/New.pem"
EC2_HOST="ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

# Convert Windows path to Unix path for scp
PEM_FILE_UNIX=$(echo "$PEM_FILE" | sed 's/\\/\//g' | sed 's/C:/\/c/g')

echo "📁 Deploying from: $PEM_FILE_UNIX"
echo "🌐 Deploying to: $EC2_HOST:$REMOTE_DIR"

# Create a backup of the current ai_learning_service.py on the server
echo "💾 Creating backup of current ai_learning_service.py..."
ssh -i "$PEM_FILE_UNIX" "$EC2_HOST" "cp $REMOTE_DIR/app/services/ai_learning_service.py $REMOTE_DIR/app/services/ai_learning_service.py.backup.$(date +%Y%m%d_%H%M%S)"

# Deploy the fixed ai_learning_service.py
echo "📤 Deploying fixed ai_learning_service.py..."
scp -i "$PEM_FILE_UNIX" "ai-backend-python/app/services/ai_learning_service.py" "$EC2_HOST:$REMOTE_DIR/app/services/"

# Deploy the test script
echo "📤 Deploying test script..."
scp -i "$PEM_FILE_UNIX" "ai-backend-python/test_learning_fix.py" "$EC2_HOST:$REMOTE_DIR/"

# Test the fix on the server
echo "🧪 Testing the fix on the server..."
ssh -i "$PEM_FILE_UNIX" "$EC2_HOST" "cd $REMOTE_DIR && python test_learning_fix.py"

# Restart the application if it's running
echo "🔄 Restarting the application..."
ssh -i "$PEM_FILE_UNIX" "$EC2_HOST" "cd $REMOTE_DIR && sudo systemctl restart lvl_up_backend || echo 'Service not found, manual restart may be needed'"

echo "✅ Deployment completed!"
echo "📋 Check the logs to verify the fix is working:"
echo "   ssh -i \"$PEM_FILE_UNIX\" \"$EC2_HOST\" \"cd $REMOTE_DIR && tail -f logs/app.log\"" 