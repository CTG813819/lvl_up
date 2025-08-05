#!/bin/bash

# Deployment script to transfer fixed files to EC2 instance
# This script will transfer the files that have been fixed locally to the EC2 instance

echo "🚀 Starting deployment to EC2 instance..."

# Set variables
EC2_HOST="ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
KEY_FILE="C:\projects\lvl_up\New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

# Files that need to be transferred (the ones we fixed)
FILES_TO_TRANSFER=(
    "app/main.py"
    "app/services/custody_protocol_service.py"
    "create_tables.py"
)

echo "📁 Transferring fixed files to EC2..."

# Transfer each file
for file in "${FILES_TO_TRANSFER[@]}"; do
    if [ -f "$file" ]; then
        echo "📤 Transferring $file..."
        scp -i "$KEY_FILE" "$file" "$EC2_HOST:$REMOTE_DIR/$file"
        if [ $? -eq 0 ]; then
            echo "✅ Successfully transferred $file"
        else
            echo "❌ Failed to transfer $file"
            exit 1
        fi
    else
        echo "⚠️ File $file not found, skipping..."
    fi
done

echo "🔧 Running database setup on EC2..."
ssh -i "$KEY_FILE" "$EC2_HOST" "cd $REMOTE_DIR && python3 create_tables.py"

echo "🔄 Restarting the backend service on EC2..."
ssh -i "$KEY_FILE" "$EC2_HOST" "sudo systemctl restart ultimate_start"

echo "⏳ Waiting for service to start..."
sleep 10

echo "📊 Checking service status..."
ssh -i "$KEY_FILE" "$EC2_HOST" "sudo systemctl status ultimate_start"

echo "✅ Deployment completed!"
echo ""
echo "🔍 To check the logs, run:"
echo "ssh -i \"$KEY_FILE\" \"$EC2_HOST\" \"sudo journalctl -u ultimate_start -f\"" 