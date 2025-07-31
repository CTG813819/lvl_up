#!/bin/bash

# Deploy comprehensive fixes to EC2 instance
# Fixes XP display issue and integrates diverse test generation

echo "🚀 Deploying comprehensive fixes to EC2..."

# EC2 instance details
EC2_HOST="ec2-54-147-131-199.compute-1.amazonaws.com"
EC2_USER="ubuntu"
KEY_FILE="lvl_up_key.pem"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ SSH key file not found: $KEY_FILE"
    echo "📝 Please ensure the SSH key is in the current directory"
    exit 1
fi

echo "📦 Transferring files to EC2..."

# Transfer the fixed files
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no \
    diverse_test_generator.py \
    improved_scoring_system.py \
    app/services/custody_protocol_service.py \
    "$EC2_USER@$EC2_HOST:/home/ubuntu/ai-backend-python/"

if [ $? -eq 0 ]; then
    echo "✅ Files transferred successfully"
else
    echo "❌ File transfer failed"
    exit 1
fi

echo "🔧 Restarting backend service..."

# Restart the backend service
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    echo "🛑 Stopping backend service..."
    sudo systemctl stop ai-backend-python
    
    echo "⏳ Waiting for service to stop..."
    sleep 5
    
    echo "🚀 Starting backend service..."
    sudo systemctl start ai-backend-python
    
    echo "⏳ Waiting for service to start..."
    sleep 10
    
    echo "📊 Checking service status..."
    sudo systemctl status ai-backend-python --no-pager
    
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 20 --no-pager
EOF

if [ $? -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo "📝 Monitoring deployment..."
    
    # Monitor logs for a few seconds
    echo "📊 Monitoring recent logs..."
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        echo "📋 Latest logs (last 30 seconds):"
        sudo journalctl -u ai-backend-python --since "30 seconds ago" --no-pager
        
        echo "🔍 Checking for diverse test generation..."
        sudo journalctl -u ai-backend-python --no-pager | grep -i "diverse" | tail -5
        
        echo "🔍 Checking for XP display fixes..."
        sudo journalctl -u ai-backend-python --no-pager | grep -i "XP" | tail -5
EOF
    
    echo "🎉 Deployment and monitoring completed!"
    echo "📝 Next steps:"
    echo "   1. Monitor logs for diverse test generation"
    echo "   2. Verify XP display is correct"
    echo "   3. Check for varied test scores (not 40.01)"
else
    echo "❌ Deployment failed!"
    echo "📝 Please check the error messages above"
fi 